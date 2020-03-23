
import argparse
import pandas as pd
import numpy as np
import os.path


def extract_metadata(input_path, output_path):
    '''
        Extract and write metadata from images dataset to dataframe

        parameters:
            input_path: directory path to Images directory
            output_path: directory path to output directory
        
    '''
    df = pd.DataFrame(columns=['path', 'age','label'])
    
    for  file in os.listdir(input_path):
        index = file.find('A')
        age = int(file[index+1:index+3])
        label = int(file[:index])
        df = df.append(pd.Series([file,age,label],index=['path', 'age','label']), ignore_index=True)
    
    df.to_csv(output_path)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--images_dir')
    parser.add_argument('--metadata_path')
    

    images_dir = parser.parse_args().images_dir
    metadata_path = parser.parse_args().metadata_path
    
    os.makedirs(metadata_path, exist_ok = True)
    output_path = os.path.join(metadata_path, 'metadata.csv')
    extract_metadata(images_dir,output_path)