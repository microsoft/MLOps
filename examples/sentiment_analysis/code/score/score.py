import json
import numpy as np
from fastai.text import *
from azureml.core.model import Model
import logging
logging.basicConfig(level=logging.DEBUG)

def init():
    global model
    model_path = Model.get_model_path('sa_classifier')
    
    model_path = os.path.split(model_path)
    model = load_learner(path=model_path[0], file =model_path[1])


def run(data):
    try:
        result =  model.predict(data)
        output = json.dumps({'sentiment':str(result[0]),
                             'likelihood':str(result[2])
                            }
                           )
        return output
    except Exception as e:
        error = str(e)
        return error