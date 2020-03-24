import os
import csv
import json
import math
import shutil
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from datetime import datetime
from azureml.core.run import Run
from amlcallback import AMLCallback
from tensorflow.keras.callbacks import ModelCheckpoint

# Create a dictionary describing the features.
image_feature_description = {
    'height': tf.io.FixedLenFeature([], tf.int64),
    'width': tf.io.FixedLenFeature([], tf.int64),
    'depth': tf.io.FixedLenFeature([], tf.int64),
    'label': tf.io.FixedLenFeature([], tf.int64),
    'image': tf.io.FixedLenSequenceFeature([], tf.float32, allow_missing=True),
}

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

def split(records, split=[8, 2]):
    # normalize splits
    splits = np.array(split) / np.sum(np.array(split))
    # split data
    train_idx = int(len(records) * splits[0])
    
    return records[:train_idx], \
            records[train_idx:]

def parse_record(example_proto):
    # Parse the input tf.Example proto using the dictionary above.
    example = tf.io.parse_single_example(example_proto, image_feature_description)
    shape = [example['height'], 
             example['width'], 
             example['depth']]
    
    label = example['label']
    image = tf.reshape(example['image'], shape)
    return (image, label)


def main(run, source_path, target_path, epochs, batch, lr):
    info('Preprocess')
    
    print(f'Using Tensorflow v.{tf.__version__}')
    print(f'GPUs Available: {len(tf.config.experimental.list_physical_devices("GPU"))}')

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    # load tfrecord metadata
    prep_step = os.path.join(source_path, 'metadata.json')
    with open(prep_step) as f:
        prep = json.load(f)

    for i in prep:
        print('{} => {}'.format(i, prep[i]))

    labels = prep['categories']
    img_shape = (prep['image_size'], prep['image_size'], 3)
    record_sz = prep['records']

    records = os.path.join(source_path, prep['file'])
    print('Loading {}'.format(records))
    with open(records, 'r') as f:
        filenames = [os.path.join(source_path, s.strip()) for s in f.readlines()]
    
    print('Splitting data:')
    train, test = split(filenames)
    print('  Train: {}'.format(len(train)))
    print('   Test: {}'.format(len(test)))

    print('Creating training dataset')
    train_ds = tf.data.TFRecordDataset(train)
    train_ds = train_ds.map(map_func=parse_record, num_parallel_calls=5)
    train_ds = train_ds.shuffle(buffer_size=10000)
    train_ds = train_ds.batch(batch)
    train_ds = train_ds.prefetch(buffer_size=5)
    train_ds = train_ds.repeat(epochs)

    # model
    info('Creating Model')
    base_model = tf.keras.applications.MobileNetV2(input_shape=img_shape,
                                               include_top=False, 
                                               weights='imagenet',
                                               pooling='avg')
    base_model.trainable = True

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.Dense(len(labels), activation='softmax')
    ])

    model.compile(optimizer=tf.keras.optimizers.Adam(lr=lr), 
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])

    model.summary()
    
    # training
    info('Training')

    # callbacks
    logaml = AMLCallback(run)
    filename = datetime.now().strftime("%d.%b.%Y.%H.%M")
    checkpoint = ModelCheckpoint(os.path.join(target_path, filename + '.e{epoch:02d}-{accuracy:.2f}-v{val_accuracy:.2f}.hdf5'),
                                 monitor='val_accuracy',
                                 save_best_only=True)

    # using both test and val in this case
    test_ds = tf.data.TFRecordDataset(test).map(parse_record).batch(batch)
    test_steps = math.ceil((len(test)*record_sz)/batch)

    
    steps_per_epoch = math.ceil((len(train)*record_sz)/batch)
    history = model.fit(train_ds, 
                    epochs=epochs, 
                    steps_per_epoch=steps_per_epoch,
                    callbacks=[logaml, checkpoint],
                    validation_data=test_ds,
                    validation_steps=test_steps)

    info('Writing metadata')
    out_file = os.path.join(target_path, 'metadata.json')
    output = {
        'image_size': prep['image_size'],
        'categories': prep['categories'],
        'index': prep['index'],
        'generated': datetime.now().strftime('%m/%d/%y %H:%M:%S'),
        'run': str(run.id)
    }

    print('Writing out metadata to {}'.format(out_file))
    with open(str(out_file), 'w') as f:
        json.dump(output, f)
    print('Done!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='data cleaning for binary image task')
    parser.add_argument('-s', '--source_path', help='directory to training data', default='data')
    parser.add_argument('-t', '--target_path', help='directory to previous data step', default='data')
    parser.add_argument('-e', '--epochs', help='number of epochs', default=10, type=int)
    parser.add_argument('-b', '--batch', help='batch size', default=32, type=int)
    parser.add_argument('-l', '--lr', help='learning rate', default=0.0001, type=float)
    args = parser.parse_args()

    run = Run.get_context()
    offline = run.id.startswith('OfflineRun')
    print('AML Context: {}'.format(run.id))
    

    info('Input Arguments')
    params = vars(args)
    for i in params:
        print('{} => {}'.format(i, params[i]))
        if not offline:
            run.log(i, params[i])

    params['run'] = run

    main(**params)