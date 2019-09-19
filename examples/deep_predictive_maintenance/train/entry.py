

import os
import numpy as np
import pandas as pd

import torch

from utils import to_tensors
from train import train

from sklearn.model_selection import train_test_split
from azureml.core import Run

if __name__ == '__main__':
    
    
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--epochs', type=int, default=2,
                        help='number of epochs to train')
    parser.add_argument('--learning_rate', type=float,
                        default=1e-3, help='learning rate')
    parser.add_argument('--l2', type=float, 
                        help='Weight decay')
    parser.add_argument('--dropout', type=float,
                        default=.2, help='drop out')
    parser.add_argument('--hidden_units', type=int,
                        default=16, help='number of neurons')
    parser.add_argument('--batch_size', type=int,
                        default=16, help='Mini batch size')
    parser.add_argument('--data_path', type=str, 
                        help='path to training-set file')
    parser.add_argument('--output_dir', type=str, 
                        help='output directory')
    
    args = parser.parse_args()
    nb_epochs = args.epochs
    learning_rate = args.learning_rate
    weight_decay = args.l2
    dropout = args.dropout
    data_path = args.data_path
    output_dir = args.output_dir
    batch_size = args.batch_size
    hidden_size = args.hidden_units
    batch_size = args.batch_size
    
    SEED = 123
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    
    
    print('Pytorch version', torch.__version__)
    
    run = Run.get_context()
    
    os.makedirs(data_path, exist_ok = True)
    training_file = os.path.join(data_path, 'preprocessed_train_file.csv')
    
    X, y = to_tensors(training_file)
    X_train, X_test, y_train, y_test = train_test_split(
                             X, y, test_size=0.15, random_state=SEED)
    

    
    network = train( X_train,y_train, 
                    X_test,y_test, weight_decay,
                    learning_rate,batch_size,
                    hidden_size,dropout,
                    nb_epochs, run)
    
    os.makedirs(output_dir, exist_ok = True)
    model_path = os.path.join(output_dir, 'network.pth')
    
    torch.save(network, model_path)
    run.register_model(model_name = 'network.pth', model_path = model_path)