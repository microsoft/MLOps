import math
import numpy as np

import torch
import gpytorch
from torch.optim import SGD, Adam
from torch.optim.lr_scheduler import MultiStepLR
from sklearn.metrics import roc_auc_score,accuracy_score

from svdkl import (NeuralNetLayer,
                  GaussianProcessLayer, 
                  DKLModel)
""" 
Trainer class train/eval model
"""
class SvDklTrainer: 
    
    """Train SV_DKL model"""

    def __init__(self, hyper_params, aml_run):
        
        
        """initialize SV-DKL model

         
        Args:
            hyper_params(dict):contains model hyperparameters
            aml_run(run):AzureML run

        """

        self.device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.hyper_params = hyper_params
        print(self.hyper_params)
       # Bernoulli likelood 
        self.likelihood = gpytorch.likelihoods.BernoulliLikelihood().to(self.device)

        nnet_layer = NeuralNetLayer(data_dim=self.hyper_params['input_dim'],
                                         output_dim=self.hyper_params['latent_dim']
                                         ).to(self.device)

        self.model = DKLModel(nnet_layer,
                           num_dim=self.hyper_params['latent_dim'],
                           grid_bounds=self.hyper_params['grid_bounds'],
                           grid_size=self.hyper_params['grid_size'],
                           num_mixtures = self.hyper_params['num_mixtures']
                            ).to(self.device)
        
       # Stochastic variational optimzer 
        self.optimizer=Adam([
            {'params': self.model.nnet_layer.parameters(),'lr':self.hyper_params['nn_lr'], 'betas':(0.9, 0.999)},
            {'params': self.model.gp_layer.hyperparameters(), 'lr': self.hyper_params['lh_lr'] * 0.01},
            {'params':self. model.gp_layer.variational_parameters()},
            {'params': self.likelihood.parameters()}], lr=self.hyper_params['lh_lr'])
        #,momentum=0.9, nesterov=True, weight_decay=0)
        self.aml_run = aml_run

    
    def fit(self, data_loader):



        """Train SV-DKL model


        Args:
            dataloader(pytroch dataloader):data loader wrapping training dataset(X,y)
            
        """
        
        scheduler = MultiStepLR(self.optimizer,
                            gamma=0.1,
                            milestones=[0.5 * self.hyper_params['epochs'], 0.75 * self.hyper_params['epochs']])
        
        for epoch in range(1, self.hyper_params['epochs'] + 1):
            self.model.train()
            self.likelihood.train()

            mll = gpytorch.mlls.VariationalELBO(self.likelihood, 
                                                self.model.gp_layer, 
                                                num_data=len(data_loader.dataset))

            train_loss = 0.
            for i, (data, target) in enumerate(data_loader):
                data, target = data.to(self.device), target.to(self.device)
                self.optimizer.zero_grad()
                output = self.model(data)
                loss = -mll(output, target)
                loss.backward()
                self.optimizer.step()
                if (i+ 1) % 2 == 0:
                    print('Train Epoch: %d [%03d/%03d], Loss: %.6f' % (epoch, i + 1, len(data_loader), loss.item()))
                    
                    if self.aml_run is not None:
                        self.aml_run.log("loss",loss.item()) 

    
    def eval(self, dataloader):

        """Evaluate SV-DKL model on test dataset


        Args:
            dataloader(pytroch dataloader):Data loader wrapping test dataset(X,y)
            

        """


        y_pred_lst = []
        y_truth_lst = []

        with torch.no_grad():
            for i, (X, y) in enumerate(dataloader):
                output = self.likelihood(self.model(X.to(self.device)))
                y_pred = output.mean.ge(0.5).float().cpu().numpy()
                y_pred_lst.append(y_pred)
                y_truth_lst.append(y.numpy())
            
            truth = np.concatenate(y_truth_lst)
            pred =  np.concatenate(y_pred_lst)
        
            auc = roc_auc_score(truth,pred)
            accuracy = accuracy_score(truth,pred)   
        
        print("AUC score: ",round(auc,2))
        print("Accuracy score: ",round(accuracy,2))

        if self.aml_run is not None:
            self.aml_run.log('auc',round(auc,2))
            self.aml_run.log('Accuracy',round(accuracy,2))
