#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pickle

import pandas as pd
import numpy as np

from azureml.core import Workspace, Model

from azureml.train import automl

from sklearn.metrics import r2_score


# In[2]:


ws = Workspace.from_config()


# In[4]:


ws.models


# In[8]:


model    = ws.models['MVP7model']
versions = model.version


# In[9]:


max_versions= 100


# In[14]:


data = [0]*max_versions

for version in range(2, versions):
    # get version of model
    model = Model(ws, name='MVP7model', version=version)
    
    # reset model tags
    model.tags['best_model'] = False
    
    model.download('outputs/{}'.format(version), exist_ok=True)
    
    with open('outputs/{}/model.pkl'.format(version), 'rb') as f:
        m = pickle.load(f)
    
    dset  = ws.datasets['{}'.format(versions-1)]
    
    df    = dset.to_pandas_dataframe()    
    df    = df.fillna(0)
    
    label = 'temperature'

    X     = df.drop(columns=[label])
    
    y     = np.array(df[label])    
    y_p   = m.predict(X)
    
    perf  = r2_score(y, y_p)
    
    data[version] = perf
        
headers = ['v{}'.format(version) for version in range(1, max_versions+1)]  
df      = pd.DataFrame([data], columns=headers)

if versions == 1:
    df.to_csv('report.csv')
else:
    with open('report.csv', 'a') as f:
        df.to_csv(f, header=False)


# In[ ]:




