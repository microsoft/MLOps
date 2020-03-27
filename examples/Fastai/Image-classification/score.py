
import os
import json
from azureml.core.model import Model
from azureml.core import Workspace
import fastai 
from fastai.vision import *
from fastai.metrics import accuracy 
from fastai.metrics import error_rate
import urllib.request


def download_jpg(url):
    file_path = "./breadpudding.jpg"
    local_filename, header = urllib.request.urlretrieve(url, file_path)    
    return local_filename

def init():   
    global food_classification_model
    # The AZUREML_MODEL_DIR environment variable indicates a directory containing the model file you registered.  
    #this init works 
    model_path=os.getenv('AZUREML_MODEL_DIR')     
    filename="export.pkl"
    classes = ['apple-pie','breadpudding','padthai', 'ramen', 'waffles']
    food_classification_model = load_learner(path=model_path, file=filename)   
    classes = food_classification_model.data.classes
    print(classes)


def run(request):   
    candidate_url = json.loads(request)["url"]   
    file_path = download_jpg(candidate_url)
    img = open_image(file_path)
    prediction = food_classification_model.predict(img)
    index = 0
    pred = str(prediction[index])
    print(pred)
    return pred


# if __name__ == "__main__":
#     init()  
#     request = { "url": "https://i.imgur.com/TqlREOJ.jpg"}
#     run(request)
#     print("main")
