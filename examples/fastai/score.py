from azureml.core import Workspace, Model
from fastai.vision import *
from fastai.metrics import error_rate
import urllib.request

global img_url
img_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTlaJelWZrzIO3CNNkhdTOGfkD396zo1xaR5DrIZaO7FiBPCdWHKg&s"

def download_jpg(url):
    file_path = "./candidate.jpg"
    result = urllib.request.urlretrieve(url, file_path)
    print(result)
    return file_path

def init():
    global pets_model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    # For multiple models, it points to the folder containing all deployed models (./azureml-models)
    path=os.getenv('AZUREML_MODEL_DIR')
    filename="lesson1-pets-resnet34-23Jan20.pkl"
    pets_model = load_learner(path=path, file=filename)

    print(pets_model.data.classes)

def run(request):
    try:
        print("start")
        candidate_url = request.args.get("url", img_url)
        
        file_path = download_jpg(candidate_url)
        print(file_path)

        img = open_image(file_path)
        print(img)
        
        prediction = pets_model.predict(img)
        
        print(prediction)
        return str(prediction[0])
    except Exception as e:
        result = str(e)
        print(result)
        return result

if __name__ == "__main__":
    init()
    run([])
    print("main")
