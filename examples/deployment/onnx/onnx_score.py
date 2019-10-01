import json
import numpy as np
import onnxruntime
import sys
import os
from azureml.core.model import Model
import time


def init():
    global session, input_name, output_name
    model = os.path.join(os.getenv('AZUREML_MODEL_DIR'),'model.onnx')
    session = onnxruntime.InferenceSession(model, None)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name 
    

def preprocess(input_data_json):
    # convert the JSON data into the tensor input
    return np.array(json.loads(input_data_json)['data']).astype('float32')

def postprocess(result):
    # We use argmax to pick the highest confidence label
    return int(np.argmax(np.array(result).squeeze(), axis=0))
    
def run(input_data):

    try:
        # load in our data, convert to readable format
        data = preprocess(input_data)
        
        # start timer
        start = time.time()
        
        r = session.run([output_name], {input_name: data})
        
        #end timer
        end = time.time()
        
        result = postprocess(r)
        result_dict = {"result": result,
                      "time_in_sec": end - start}
    except Exception as e:
        result_dict = {"error": str(e)}
    
    return result_dict

def choose_class(result_prob):
    """We use argmax to determine the right label to choose from our output"""
    return int(np.argmax(result_prob, axis=0))
