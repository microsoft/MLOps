#!/bin/bash
## Script to setup resources needed to train the model

# Login to the Azure subscription
az login
# Install the Azure Machine Learning extension, if it's not already installed
az extension add -n azure-cli-ml
# Try to update it, in case it's already installed
az extension update -n azure-cli-ml

# Prompt for input
echo -e "Enter the resource group name:"
read RESOURCEGROUP
echo -e "Enter the Azure region to use:"
read LOCATION
echo -e "Enter the Azure Machine Learning workspace name:"
read WORKSPACE

# Create a new resourcegroup
echo "Creating resource group"
az group create --name $RESOURCEGROUP --location $LOCATION

# Create the workspace
echo "Creating workspace"
az ml workspace create -w $WORKSPACE -g $RESOURCEGROUP 

# Cache the workspace/resource/location info in the local folder
echo "Attaching folder to workspace"
az ml folder attach -w $WORKSPACE -g $RESOURCEGROUP

# Create the compute target used to train the model
echo "Creating the compute target for training"
az ml computetarget create amlcompute -n cpu-cluster \
   --max-nodes 4 --vm-size Standard_D2_V2

# Register the dataset
echo "Registering training dataset"
az ml dataset register -f dataset.json

# Start the training run
echo "Starting training run"
az ml run submit-script -c mnist -e myexperiment --source-directory scripts -t runoutput.json

# Register the trained model
echo "Registering the trained model"
az ml model register -n mymodel -f runoutput.json --asset-path "outputs/sklearn_mnist_model.pkl" -t registeredmodel.json

# Deploy the registered model
echo "Deploying the registered model as a web service"
az ml model deploy -n myservice -m "mymodel:1" --ic inferenceConfig.yml --dc aciDeploymentConfig.yml

# Submit test data against the deployed model
echo "Sending test data to the web service"
az ml service run -n myservice -d @testdata.json