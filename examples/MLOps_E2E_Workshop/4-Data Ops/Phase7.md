# Phase 7: Data Ops for ML: Data Ingestion & Pre-processing

The data is coming from various sources in a raw and unprepared shape. In most cases, before using the data for the model training or scoring purposes, it should be pre-processed, cleaned, transformed, and merged/split. In this challenge, we will build a data ingestion pipeline taking care of the data preparation for the model training.  

## Prerequisites

Before starting this challenge, make sure you have the following prerequisite requirements:

* Azure Storage Account with three blob containers for the input, training and testing data
* The source data file in the input data container
* Azure Data Factory (ADF) workspace
* Azure Databricks workspace
* Azure Machine Learning workspace with a training pipeline

Azure Data Factory workspace and Azure Databricks workspace should be provisioned with ***Infrastructure as Code*** (/environment_setup/iac-create-di-environment.yml) from the **Challenge07** folder of the OpenHack files. This pipeline definition requires two additional variables in the variable group: DATABRICKS_WS_NAME (Databricks workspace name) and DATA_FACTORY_NAME (ADF workspace name).

## Resources

* [Data Ingestion overview](https://dev.azure.com/csedevops/MLOps/_git/DataOps?path=%2FREADME.md&_a=preview)
* [Introduction to Azure Data Factory](https://docs.microsoft.com/en-us/azure/data-factory/v1/data-factory-introduction)
* [Azure Databricks Concepts](https://docs.microsoft.com/en-us/azure/databricks/getting-started/concepts#concepts)
* [Databricks File System](https://docs.databricks.com/data/databricks-file-system.html)
* [Run a Databricks notebook with the Databricks Notebook Activity in Azure Data Factory](https://docs.microsoft.com/en-us/azure/data-factory/transform-data-using-databricks-notebook)
* [Execute Azure Machine Learning pipelines in Azure Data Factory](https://docs.microsoft.com/en-us/azure/data-factory/transform-data-machine-learning-service)
* [Data Access in Azure Machine Learning](https://docs.microsoft.com/en-us/azure/machine-learning/concept-data)


## Tasks

1. Understand the various Data Ingestion options available with Azure services. Discuss Pros and Cons of the available options.
2. Implement a solution that automatically triggers a data ingestion pipeline to run a Python script when new data drops (i.e. file to a blob store). The Python script should perform the following tasks:
    * Process the data
    * Split the data into training and testing data. The training data is used my the Azure ML training pipeline. The testing data will be used for the final model evaluation which is out of the scope of this challenge
    * Output the data into different containers on the blob store
    * Invoke a model training pipeline

### Hints

* As a starting point, use the pre-baked ***ADF pipeline*** (/adf/arm-template) from the **Challenge07** folder of the OpenHack files. Import it in ADF workspace. The template contains some fake service connections which you will need to update to get it working.
* Use the ***Data preparation Python script*** (/dataingestion/data-prepare.py) as a Databricks notebook to transform and split the data.
* Mount the blob containers to the dbfs file system with ***mount-data-containers.py***(/adf/utils/notebooks/mount-data-containers.py). Run it manually on a Databricks cluster with hardcoded argument values. You only need to do this once for the lifetime of a workspace.

### Success Criteria

To successfully complete this task, you must: 

* Drop an input file (porto_seguro_safe_driver_prediction_test.csv) into the input blob container.
* Automatically start the execution of the ADF pipeline.
* Place the training and testing data files in the corresponding blob containers using the ADF pipeline.
* Automatically invoke the training AML pipeline consuming the training data.


## Reflect

After completing this challenge, consider the following questions:

* What is the benefit of using ADF as a data ingestion orchestrator?
* How could we implement the data ingestion without ADF using the Databricks cluster?
