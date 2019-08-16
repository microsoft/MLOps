# MLOps on Azure
- [![Build Status](https://dev.azure.com/aidemos/MLOps/_apis/build/status/microsoft.MLOps?branchName=master)](https://dev.azure.com/aidemos/MLOps/_build/latest?definitionId=96?branchName=master)
- [Example MLOps Release Pipeline](https://dev.azure.com/aidemos/ClassicalML-BuildDemo/_release?definitionId=1)
- [MLOps Architecture Deep Dive-  YouTube](https://www.youtube.com/watch?v=nst3UAGpiBA)
- [Official Python Azure MLOps repo](https://github.com/Microsoft/MLOpsPython)

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
- [Set up model training & deployment with Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/pipelines/targets/azure-machine-learning?view=azure-devops)

> If you are using the Machine Learning DevOps extension, you can access model name and version info using these variables:
> - Model Name: Release.Artifacts.{alias}.DefinitionName containing model name
> - Model Version: Release.Artifacts.{alias}.BuildNumber 
> where alias is source alias set while adding the release artifact. 

## Getting Started / MLOps Workflow
An example repo which exercises our recommended flow can be found [here](https://github.com/Microsoft/MLOpsPython)

## MLOps Best Practices
### Train Model
- Data scientists work in topic branches off of master.
- When code is pushed to the Git repo, trigger a CI (continuous integration) pipeline.
- First run: Provision infra-as-code (ML workspace, compute targets, datastores).
- For new code: Every time new code is committed to the repo, run unit tests, data quality checks, train model.

We recommend the following steps in your CI process:
- **Train Model** - run training code / algo & output a [model](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model) file which is stored in the [run history](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#run).
- **Evaluate Model** - compare the performance of newly trained model with the model in production. If the new model performs better than the production model, the following steps are executed. If not, they will be skipped.
- **Register Model** - take the best model and register it with the [Azure ML Model registry](https://docs.microsoft.com/en-us/azure/machine-learning/service/concept-azure-machine-learning-architecture#model-registry). This allows us to version control it.

### Operationalize Model
- You can package and validate your ML model using the **Azure ML CLI**.
- Once you have registered your ML model, you can use Azure ML + Azure DevOps to deploy it.
- You can define a **release definition** in Azure Pipelines to help coordinate a release. Using the DevOps extension for Machine Learning, you can include artifacts from Azure ML, Azure Repos, and GitHub as part of your Release Pipeline.
- In your release definition, you can leverage the Azure ML CLI's **model deploy** command to deploy your Azure ML model to the cloud (ACI or AKS).
- Define your deployment as a [gated release](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/approvals/gates?view=azure-devops). This means that once the model web service deployment in the Staging/QA environment is successful, a notification is sent to approvers to manually review and approve the release. Once the release is approved, the model scoring web service is deployed to [Azure Kubernetes Service(AKS)](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) and the deployment is tested.

# MLOps Solutions
We are committed to providing a collection of best-in-class solutions for MLOps, both in terms of well documented & fully managed cloud solutions, as well as reusable recipes which can help your organization to bootstrap its MLOps muscle. These examples are community supported and are not guaranteed to be up-to-date as new features enter the product.

All of our examples will be built in the open and we welcome contributions from the community!
- https://github.com/Microsoft/MLOpsPython (reference architecture for MLOps + python)
- https://github.com/Microsoft/Recommenders (recommender systems with E2E mlops baked in)
- https://github.com/MicrosoftDocs/pipelines-azureml (CI/CD with the azure ML CLI)
- https://github.com/Microsoft/MLOps_VideoAnomalyDetection (self-supervised learning with hyperparameter tuning and automated retraining)
- https://github.com/Azure-Samples/MLOpsDatabricks (set up MLOps with Azure ML + databricks)
- https://github.com/roalexan/azureml#schedule-using-adf  (schedule an azure ML pipeline from an azure data factory pipeline)
- https://www.azuredevopslabs.com/labs/vstsextend/aml/ (automated template to deploy MLOps on ADO)
- https://github.com/Azure/ACE_Azure_ML/tree/master/devops (set up azure ML + azure DevOps together for predictive maintenance)

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
- Monitor & know when to retrain by analyzing signals such as data drift

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
