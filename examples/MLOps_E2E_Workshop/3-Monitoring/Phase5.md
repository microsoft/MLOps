# Phase 5: Log metrics and model evaluation  

Now that you've got familiar with training and registering the ML model with Azure Machine Learning pipelines, let's make it better by capturing a few important metrics during the model training and use it to evaluate the trained model before registering.


## Prerequisites

Complete all the tasks in **reproducible training** folder and phase 4. 

## Resources

* [Documentation - Monitor Azure ML experiment runs and metrics](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-track-experiments)
* [Documentation - What are Azure ML pipelines?](https://docs.microsoft.com/en-us/azure/machine-learning/concept-ml-pipelines#what-are-azure-ml-pipelines)


## Tasks

1. Agree on the important model metrics that will be used to evaluate the trained model ***(You can use the same AUC(Area Under ROC Curve) metrics which were initially made available from the experimentation notebook)***.
2. Start measuring and logging the important metrics within the model training step.
3. Confirm the captured metric are under a specific run in AML workspace.
4. Add the evaluation step before registering the model with Azure ML workspace. This evaluation step should check on the captured metrics and decide whether to register a model or not.

### Success Criteria

To successfully complete this task, you must: 

* Successfully measure and log metrics with Azure ML SDK.
* Successfully add an evaluation step before registering a trained ML model.


## Reflect

After completing this challenge, consider the following questions:

* What are the benefits of evaluating the trained Ml model?
