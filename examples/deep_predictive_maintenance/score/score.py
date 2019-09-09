
import os
import json
import numpy as np
import torch
from azureml.core.model import Model

def init():
    global model
    
    model_path = Model.get_model_path('deep_pdm')
    print("model loaded:",model_path)
    
    model = torch.load(model_path, map_location=torch.device('cpu'))
    model.eval()
    

def run(input_data):
    x_input = torch.tensor(json.loads(input_data)['input_data'])
    score,proba = model(x_input)
    
    score = score.data.numpy().argmax(axis=1).item()
    proba = proba.view(-1)[0].item()
    
    return {'prediction':int(score), 'likelihood':float(proba)}