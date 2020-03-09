# Phase 8: Data Ops for ML: CI/CD Pipelines as Code

The data ingestion solution is a combination of code and a pipeline orchestrating it. As with any software solution, the DevOps practices must be applied to its development lifecycle. In this challenge, we will configure SCM with branching policy and CI/CD pipelines to deploy the data ingestion solution across environments.

## Prerequisites

Before starting this challenge, make sure you have the following prerequisite requirements:

* A data ingestion pipeline from the previous challenge
* A new target (QA) environment consisting of:
    * Azure Data Factory workspace
    * Azure Databricks workspace

Use Azure Portal to manually provision Azure Data Factory and Azure Databricks workspaces.
For the sake of simplicity reuse storage account and AML workspace (with a published ML pipeline) from the previous challenges in the QA environment.

## Tasks

1. Have the source code of the data ingestion solution stored in a source code repository (git). Implement branching policy for the data pipeline and the notebooks.
2. Implement CI/CD pipelines deploying the data ingestion pipeline and the notebooks to the target environment.

### Hints

* Use ***Invoke-ADFPipeline.ps1***(/adf/utils/Invoke-ADFPipeline.ps1) to run an ADF pipeline
* Use ***test-data-ingestion.py***(/code/dataingestion/test-data-ingestion.py) to check if the data is ingested/transformed correctly
* Make sure ***arm-template-parameters-definition.json***(/adf/resources/arm-template-parameters-definition.json) file is in the ADF source code folder

### Success Criteria

To successfully complete this task, you must demonstrate: 

* Source control management of the data ingestion pipeline including the data preparation Python code.
* The ability to work with the source code as a team following a branching policy.
* Azure DevOps CI/CD pipelines deploying the whole data ingestion pipeline to the target environment. Have the solution parametrized so it can be deployed to multiple environments.
    * Lint the Python code
    * Deploy an ADF pipeline and the Python data preparation code
    * Test run of the deployed ADF pipeline
    * Integration test checking if the data is ingested/transformed correctly
* Azure DevOps CI/CD pipelines stored in a source code repository (git)
* Dropping an input file to the input blob container will automatically start the pipeline execution, transfer the data, and invoke AML training pipeline

### Resources

* [CI/CD for a Data Ingestion pipeline](https://docs.microsoft.com/azure/machine-learning/how-to-cicd-data-ingestion)
* [Continuous integration and delivery in Azure Data Factory](https://docs.microsoft.com/azure/data-factory/continuous-integration-deployment#overview)
* [Azure Databricks Extension](https://github.com/microsoft/azdo-databricks)

## Reflect

After completing this challenge, consider the following questions:

* In real life you have more environments in a chain (e.g. Dev-QA-UAT-PROD). How would you extend the CI/CD pipeline to deploy the data ingestion solution to all environments? Would you automatically do the test run of the data ingestion pipeline in the PROD environment? If so, then how?
* The ADF pipeline invokes a published ML pipeline by id. How would you pass the value of the ML pipeline id to the ADF, given that it changes every time when the ML pipeline is published and given that normally ADF and ML pipelines are maintained by separate teams?
* How could you speed up the CI/CD execution?
* How could you implement unit tests for the data preparation code?
* How would you configure CI/CD triggering on a change in the data preparation code and a change in the ADF pipeline?
