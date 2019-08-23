#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

import numpy as np

from azureml.core import Workspace, Dataset, Experiment

from azureml.train.automl import AutoMLConfig


# In[ ]:


ws = Workspace.get('retrainingPMVP', subscription_id='60582a10-b9fd-49f1-a546-c4194134bba8')


# In[ ]:


dstore = ws.get_default_datastore()


# In[ ]:


delta = int(sys.argv[1])


# In[ ]:


dset = ws.datasets['{}'.format(delta)]


# In[ ]:


df   = dset.to_pandas_dataframe()


# In[ ]:


label = 'temperature'

X     = df.drop(columns=[label])
y     = np.array(df[label])


# In[ ]:


primary_metric = 'r2_score'


# In[ ]:


# setup automl
automl_config = AutoMLConfig(task = 'regression',
                             primary_metric = primary_metric,
                             X = X, 
                             y = y,
                             preprocess=True,
                             iterations=1,
                             n_cross_validations=5)

# create experiment
experiment_name = 'MVP7'
exp = Experiment(ws, name=experiment_name)

# submit local automl run
run = exp.submit(automl_config, show_output=True)
run.wait_for_completion();


# In[ ]:


best_run = run.get_output()[0]


# In[ ]:


best_run.get_metrics()[primary_metric]


# In[ ]:


best_run.register_model('MVP7model', model_path='outputs/model.pkl')

