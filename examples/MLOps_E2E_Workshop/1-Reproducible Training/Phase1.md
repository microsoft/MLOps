# Phase 1: Create your Development Environment

As is common in many machine learning scenarios, the data science team in your organization has experimented with the *safe driver prediction* data, and produced a Jupyter notebook that trains a model and evaluates its predictive performance. Your team needs to first understand and reproduce how the notebook code solves the business problem.

To do this, you'll create an Azure Machine Learning workspace where you can manage all of the code and data assets centrally, and create a *compute instance* that you can use as a  cloud workstation to run the notebook code.

## Prerequisites

Before starting this challenge, ensure you have the following prerequisite requirements in place:

* A Microsoft Azure subscription.
* The datasets for this exercise (they are in this Git repository)

### Resources

Throughout the challenge use the references below for guidance

* [What is an Azure Machine Learning workspace?](https://docs.microsoft.com/azure/machine-learning/concept-workspace)
* [What is an Azure Machine Learning compute instance?](https://docs.microsoft.com/azure/machine-learning/concept-compute-instance)
* [Basic vs. Enterprise version of Azure Machine Learning Workspace](https://docs.microsoft.com/en-us/azure/machine-learning/overview-what-is-azure-ml#sku)


## Task

1. Create a **Machine Learning** resource in your Azure subscription. This will create an Azure Machine Learning *workspace* and some related resources.
    * After creating your workspace in the [Azure portal](https://portal.azure.com), use the web-based [Azure Machine Learning studio](https://ml.azure.com) interface to work with it.
2. In your workspace, create a **Compute Instance** and wait for it to start.
3. Open the ***Jupyter*** environment link for your compute instance.
    * If you have not worked with Jupyter before, have a look at [Jupyter Notebook for Beginners: A Tutorial](https://www.dataquest.io/blog/jupyter-notebook-tutorial/).
4. Download and extract all the files in the repository to your local machine.
5. In the Jupyter web interface for your compute instance, open the **Users** folder and upload the following files in the following structure:

    * porto_seguro_safe_driver_prediction_LGBM.ipynb
    * data
        * porto_seguro_safe_driver_prediction_train.csv

6. In Jupyter, open the **porto-seguro-safe-driver-prediction-LGBM.ipynb** notebook, and run the code it contains to train and validate the insurance claim classification model created by the data science team.

### Success Criteria

To successfully complete this task, you must: 

* Provision an Azure Machine Learning workspace and compute instance.
* Run the experimentation notebook in your Azure Machine Learning compute instance (which should produce a .pkl file containing the trained model).


## Reflect

After completing this challenge, consider the following questions:

* What benefits and challenges can you see in using an Azure Machine Learning workspace as a central place for data scientists and developers to collaborate on machine learning code?
* What benefits and challenges can you see in using Jupyter Notebooks as a development interface for model training code - particularly in respect to automating training processes?
