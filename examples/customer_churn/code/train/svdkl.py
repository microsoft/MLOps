import math
import numpy as np
import torch
import gpytorch
from gpytorch.models import AbstractVariationalGP
from gpytorch.variational import (CholeskyVariationalDistribution,
                                VariationalStrategy,
                                 AdditiveGridInterpolationVariationalStrategy)
from gpytorch.mlls.variational_elbo import VariationalELBO
from gpytorch.utils.grid import choose_grid_size


"""
Binary classifier with implementation of Stochastic-variational deep kernel learning
 https://arxiv.org/abs/1611.00336
"""


class NeuralNetLayer(torch.nn.Sequential):
    """Fully connected network: features extractor layer"""
    def __init__(self, data_dim, output_dim):
        

        """Full connected network

         input->200->100->50->2

        """
        super(NeuralNetLayer, self).__init__()
       
        self.add_module('linear1', torch.nn.Linear(data_dim, 200))
        self.add_module('bn1', torch.nn.BatchNorm1d(200))
        self.add_module('relu1', torch.nn.ReLU())
        self.add_module('linear2', torch.nn.Linear(200, 100))
        self.add_module('bn2', torch.nn.BatchNorm1d(100))
        self.add_module('relu2', torch.nn.ReLU())
        self.add_module('linear3', torch.nn.Linear(100, 50))
        self.add_module('bn3', torch.nn.BatchNorm1d(50))
        self.add_module('relu3', torch.nn.ReLU())
        self.add_module('linear4', torch.nn.Linear(50,output_dim))

# GP layer
class GaussianProcessLayer(AbstractVariationalGP):
    """Gaussian Process layer using additive covariance kernel sturcture"""
    def __init__(
        self, 
        num_dim, 
        grid_bounds, 
        grid_size,
        num_mixtures):

        """Initialize Gaussian process layer


        Args:
            num_dim(int): data input dimension
            grid_bound(tuple): bound of the grid, entries,represent min/max values of each dimensionn
                               and represent number of inducing points
            grid_size(int): size of grid in each dimension
            num_mixture(int): number of mixture components

        """
        variational_distribution = CholeskyVariationalDistribution(
                                                 num_inducing_points=grid_size,
                                                 batch_size=num_dim
                                                )
       
        variational_strategy = AdditiveGridInterpolationVariationalStrategy(
                                                         self,
                                                         grid_size=grid_size,
                                                         grid_bounds=[grid_bounds],
                                                         num_dim=num_dim,
                                                         variational_distribution=variational_distribution
                                                        )
        super(GaussianProcessLayer,self).__init__(variational_strategy)
        self.covar_module = gpytorch.kernels.SpectralMixtureKernel(num_mixtures=num_mixtures,
                                                                   ard_dum_dims=num_dim)
        self.mean_module = gpytorch.means.ConstantMean()
        self.grid_bounds = grid_bounds
        

    def forward(self,x):


        """Forward pass"""

        """
        Args:
            x(pytorch tensor): training input 
        """

        mean = self.mean_module(x)
        covar = self.covar_module(x)


        return gpytorch.distributions.MultivariateNormal(mean, covar)       

# SV-DKL model
class DKLModel(gpytorch.Module):
    def __init__(
        self, 
        nnet_layer,
        num_dim, 
        grid_bounds,
        grid_size,
        num_mixtures):


        """SV-DKL model


        Args:
            nnet_layer(pytorch neural net): feature extractor
            num_dim(int): data input dimension
            grid_bound(tuple): bound of the grid, entries,represent min/max values of each dimension
                               and represent number of inducing points
            grid_size(int): size of grid in each dimension
            num_mixture(int): number of mixture components

        """
        super(DKLModel, self).__init__()
        self.nnet_layer = nnet_layer
        self.gp_layer = GaussianProcessLayer(num_dim=num_dim, 
                                             grid_bounds=grid_bounds,
                                             grid_size=grid_size,
                                             num_mixtures=num_mixtures
                                             )
        self.grid_bounds = grid_bounds

    def forward(self,x):

        """Forward pass"""

        """
        Args:
            x(pytorch tensor): training input 
        """

        features = self.nnet_layer(x)
        features = gpytorch.utils.grid.scale_to_bounds(
            features, self.grid_bounds[0], 
            self.grid_bounds[1]
            )
            
        res = self.gp_layer(features)

        return res
