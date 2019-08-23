#!/usr/bin/env python
# coding: utf-8

# In[20]:


import os
import sys

from azureml.core import Workspace, Dataset

from azureml.opendatasets import NoaaIsdWeather

from datetime import datetime, timedelta


# In[21]:


ws = Workspace.get('retrainingPMVP', subscription_id='60582a10-b9fd-49f1-a546-c4194134bba8')


# In[22]:


dstore = ws.get_default_datastore()


# In[36]:


def get_data(start, delta):
    os.makedirs('data', exist_ok=True)
    
    t1   = start + timedelta(days=28*(delta-1))
    t2   = start + timedelta(days=28*delta)

    isd   = NoaaIsdWeather(t1, t2)
    df    = isd.to_pandas_dataframe()
    df    = df[df['stationName'].str.contains('FLORIDA|TEXAS', na=False, regex=True)]
    df    = df.drop(columns = ['cloudCoverage', 'presentWeatherIndicator', 'pastWeatherIndicator', 'snowDepth', 'stationName', 'countryOrRegion', 'p_k'])
        
    df.to_csv('data/{}.csv'.format(delta), index=False)
    dstore.upload('data', target_path='data', overwrite=True, show_progress=True)
    
    dset = Dataset.from_delimited_files(dstore.path('data/{}.csv'.format(delta)))
    
    dset.register(ws, '{}'.format(delta), exist_ok=True, update_if_exist=True)


# In[37]:


import sys

delta  = int(sys.argv[1])
START  = datetime(2016, 1, 1)

get_data(START, delta)


# In[ ]:




