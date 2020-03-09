# Phase 3: Orchestrate ML Operationalization with a Pipeline

In Phase 2, you transformed the experimental notebook produced by the data science team into a script that can be managed and run independently of the notebook. You used the script to train the model, then you used code in the notebook to register the model that the script produced.

In this phase, you'll encapsulate both of these tasks into an Azure ML pipeline that breaks the tasks down into a sequence of steps that can be run on-demand or automatically. Running these training steps with a full set of data can take a very long time on a typical workstation, but you don't want to invest in expensive hardware that will only be used periodically. To resolve this, your pipeline will be configured to run on an Azure Machine Learning cluster that is provisioned and scaled automatically when needed.

You'll also write code to retrieve the registered model, and deploy it as a real-time inferencing service so it can be consumed by an insurance application approval application.

## Prerequisites 

* Basic understanding of Azure ML pipelines
* Completion of phase 1 and 2

## Resources

* [Notebook: Creating an Azure Machine Learning Pipeline](https://github.com/MicrosoftDocs/mslearn-aml-labs/blob/master/05-Creating_a_Pipeline.ipynb)
* [Notebook: Creating a Real-Time Inferencing Service](https://github.com/MicrosoftDocs/mslearn-aml-labs/blob/master/06-Deploying_a_model.ipynb)
* [Documentation - What are Azure Machine Learning pipelines?](https://docs.microsoft.com/azure/machine-learning/concept-ml-pipelines)
* [Documentation - How to create your first Azure ML Pipeline](https://docs.microsoft.com/azure/machine-learning/how-to-create-your-first-pipeline)
* [Documentation - How to debug and troubleshoot machine learning pipelines](https://docs.microsoft.com/azure/machine-learning/how-to-debug-pipelines)
* [Documentation - Data access in Azure Machine Learning](https://docs.microsoft.com/azure/machine-learning/concept-data)
* [Documentation - What are compute targets in Azure Machine Learning?](https://docs.microsoft.com/azure/machine-learning/concept-compute-target)
* [Documentation - How to deploy models with Azure Machine Learning](https://docs.microsoft.com/azure/machine-learning/how-to-deploy-and-where)
* [*Microsoft Learn* module - Deploying machine learning models with Azure Machine Learning](https://docs.microsoft.com/learn/modules/register-and-deploy-model-with-amls/index)


## Task

Create a new notebook and write code to complete the following tasks:

1. Create an Azure ML pipeline that contains the following steps:

    * Train the model using an Estimator
    * Register the model with the name **lgbm_binary_model.pkl** using a Python script

    The pipeline should run on a training cluster compute target in your Azure Machine Learning workspace.
2. Run code in a notebook to retrieve the registered model and deploy it as an inferencing service to an Azure Container Instance.
3. Test the deployed service by submitting a REST request to its endpoint. Use the following test data in numpy array format. This represents details for two drivers, for which your service should predict the likelihood of an insurance claim.

    ```Python
    [[0,1,8,1,0,0,1,0,0,0,0,0,0,0,12,1,0,0,0.5,0.3,0.610327781,7,1,-1,0,-1,1,1,1,2,1,65,1,0.316227766,0.669556409,0.352136337,3.464101615,0.1,0.8,0.6,1,1,6,3,6,2,9,1,1,1,12,0,1,1,0,0,1],
    [4,2,5,1,0,0,0,0,1,0,0,0,0,0,5,1,0,0,0.9,0.5,0.771362431,4,1,-1,0,0,11,1,1,0,1,103,1,0.316227766,0.60632002,0.358329457,2.828427125,0.4,0.5,0.4,3,3,8,4,10,2,7,2,0,3,10,0,0,1,1,0,1]]
    ```

### Hints

* Use the [Creating an Azure Machine Learning Pipeline](https://github.com/MicrosoftDocs/mslearn-aml-labs/blob/master/05-Creating_a_Pipeline.ipynb) notebook as a starting point for the code to create and publish your pipeline. You should adapt the code in this sample notebook to:
    * Create and register a **Dataset** for the driver insurance training data so that your training script can read it from a central **Datastore** in the workspace, regardless of the compute target on which it is run.
    * Create an Azure Machine Learning compute target on which to run the pipeline and its steps. To avoid automatic scale down of AML managed compute, edit training compute and set **Idle seconds before scale down** to 1800 or more. This can save time between pipeline runs if you are frequently debugging AML pipelines.
    * Use a **PipelineData** object to pass the *output* of the training step (the trained model) to the *input* of the model registration step. This creates a dependency between the steps. In addition to defining *inputs* and *outputs* for the steps, both scripts will require a *argument* for this object to define the virtual path to the folder where the model file will be saved by the first step (previously this was hard-coded to the run's **output** folder) and loaded by the second step.
    * Define the steps for your pipeline - these should be an **EstimatorStep** for the training script, and a **PythonScriptStep** for the model registration step.
    * Run the pipeline and verify that it has trained and registered the model.
    * Publish the pipeline and initiate it from its endpoint.
* Use the [Creating a Real-Time Inferencing Service](https://github.com/MicrosoftDocs/mslearn-aml-labs/blob/master/06-Deploying_a_model.ipynb) notebook as a starting point for the code to deploy the model that was trained by your pipeline. You should adapt the code in this sample notebook to:
    * Retrieve the most recent version of the registered insurance claim prediction model.
    * Use the *scoring script* provided in the **Challenge03** folder of the OpenHack files. This includes an **init** function that loads the registered model, and a **run** function that uses it to predict claim classifications for new driver data.
    * Create a *Conda dependencies* file that includes the Python packages required by your scoring script.
    * Deploy the insurance claim prediction model as an Azure Container Instance (ACI) service, with the scoring script and conda dependencies you defined.
    * Test the deployed service by submitting sample driver data to its endpoint and reviewing the predictions it returns.
    * Check for the Azure Container Instance's container logs if service deployment takes longer than expected.

### Success Criteria

To successfully complete this task, you must: 

* Successfully run your Azure ML pipeline by initiating it from its endpoint.
* Successfully deploy the trained model as a service and test its endpoint.


## Reflect

* What are the benefits of splitting the ML process into steps?
* What are the benefits of publishing an Azure ML pipeline as a REST service?
* What other steps might you include in the training pipeline?
