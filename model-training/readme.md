# Model Training with MLOps
This folder contains training scripts and configuration which can be used to train a model using Azure ML.

- **.azureml/sklearn.runconfig** is a serialized configuration which specifices the environment( base image and package dependencies) required to train your ML model.

- **train-sklearn.py** is a normal scikit-learn training script

- **training-env.yml** is a conda dependencies file which can be used to run this training script locally.

# How to train
First, set up your workspace with the Azure ML CLI. See https://aka.ms/azmlcli for more info.

After you have the CLI installed, you can execute a remote run of this training script by running the following command
```cli
az ml run submit-script -e test -c sklearn -d training-env.yml train-sklearn.py
```
