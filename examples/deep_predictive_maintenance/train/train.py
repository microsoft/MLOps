
import numpy as np

import torch
import torch.nn as nn
import torch.utils.data as utils

from network import Network
from sklearn.metrics import (precision_score,recall_score,f1_score)



def train(X_train,y_train, 
          X_val,y_val,weight_decay,
          learning_rate,batch_size,
          hidden_size,dropout,
          nb_epochs, run):

    '''
        Train lstm network 
        
        params:
            X_train: training set
            y_train: training label
            X_test: validation set
            y_test: validation label
            weight_decay: l2 reguralization
            learning_rate: optimizer learning rate
            batch_size: mini batches size
            hidden_size: number of hidden units
            dropout: Dropout
            nb_epochs: number of epocs to train
            run: AML RUN
    '''
    
    print("Start training....")
    print('learning rate', learning_rate)
    print("L2 regularization", weight_decay)
    print('dropout', dropout)
    print('batch_size', batch_size)
    print('hidden_units', hidden_size)
    
    dataset = utils.TensorDataset(torch.from_numpy(X_train),
                                  torch.from_numpy(y_train)) 
    dataloader = utils.DataLoader(dataset, batch_size = batch_size,
                                  shuffle = True)
    
    val_dataset = utils.TensorDataset(torch.from_numpy(X_val),
                                      torch.from_numpy(y_val))
    val_dataloader = utils.DataLoader(val_dataset)
    
    use_gpu = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    input_size = X_train.shape[2] #features dimension
    nb_layers = 2 # lstm layers
    
    network = Network(batch_size, 
                      input_size,hidden_size,
                      nb_layers,dropout).to(use_gpu)
    

    cost_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate,
                                weight_decay=weight_decay)
    
    # Train the model
    for epoch in range(nb_epochs):
        for i, (X, y) in enumerate(dataloader):
            optimizer.zero_grad()
            y_pred, _ = network(X.to(use_gpu))
            loss = cost_fn(y_pred, y.to(use_gpu))
            loss.backward()
            optimizer.step()
            if (i+1) % 100 == 0:
                run.log('loss', loss.item())
                
        # end of epoch evaluate      
        evaluate(val_dataloader, network, use_gpu, run)
        network.train()

    return network

def evaluate(dataloader, network, use_gpu, run):
    
    '''
        Evaluate model on validation set
        
        params:
            dataloader: dataloader
            network: model
            use_gpu: device
            run: AML RUN
    '''
    
    
    
    y_pred_lst = []
    y_truth_lst = []
    with torch.no_grad():
        for i, (X, y) in enumerate(dataloader):
            
                #X = X.to(use_gpu)
                output, _ = network(X.to(use_gpu))
                y_pred = output.to('cpu').data.numpy().argmax(axis=1)
                
                y_pred_lst.append(y_pred)
                y_truth_lst.append(y.data.numpy())
                
                
        y_pred_np = np.array(y_pred_lst)
        y_truth_np = np.array(y_truth_lst)
        
        precision = precision_score(y_truth_np, y_pred_np)
        recall = recall_score(y_truth_np, y_pred_np)
        f1 = f1_score(y_truth_np, y_pred_np)

        run.log('precision', round(precision,2))
        run.log('recall', round(recall,2))
        run.log('f1', round(f1,2))