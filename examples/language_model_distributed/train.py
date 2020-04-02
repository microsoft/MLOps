
import os
import shutil 
import argparse
import subprocess
from git.repo.base import Repo
from zipfile import ZipFile


WORK_DIR = 'examples'
SRC_DIR = '/transformers'
OUTPUT_DIR = os.path.join(os.getcwd(),'outputs')
DATA_DIR = os.path.join(os.getcwd(),'wikitext-2-raw')

REPO_URL="https://github.com/datashinobi/transformers.git"
BRANCH='yassine/aml_distributed'



parser = argparse.ArgumentParser()
parser.add_argument('--dataset-path', dest='ds_path')
parser.add_argument('--rank', type=str,help='rank within nodes')
parser.add_argument('--node_count', type=str,help='number of nodes')
parser.add_argument('--process_per_node', type=str,help='number of process per node')
parser.add_argument('--batch_size', type=str,help='training & eval batch size')

args = parser.parse_args()

#============Clone forked repo==========
if os.path.exists(SRC_DIR):
    print("huggingface repo exists, skip cloning")
else:
    print('clone huggingface repo..........')
    Repo.clone_from(REPO_URL,SRC_DIR, branch=BRANCH)

#===============Unzip dataset=============
data_file = os.path.join(args.ds_path,"wikitext-2-raw-v1.zip")
with ZipFile(data_file,"r") as zip_file:
    zip_file.extractall(os.getcwd())
print(os.listdir(DATA_DIR))

#===========start training=================
master_node_params = os.environ['AZ_BATCH_MASTER_NODE'].split(':')
print("MASTER node", master_node_params)
master_ip = master_node_params[0]
master_port = master_node_params[1]
if int(args.process_per_node) > 1:
    process = subprocess.Popen(['python', '-m', 'torch.distributed.launch',\
                            '--nnodes',args.node_count,\
                            '--nproc_per_node',args.process_per_node,\
                            '--node_rank', args.rank,\
                            '--master_addr',master_ip,\
                            '--master_port',master_port,\
                            os.path.join(SRC_DIR, WORK_DIR, 'run_language_modeling.py'),\
                            '--output_dir', OUTPUT_DIR,\
                            '--model_type', 'bert', \
                            '--model_name_or_path', 'bert-base', \
                            '--do_train', \
                            '--train_data_file', os.path.join(DATA_DIR, 'wiki.train.raw'),\
                            '--do_eval', \
                            '--eval_data_file', os.path.join(DATA_DIR, 'wiki.test.raw'),\
                            '--mlm',\
                            '--per_gpu_train_batch_size', args.batch_size,\
                            '--per_gpu_eval_batch_size', args.batch_size
                             ],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT
                        )
else:
    process = subprocess.Popen(['python', '-m', 'torch.distributed.launch',\
                            '--nnodes',args.node_count,\
                            '--nproc_per_node',args.process_per_node,\
                            '--node_rank', args.rank,\
                            '--master_addr',master_ip,\
                            '--master_port',master_port,\
                            os.path.join(SRC_DIR, WORK_DIR, 'run_language_modeling.py'),\
                            '--output_dir', OUTPUT_DIR,\
                            '--model_type', 'bert', \
                            '--model_name_or_path', 'bert-base-uncased', \
                            '--do_train', \
                            '--train_data_file', os.path.join(DATA_DIR, 'wiki.train.raw'),\
                            '--do_eval', \
                            '--eval_data_file', os.path.join(DATA_DIR, 'wiki.test.raw'),\
                            '--mlm',\
                            '--per_gpu_train_batch_size', args.batch_size,\
                            '--per_gpu_eval_batch_size', args.batch_size ,\
                            '--local_rank', '0'
                             ],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT
                        )
    

lines_iterator = iter(process.stdout.readline, b"")
while process.poll() is None:
    for line in lines_iterator:
        print(line, end = "\r\n",flush =True)   
