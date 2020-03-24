# MLOps with GitHub Actions and Event Grid 

This example shows you how to use Azure Machine Learning, GitHub Actions and Event Grid to create a CI/CD flow. The intent of this project is to provide references on how you can implement this withyour own projects. 

# Preqrequisites 

It's reccomended that you have an understanding of Azure Machine Learning and have at least contributor access to an Azure Machine Learning workspace. Here are some features and concepts the repo will be using: 

* [MLOps on Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment)
* [Azure Machine Learning Pipelines](https://docs.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines)
* [Azure Event Grid integration with Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-event-grid)


# Content

## Code

This folder contains example code to build an image classifaction model to distinguish betweens tacos and burritos. You can replace any of the training code with your own. Additionally this folder also porvides a build and deploy yaml in the subfolder **workflows** that you will trigger as actions. 

## Azure Function 

This folder contains code for a simple Azure function that gets trigger by a model registration event (via event grid). This is important when automating continuous model deployment. 
