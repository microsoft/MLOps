
import argparse
import pandas as pd
import numpy as np
import os.path
import cv2
from azureml.core.run import Run
from keras_vggface import utils
from keras.engine import  Model
from keras.layers import Input
from keras_vggface.vggface import VGGFace
import h5py
import matplotlib.pyplot as plt

def features_extractor(X):
    """
     Part 1 of the face recognition pipeline extract 1st F layer from VGGFace 
    

    input : X 4D tensors (m,224,224,3)
    output: features matrix (m,4096)
    """
    # preprocess 
    X = X.astype(np.float64)/255.
    
    # Layer Features
    layer_name = 'fc6' 
    vgg_model = VGGFace() 
    print(vgg_model.summary())
    
    out = vgg_model.get_layer(layer_name).output
    vgg_model_new = Model(vgg_model.input, out)
    X_features = vgg_model_new.predict(X)
    
    X_features = X_features /np.linalg.norm(X_features,axis =1, keepdims=True)
    return X_features
    
    
def to_tensors(df):

    """
        convert images in path columns to numpy 4D tensors
    """
    X = df.path.apply(lambda path: cv2.imread(path))
    X = np.stack(X, axis = 0)
    
    return X

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--metadata_path')
    parser.add_argument('--images_dir')
    parser.add_argument('--vggface_path')
    
    images_dir = parser.parse_args().images_dir
    metadata_path =parser.parse_args().metadata_path
    vggface_path =parser.parse_args().vggface_path
    
    os.makedirs(vggface_path, exist_ok = True)

    df = pd.read_csv(os.path.join(metadata_path, 'metadata.csv'))
    df.loc[:,'path'] = df.path.apply(lambda path: os.path.join(images_dir, path))
    X, y = to_tensors(df), df.label.values
    
    X_features = features_extractor(X)
    np.save(os.path.join(vggface_path, 'X.npy'), X_features)
    np.save(os.path.join(vggface_path, 'y.npy'), y)