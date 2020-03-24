import os
import csv
import json
import shutil
import random
import argparse
import tensorflow as tf
from pathlib import Path
from datetime import datetime

def _float_feature(value):
    """Returns a float_list from a float / double."""
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _floats_feature(value):
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(float_list=tf.train.FloatList(value=value.reshape(-1)))

def info(msg, char = "#", width = 75):
    print("")
    print(char * width)
    print(char + "   %0*s" % ((-1*width)+5, msg) + char)
    print(char * width)

def example(base_path, rel_path, labelidx, image_size=160):
    # get path
    image_path = os.path.join(base_path, rel_path)
    
    # load bits and resize
    img_raw = tf.io.read_file(image_path)
    img_tensor = tf.image.decode_jpeg(img_raw, channels=3)
    img_final = tf.image.resize(img_tensor, [image_size, image_size]) / 255
    
    img_shape = img_final.shape
    assert img_shape[2] == 3, "Invalid channel count"
    
    # feature descriptions
    feature = {
        'height': _int64_feature(img_shape[0]),
        'width': _int64_feature(img_shape[1]),
        'depth': _int64_feature(img_shape[2]),
        'label': _int64_feature(int(labelidx)),
        'image': _floats_feature(img_final),
    }
    
    example = tf.train.Example(features=tf.train.Features(feature=feature))
    
    return example

def main(source_path, target_path, records, image_size, force):
    info('Preprocess')
    raw_path = Path(source_path)

    categories = sorted([str(p.relative_to(source_path)) for p in list(raw_path.glob('*/'))])

    if len(categories) == 0:
        raise Exception('There is no visible data to parse!')

    index = dict((name, index) for index, name in enumerate(categories))

    images = [[str(p.relative_to(source_path)),
               str(p.parent.relative_to(source_path)),
               index[str(p.parent.relative_to(source_path))]] for p in list(raw_path.glob('*/*'))]

    random.shuffle(images)
    random.shuffle(images)
    random.shuffle(images)

    # check for existing files on force clear
    write_path = os.path.join(target_path, 'tfrecords')
    processed_files = os.path.join(target_path, 'files.csv')
    out_file = os.path.join(target_path, 'metadata.json')

    if force and os.path.exists(write_path):
        info('Cleanup')
        print('Removing "{}"'.format(write_path))
        shutil.rmtree(write_path, ignore_errors=True)
    if force and os.path.exists(processed_files):
        print('Removing "{}"'.format(processed_files))
        os.remove(processed_files)
    if force and os.path.exists(out_file):
        print('Removing "{}"'.format(out_file))
        os.remove(out_file)
    info('Processing Images')
    
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    if not os.path.exists(write_path):
        os.makedirs(write_path)

    print('Writing to {}'.format(write_path))

    total_records = 0
    tfrecords = []
    writer = None
    record_file = os.path.join(write_path, '{}.tfrecords')

    for row in images:
        if total_records % records == 0:
            if writer != None:
                writer.flush()
                writer.close()
            tfrecord = record_file.format('images{}_{}'.format(total_records//records, records))
            tfrecords.append(tfrecord)
            info('Writing to {}'.format(tfrecord))
            writer = tf.io.TFRecordWriter(tfrecord)
        try:
            print('Trying {}...'.format(row[0]), end=' ')
            image = example(source_path, row[0], row[2], image_size)
            writer.write(image.SerializeToString())
            total_records += 1
            print('Success!')
        except Exception as e:
            print('Error: {}'.format(e))

    if writer != None:
        writer.flush()
        writer.close()

    info('Post process')
    
    print('Writing out record listing to {}'.format(processed_files))
    with open(processed_files, 'w') as f:
        for line in tfrecords:
            f.write('{}\n'.format(str(Path(line).relative_to(target_path))))

    output = {
        'data': str(Path(write_path).relative_to(target_path)),
        'file': str(Path(processed_files).relative_to(target_path)),
        'image_size': image_size,
        'records': records,
        'categories': categories,
        'index': index,
        'generated': datetime.now().strftime('%m/%d/%y %H:%M:%S'),
        'total_records': total_records,
        'total_files': len(tfrecords)
    }

    print('Writing out metadata to {}'.format(out_file))
    with open(str(out_file), 'w') as f:
        json.dump(output, f)

    print('Done!\nProcessed {} records.'.format(total_records))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='data cleaning for binary image task')
    parser.add_argument('-s', '--source_path', help='directory to raw data', default='data')
    parser.add_argument('-t', '--target_path', help='directory to cleaned data', default='data')
    parser.add_argument('-r', '--records', help='images per TFRecord', default=16, type=int)
    parser.add_argument('-i', '--image_size', help='resize height and width', default=160, type=int)
    parser.add_argument('-f', '--force', help='force clear all data', default=False, action='store_true')
    args = parser.parse_args()

    params = vars(args)
    for i in params:
        print('{} => {}'.format(i, params[i]))

    main(**params)