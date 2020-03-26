
import os
import shutil,glob
import argparse
from git.repo.base import Repo


SRC_DIR = '/maskrcnn'
SAMPLES_DIR = os.path.join(SRC_DIR,'samples')
LOGS_DIR = os.path.join(os.getcwd(),'logs')
os.makedirs(LOGS_DIR, exist_ok = True)

parser = argparse.ArgumentParser()
parser.add_argument('--is_distributed', type=bool,help='Distributed training')

args = parser.parse_args()
is_distributed = args.is_distributed

#=====Clone distributed training implementation of Mask_RCNN==========

REPO_URL="https://github.com/datashinobi/Mask_RCNN.git"
BRANCH='yassine/horovod'

if os.path.exists(SRC_DIR):
    print("Repo exists, skip cloning")
else:
    print('Clonerepo..........')
    Repo.clone_from(REPO_URL,SRC_DIR, branch=BRANCH)

#=====move training code to source dir=====
shutil.copytree(os.path.join(os.getcwd(),'horovod'), os.path.join(SAMPLES_DIR,'horovod'))  

os.chdir(os.path.join(SAMPLES_DIR,'horovod'))

from train import run
run(is_distributed,LOGS_DIR)
