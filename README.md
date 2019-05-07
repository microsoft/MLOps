# MLOps on Azure
[![Build Status](https://dev.azure.com/aidemos/MLOps/_apis/build/status/Microsoft.MLOps_Hub?branchName=master)](https://dev.azure.com/aidemos/MLOps/_build/latest?definitionId=90?branchName=master)

## What is MLOps?
MLOps empowers data scientists and app developers to help bring ML models to production. 
MLOps enables you to track / version / audit / certify / re-use every asset in your ML lifecycle and provides orchestration services to streamline managing this lifecycle.

## How does Azure ML help with MLOps?
Azure ML contains a number of asset management and orchestration services to help you manage the lifecycle of your model training & deployment workflows.

With Azure ML + Azure DevOps you can effectively and cohesively manage your datasets, experiments, models, and ML-infused applications.
![ML lifecycle](./media/ml-lifecycle.png)

## New MLOps features
- [Azure DevOps Machine Learning extension](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml) 
- [Azure ML CLI](https://aka.ms/azmlcli)

## Architecture Flow for MLOps

### Train Model
1. Data Scientist writes/updates the code and push it to git repo. This triggers an Azure DevOps build.
2. Once the Azure DevOps build pipeline is triggered, it runs following types of tasks:
    - Run for new code: Every time new code is committed to the repo, the build pipeline performs data sanity tests and unit tests on the new code.
    - One-time run: These tasks runs only for the first time the build pipeline runs. It will programatically create an [Azure ML Service Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#workspace), provision [Azure ML Compute](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-set-up-training-targets#amlcompute) (used for model training compute), and publish an [Azure ML Pipeline](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-ml-pipelines). This published Azure ML pipeline is the model training/retraining pipeline.
    
    > Note: The Publish Azure ML pipeline task currently runs for every code change

3. The Azure ML Retraining pipeline is triggered once the Azure DevOps build pipeline completes. All the tasks in this pipeline runs on Azure ML Compute created earlier. Following are the tasks in this pipeline:

    - **Train Model** task executes model training script on Azure ML Compute. It outputs a [model](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model) file which is stored in the [run history](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#run).

    - **Evaluate Model** task evaluates the performance of newly trained model with the model in production. If the new model performs better than the production model, the following steps are executed. If not, they will be skipped.

    - **Register Model** task takes the improved model and registers it with the [Azure ML Model registry](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model-registry). This allows us to version control it.

### Deploy Model

Once you have registered your ML model, you can use Azure ML + Azure DevOps to deploy it.

The **Package Model** task packages the new model along with the scoring file and its python dependencies into a [docker image](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#image) and pushes it to [Azure Container Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro). This image is used to deploy the model as [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service).
    
The **Deploy Model** task handles deploying your Azure ML model to the cloud (ACI or AKS).
This pipeline deploys the model scoring image into Staging/QA and PROD environments.

 In the Staging/QA environment, one task creates an [Azure Container Instance](https://docs.microsoft.com/en-us/azure/container-instances/container-instances-overview) and deploys the scoring image as a [web service](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#web-service) on it. 

The second task invokes the web service by calling its REST endpoint with dummy data.
    
5. The deployment in production is a [gated release](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/approvals/gates?view=azure-devops). This means that once the model web service deployment in the Staging/QA environment is successful, a notification is sent to approvers to manually review and approve the release. Once the release is approved, the model scoring web service is deployed to [Azure Kubernetes Service(AKS)](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) and the deployment is tested.

## How is MLOps different from DevOps?
- Data/model versioning != code versioning - how to version data sets as the schema and origin data change
- Digital audit trail requirements change when dealing with code + (potentially customer) data
- Model reuse is different than software reuse, as models must be tuned based on input data / scenario.
- To reuse a model you may need to fine-tune / transfer learn on it (meaning you need the training pipeline)
- Models tend to decay over time & you need the ability to retrain them on demand to ensure they remain useful in a production context.

# What are the key challenges we wish to solve with MLOps?

**Model reproducibility & versioning**
- Track, snapshot & manage assets used to create the model
- Enable collaboration and sharing of ML pipelines

**Model auditability & explainability**
- Maintain asset integrity & persist access control logs
- Certify model behavior meets regulatory & adversarial standards

**Model packaging & validation**
- Support model portability across a variety of platforms
- Certify model performance meets functional and latency requirements

**Model deployment & monitoring**
- Release models with confidence
- Monitor & know when to retrain

# MLOps Solutions
We are committed to providing a collection of best-in-class solutions for MLOps, both in terms of well documented & fully managed cloud solutions, as well as reusable recipes which can help your organization to bootstrap its MLOps muscle.

All of our examples will be built in the open and we welcome contributions from the community!
- https://github.com/Microsoft/MLOpsPython
- https://github.com/Microsoft/Recommenders
- https://github.com/MicrosoftDocs/pipelines-azureml
- https://github.com/Microsoft/MLOps_VideoAnomalyDetection

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
