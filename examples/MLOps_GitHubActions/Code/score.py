import os
import json
import time
import logging
import requests
import datetime
import numpy as np
from PIL import Image
from io import BytesIO
import tensorflow as tf

# azureml imports
from azureml.core.model import Model

def init():
    global model, image_size, index, categories

    aml_logger = logging.getLogger('azureml')
    aml_logger.setLevel(logging.DEBUG)
    server_logger = logging.getLogger('root')
    server_logger.setLevel(logging.DEBUG)

    try:
        path = Model.get_model_path('seer')
    except:
        path = 'data/model'

    model_path = os.path.join(path, 'model.hdf5')
    meta_path = os.path.join(path, 'metadata.json')
    print('Loading {}'.format(meta_path))

    with open(meta_path) as f:
        metadata = json.load(f)

    for i in metadata:
        print('{} => {}'.format(i, metadata[i]))

    image_size = metadata['image_size']
    index = metadata['index']
    categories = metadata['categories']

    print('Attempting to load model')
    model = tf.keras.models.load_model(model_path)
    model.summary()
    print('Done!')

    print('Initialized model "{}" at {}'.format(model_path, datetime.datetime.now()))

def process_image(path):
    global image_size

    # Extract image (from web or path)
    if(path.startswith('http')):
        response = requests.get(path)
        img = np.array(Image.open(BytesIO(response.content)))
    else:
        img = np.array(Image.open(path))

    img_tensor = tf.convert_to_tensor(img, dtype=tf.float32)
    img_final = tf.image.resize(img_tensor, [image_size, image_size]) / 255
    return img_final

def run(raw_data):
    global model, image_size, index, categories
    prev_time = time.time()
          
    post = json.loads(raw_data)

    # get image
    img_path = post['image']
    tensor = process_image(img_path)
    t = tf.reshape(tensor, [-1, image_size, image_size, 3])

    # predict with model (there's only one)
    pred = model.predict(t, steps=1)[0]
    print(pred)

    current_time = time.time()
    inference_time = datetime.timedelta(seconds=current_time - prev_time)

    predictions = {}
    for i in range(len(pred)):
        predictions[categories[i]] = str(pred[i])

    payload = {
        'time': str(inference_time.total_seconds()),
        'prediction': categories[int(np.argmax(pred))],
        'scores': predictions
    }

    print('Input ({}),\nPrediction ({})'.format(post['image'], payload))

    return payload


if __name__ == '__main__':
    import pprint
    init()
    tacos = 'https://lh3.googleusercontent.com/-UT5H8nPflkQ/T4tqueyhb_I/AAAAAAAAGl8/1FP7G__Zuys/s640/Lentil+Tacos+close.jpg'
    burrito = 'https://www.exploreveg.org/files/2015/05/sofritas-burrito.jpeg'

    print('\n---------------------\nInference with tacos:')
    t = run(json.dumps({'image': tacos}))
    json.dumps(t)
    print('\n=======================')
    pprint.pprint(t)

    print('\n\n\nInference with burrito:')
    b = run(json.dumps({'image': burrito}))
    print('\n=======================')
    pprint.pprint(b)
    