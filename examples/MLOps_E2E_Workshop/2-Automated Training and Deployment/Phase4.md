# Phase 4: Training from a DevOps Pipeline

So far you've spent some time looking at Azure ML pipelines. In Challenge 3 you used a notebook to set up an Azure ML pipeline that trained and registered a model. A notebook is convenient for experimentation, but is not suited for automating a full workflow. This is where Azure DevOps comes in. Using Azure Pipelines to operationalize Azure ML pipelines enables powerful tools such as version management, model/data validation, model evaluation/selection, and staged deployments to QA/production. For this challenge, you'll set up an Azure Pipeline that reproduces the Azure ML pipeline created in your notebook in Challenge 3.

* The word 'pipeline' has started to take on multiple meanings - make sure you don't get pipeline types mixed up. See [here](https://docs.microsoft.com/azure/machine-learning/concept-ml-pipelines#which-azure-pipeline-technology-should-i-use) for a description of the pipeline types. For clarity, these challenges are referring to 'Azure Pipelines' as 'DevOps pipelines'.

## Prerequisites 

Complete all of the phases from reproducible training. 

## Resources

* [Key concepts for new Azure Pipelines users](https://docs.microsoft.com/azure/devops/pipelines/get-started/key-pipelines-concepts?view=azure-devops)
* [*MLOpsPython* - templates to create Azure DevOps CI/CD pipelines for Azure ML](https://github.com/microsoft/MLOpsPython)
* [Azure Pipelines YAML schema reference](https://docs.microsoft.com/azure/devops/pipelines/yaml-schema?view=azure-devops&tabs=schema)
* [Machine Learning extension for Azure DevOps](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml)

## Tasks

1. Using [MLOpsPython](https://github.com/microsoft/MLOpsPython) as a template, create an Azure DevOps pipeline that creates and runs an Azure ML pipeline to train, validate, and register a model based on your training scripts. 
    * Start with the MLOpsPython [Getting Started guide](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md) before tackling this task. 
    * Instead of trying to reuse the existing resources from your subscription, create new resources in a new resource group.
    * Replace the environment_setup folder from MLOpsPython with the environment_setup folder in the **automated training and deployment** folder of the OpenHack files. This will allow you to create Azure resources required by this challenge and the later ones.
    * Set the DevOps pipeline variable ```RUN_EVALUATION``` to false. Evaluation will be explored in a later challenge.
    * Use mcr.microsoft.com/mlops/python:openhack Docker image instead of mcr.microsoft.com/mlops/python:latest which is used in MLOpsPython repo
    * Upload the training data file to the ***trainingdata*** container in the created blob storage account
    * Create a ***Datastore*** in the AML workspace pointing to the uploaded data file.
    * Specify the Datastore name in the ```DATASTORE_NAME``` environment variable and the data file name in the ```DATAFILE_NAME``` environment variable 
    * Add ***lightgbm*** package to the dependencies and ***azureml-dataprep*** package to the pip dependencies in the dependencies yml file.
2. Configure the DevOps pipeline to run lint and unit tests before creating the Azure ML pipeline.
    * Unit tests are provided in the **automated training and deployment** folder.
    * Additionally, you are expected to implement a policy so that any code change submitted as a PR must pass unit tests and linting before being merged to the master branch.
3. Configure the DevOps pipeline to deploy the model to Azure Container Instances (ACI).
    * To satisfy this challenge you only need to deploy to [Azure Container Instances](https://azure.microsoft.com/services/container-instances/), which is generally suitable for a QA deployment. For a production deployment you may wish to deploy to an [Azure Kubernetes Cluster](https://docs.microsoft.com/azure/aks/intro-kubernetes), or [Azure App Service](https://docs.microsoft.com/azure/app-service/containers/quickstart-docker).

4. Perform basic validation that the ACI deployment was successful.

### Success Criteria

To successfully complete this task, you must demonstrate: 

* An Azure DevOps CI/CD pipeline that:
    * Has a policy to prevent any unreviewed code changes from being committed to the master branch prior to successful linting and unit test runs.
    * Runs the code quality tests (linting) and unit tests in the master branch prior to publishing the Azure ML training pipeline. The test results are available in Azure DevOps UI. The CI pipeline fails if the tests are not successful.
    * Creates, publishes and runs an Azure ML training pipeline.
    * Deploys a registered model to Azure Container Instances (ACI) and performs a smoke test of the deployment.


## Reflect

1. Why are lint and unit tests run before creating the Azure ML pipeline?
