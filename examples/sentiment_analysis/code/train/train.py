import argparse
import numpy as np
import os.path
import shutil
import random

import matplotlib
matplotlib.use("Agg")

import torch
from fastai.text import *
from azureml.core.run import Run
import fastai


if __name__ == "__main__":
    
    print('fastai',fastai.__version__)
    print('pytorch',torch.__version__)
    print('cudnn enabled ',torch.backends.cudnn.enabled)
    
    SEED = 67
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.backends.cudnn.deterministic = True
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(SEED)
   
    
    run = Run.get_context()
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input_dir',type=str, help='path to dataset')
    parser.add_argument('--lm_lr',type=float,help='language model encoder max learning rate')
    parser.add_argument('--clf_lr', type=float,help='classifier max learning rate')
    parser.add_argument('--momentum_1',type=float,dest='mom_1',help='momentum 1')
    parser.add_argument('--momentum_2',type=float,dest='mom_2', help='momentum 2')
    
    input_dir = parser.parse_args().input_dir
    lm_lr = parser.parse_args().lm_lr
    clf_lr = parser.parse_args().clf_lr
    print(input_dir)
    
    #load dataset into databunch
    data_bunch = (TextList
           .from_csv(input_dir, 'reviews.csv', cols='reviewText')
           .split_by_rand_pct()           
           .label_for_lm()
           .databunch())
    
    #momentum dropout, epochs
    moms = (parser.parse_args().mom_1,parser.parse_args().mom_2)
    DROP_OUT = 0.5
    EPOCHS =  10
    
    # Fit language model encoder
    learner = language_model_learner(data_bunch,
                                     arch= AWD_LSTM, 
                                     drop_mult=DROP_OUT
                                    )
    learner.fit_one_cycle(EPOCHS//2,lm_lr)
    learner.save_encoder('encoder')
    
    print('train classifier...')
    data_clf = TextClasDataBunch.from_csv(input_dir, 
                                       'reviews.csv', 
                                       text_cols='reviewText',
                                       label_cols='sentimentScore',
                                       vocab=data_bunch.train_ds.vocab,
                                       num_workers=0,
                                       bs=32)

    learner= text_classifier_learner(data_clf, 
                                     AWD_LSTM,
                                     drop_mult=DROP_OUT
                                    )
    learner.load_encoder('encoder')
    print(learner.summary())
    learner.fit_one_cycle(EPOCHS//2,
                          lm_lr,
                          moms
                         )
    
    
    #Unfreeze all layer groups and retrain...
    learner.unfreeze()
    learner.fit_one_cycle(EPOCHS,
                          slice(clf_lr,lm_lr), 
                          moms
                         )
    
    # save & register model
    model_name = 'classifier.pth'
    output_dir = 'outputs'
    
    os.makedirs(output_dir, exist_ok = True)
    
    learner.export(model_name)
    shutil.copyfile(os.path.join(learner.path,model_name),
                    os.path.join(output_dir, model_name)
                   )

    # Track validation loss and val_accurary to AML run
    val_losses = [round(loss.item(),2) for loss in learner.recorder.losses]
    run.log_list('validation loss',val_losses)
    
    _,acc = learner.validate(learner.data.test_ds)
    run.log('val_accuracy', round(acc.item(),3))

    