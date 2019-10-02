

import argparse
import os
import tensorflow as tf
import fileinput
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--dataset-path', dest='ds_path')
parser.add_argument('--epochs', dest='epochs')

args = parser.parse_args()
data_path = args.ds_path
epochs = args.epochs

tf_path = tf.__path__
print('tf.__path__',tf_path)
TF_MODELS_DIR = os.path.join(tf.__path__[1],
                             'models',
                             'research',
                             'object_detection')

OUTPUT_DIR = 'outputs'
LOGS_DIR = 'logs'
for directory in [OUTPUT_DIR,LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)


rcnn_config_file = 'faster_rcnn_resnet101_pets.config'
rcnn_config_path = os.path.join(TF_MODELS_DIR,
                                'samples',
                                'configs',
                                rcnn_config_file)

for line in fileinput.input(rcnn_config_path, inplace=True):
    print(line.replace("PATH_TO_BE_CONFIGURED", data_path))

with open(rcnn_config_path,"r") as f:
    print(f.readline())


shutil.copy(rcnn_config_path, 
           os.path.join(data_path, rcnn_config_file))


pipeline_config_arg = f'--pipeline_config_path={rcnn_config_path}'
epochs_arg = f'--num_train_steps={epochs}'
model_dir_arg = f'--model_dir={OUTPUT_DIR}'

#start training
process = subprocess.Popen(['python',
                            os.path.join(TF_MODELS_DIR,'model_main.py'),
                            pipeline_config_arg,
                            model_dir_arg,
                            epochs_arg,
                            '--sample_1_of_n_eval_examples=1',
                            '--alsologtostderr'
                             ],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT
                        )

lines_iterator = iter(process.stdout.readline, b"")
while process.poll() is None:
    for line in lines_iterator:
        print(line, end = "\r\n",flush =True)
        
# Write event to logs directory
shutil.move(os.path.join(OUTPUT_DIR,"eval_0"),  LOGS_DIR)