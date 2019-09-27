import json
import pandas as pd
import os
import h2o

from azureml.core.model import Model

def init():
    h2o.init()
    global model
    # retrieve the path to the model file using the model name
    model_path = Model.get_model_path('H2O_model_name')
    model = h2o.load_model(model_path)


def run(raw_data):
    data = pd.read_json(raw_data,orient='table')
    # make prediction
    h2data = h2o.H2OFrame(data)
    y_hat = h2o.as_list(model.predict(h2data))
    # you can return any data type as long as it is JSON-serializable
    return y_hat.to_json(orient="table")