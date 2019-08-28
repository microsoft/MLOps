import numpy as np
import argparse
import os

import torch
from torch.utils.data import TensorDataset,DataLoader

from trainer import SvDklTrainer
from azureml.core import Run

parser = argparse.ArgumentParser()
parser.add_argument('--data-folder', type=str, dest='data_folder', help='data folder mounting point')
parser.add_argument('--batch-size', type=int, dest='batch_size', default=512, help='mini batch size for training')
parser.add_argument('--epochs', type=int, dest='epochs', default=100, help='number of epochs')
parser.add_argument('--neural-net-lr', type=float, dest='nn_lr', default=1e-2,help='Neural net learning rate')
parser.add_argument('--likelihood-lr', type=float, dest='lh_lr', default=1e-2,help='Likelihood learning rate')
parser.add_argument('--grid-size', type=int, dest='grid_size', default=64, help='grid size of each dimension')
parser.add_argument('--grid-bounds', type=tuple, dest='grid_bounds', default=(-1,1), help='bound of the grid')
parser.add_argument('--latent-dim', type=int, dest='latent_dim', default=2, help='dimensionality of latent space')
parser.add_argument('--num-mixtures', type=int, dest='num_mixtures', default=4, help='number of mixture components')
args = parser.parse_args()

data_folder = args.data_folder
print('data folder', data_folder)


X_train,y_train = torch.FloatTensor(np.load(os.path.join(data_folder,'X_train.npy'))), torch.FloatTensor(np.load(os.path.join(data_folder,'y_train.npy')))
X_test,y_test = torch.FloatTensor(np.load(os.path.join(data_folder,'X_test.npy'))), torch.FloatTensor(np.load(os.path.join(data_folder,'y_test.npy')))

print('Training set loaded',X_train.size(),y_train.size())
print('Test set loaded',X_test.size(),y_test.size())

grid_bounds = (-1,1) if args.grid_bounds == -1 else (0,1)
hyper_params = {'nn_lr':args.nn_lr,
               'lh_lr':args.lh_lr,
               'batch_size':args.batch_size,
               'epochs':args.epochs,
               'grid_size':args.grid_size,
               'grid_bounds':grid_bounds,
               'latent_dim':args.latent_dim,
               'input_dim':X_train.size(1),
               'num_mixtures':args.num_mixtures
              }


train_dataloader = DataLoader(TensorDataset(X_train,y_train), 
                              batch_size = hyper_params['batch_size'],
                              shuffle = True)
test_dataloader = DataLoader(TensorDataset(X_test,y_test), 
                              batch_size = hyper_params['batch_size'],
                              shuffle = True)
# start training

SEED = 123
torch.manual_seed(SEED)
torch.backends.cudnn.deterministic = True

run = Run.get_context()

trainer = SvDklTrainer(hyper_params, aml_run=run)
trainer.fit(train_dataloader)
trainer.eval(test_dataloader)

