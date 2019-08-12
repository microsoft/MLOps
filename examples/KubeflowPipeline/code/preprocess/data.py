import os
import time
import shutil
import wget
import zipfile
import argparse
import numpy as np
import tensorflow as tf
from pathlib2 import Path

def check_dir(path, check=False):
    if check:
        assert os.path.exists(path), '{} does not exist!'.format(path)
    else:
        if not os.path.exists(path):
            os.makedirs(path)
        return Path(path).resolve(strict=False)

def download(source, target, force_clear=False):
    if force_clear and os.path.exists(target):
        print('Removing {}...'.format(target))
        shutil.rmtree(target)

    check_dir(target)
    
    targt_file = str(Path(target).joinpath('data.zip'))
    if os.path.exists(targt_file) and not force_clear:
        print('data already exists, skipping download')
        return

    if source.startswith('http'):
        print("Downloading from {} to {}".format(source, target))
        wget.download(source, targt_file)  
        print("Done!")
    else:
        print("Copying from {} to {}".format(source, target))
        shutil.copyfile(source, targt_file)

    print('Unzipping {}'.format(targt_file))
    zipr = zipfile.ZipFile(targt_file)
    zipr.extractall(target)
    zipr.close()

def process_image(path, image_size=160):
    img_raw = tf.io.read_file(path)
    img_tensor = tf.image.decode_jpeg(img_raw, channels=3)
    img_final = tf.image.resize(img_tensor, [image_size, image_size]) / 255
    return img_final

def walk_images(base_path, image_size=160):
    images = []
    print('Scanning {}'.format(base_path))
    # find subdirectories in base path
    # (they should be the labels)
    labels = []
    for (_, dirs, _) in os.walk(base_path):
        print('Found {}'.format(dirs))
        labels = dirs
        break

    for d in labels:
        path = os.path.join(base_path, d)
        print('Processing {}'.format(path))
        # only care about files in directory
        for item in os.listdir(path):
            if not item.lower().endswith('.jpg'):
                print('skipping {}'.format(item))
                continue

            image = os.path.join(path, item)
            try:
                img = process_image(image, image_size)
                assert img.shape[2] == 3, "Invalid channel count"
                # write out good images
                images.append(image)
            except Exception as e:
                print('{}\n{}\n'.format(e, image))

    return images

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='data cleaning for binary image task')
    parser.add_argument('-b', '--base_path', help='directory to base data', default='../../data')
    parser.add_argument('-d', '--data', help='directory to training data', default='train')
    parser.add_argument('-t', '--target', help='target file to hold good data', default='train.txt')
    parser.add_argument('-i', '--img_size', help='target image size to verify', default=160, type=int)
    parser.add_argument('-z', '--zipfile', help='source data zip file', default='../../tacodata.zip')
    parser.add_argument('-f', '--force', help='force clear all data', default=False, action='store_true')
    args = parser.parse_args()
    print(args)

    print('Using TensorFlow v.{}'.format(tf.__version__))

    base_path = Path(args.base_path).resolve(strict=False)
    print('Base Path:  {}'.format(base_path))
    data_path = base_path.joinpath(args.data).resolve(strict=False)
    print('Train Path: {}'.format(data_path))
    target_path = Path(base_path).resolve(strict=False).joinpath(args.target)
    print('Train File: {}'.format(target_path))
    zip_path = args.zipfile

    print('Acquiring data...')
    download('https://aiadvocate.blob.core.windows.net/public/tacodata.zip', str(base_path), args.force)

    if os.path.exists(str(target_path)):
        print('dataset text file already exists, skipping check')
    else:
        print('Testing images...')
        images = walk_images(str(data_path), args.img_size)

        # save file
        print('writing dataset to {}'.format(target_path))
        with open(str(target_path), 'w+') as f:
            f.write('\n'.join(images))

    # python data.py -z https://aiadvocate.blob.core.windows.net/public/tacodata.zip -t train.txt
