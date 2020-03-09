# MLOps 

Welcome to this hands on MLOps lab!

DevOps (the combination of **Dev**elopment and **Op**eration**s**) is the union of people, process, and products to enable continuous delivery of value to our end users. Increasingly, organizations are embracing DevOps disciplines and best practices to increase efficiency and consistency in software releases.

The growth of software solutions that include a *machine learning* component has resulted in a increased need to integrate DevOps practices with traditional data science processes for data preparation and model training, taking into account some of the unique tools and techniques that are specific to the machine learning lifecycle. This machine learning-focused approach to DevOps is sometimes referred to as *MLOps*.  *MLOps* is sometimes associated with fundamental DevOps practices (like CI/CD) for only the machine learning code and models, while "DevOps for Data Science" includes a more holistic approach to the solution space including DevOps practices for the data used to train the models as well as observing and running those models at scale in production environments.

## Introduction

The challenges in this lab have been designed to reflect real-world issues often encountered by organizations as they try to take the results of data scientist's experimentation (often in the form of ad-hoc code in notebooks or unmanaged scripts) and integrate them into a repeatable, automatable continuous software release process.

In this lab, the machine learning model you will train and deploy is based on the  [*Porto Seguro’s Safe Driver Prediction* Kaggle competition](https://www.kaggle.com/c/porto-seguro-safe-driver-prediction) in which a model is trained to predict the likelihood of a driver making an insurance claim. Your team must take some initial experimentation code used by data scientists to train an validate a classification model for insurance claim prediction, and adapt it to work in a managed DevOps solution by:

- Adding centralized logging and versioning so that each run of the training code records training parameters and metrics that can be compared over time. This will enable data scientists to track the models performance when predicting insurance claims from the data that has been collected.
- Refactoring the code from cells in an interactive notebook into scripts that can be run consistently on multiple compute targets - enabling local testing with small data samples as well as large-scale processing using on-demand training clusters that can handle the large volume of insurance claim data that has been collected.
- Separating discrete machine learning tasks into a multi-step pipeline that can be automated. This will provide a consistent, repeatable process that can be used to update the insurance claim prediction model as new data is collected and deploy the trained model as a service that can be consumed by applications.
- Integrating the model training and deployment code into a managed DevOps solution, where *continuous integration* pipelines can be used to enforce source control, code quality policies, and other standards that help ensure code maintainability and release management.
- Adding data orchestration to the DevOps solution to ensure reliable, automated ingestion and preparation of the insurance claim data used to train and validate the model.
- Capturing telemetry to track model usage and performance, enabling you to monitor driver data and claim predictions.

## DevOps for Machine Learning Overview

The challenges your team will face when creating a Machine Learning DevOps solution the insurance claim prediction model are typical for most enterprise machine learning scenarios. The following image shows a typical pattern in which:

- Business goals drive the collection of data and experimentation with that data.
- The output of experimentation is typically some code in notebooks and scripts, that is refactored to create a *build pipeline* where source control and continuous integration enforce code management and unit testing.
- The managed code is used to run a *training pipeline* that trains and validates a model based on data that is prepared using a *data pipeline*.
- The trained model is packaged and deployed using a *release pipeline*, which publishes the model as either a *real-time* service for business apps to consume directly, or as a *batch scoring pipeline* that performs asynchronous inferencing for high volumes of data.
- Telemetry from the deployed model is captured and used to provide *observability* of key metrics, which can be used to drive further iterations of experimentation and model training.


As organizations follow this pattern, multiple roles may need to collaborate to drive the process. For example:

- **Data scientists** explore and experiment with data, often using ad-hoc scripts and notebooks without a formal code management process.
- **Data engineers** implement infrastructure for data storage, transfer, and transformation.
- **Software engineers** typically follow Agile and DevOps processes to manage model build, test, and deployment; and integration into applications.
- **IT operations specialists** monitor and manage the overall infrastructure, enforcing policies and resolving service interruptions.
- **Business stakeholders** define the overall goals for the solution, and are concerned with the value that the solution brings to the business.
- **Data end users** consume the deployed models; sometimes explicitly to perform analytics, but often transparently within a line-of-business application.

## MLOps in Azure

Microsoft Azure offers a platform with support for DevOps, machine learning, and other related workloads such as data storage and transformation. Specific Azure technologies you will use in this include:

- **Azure Machine Learning**: A cloud-based platform for creating and operating machine learning solutions, including:
    - Data ingestion and versioning.
    - Model training and validation.
    - Compute management for training and deployment.
    - Orchestration of machine learning tasks.
    - Deployment of predictive models as services.
    - Monitoring of machine learning models.
- **Azure DevOps**: A cloud-based solution for collaborative software development and release management, including:
    - Source control and versioning.
    - Build and release automation.
    - Tools for managing Agile development processes.
    - Automated testing.
- **Azure Data Factory**: A framework for scalable, automated management of data movement and transformation.
- **Azure Storage**: Cloud-based data storage.

## Assumptions and Prerequisites

The challenges in this lab assume that you have some existing experience of using Microsoft Azure. Experience of the following is not required, but will be highly beneficial:

- Training machine learning models using Python frameworks such as scikit-learn.
- Managing data, compute and model training experiments with Azure Machine Learning.
- Managing source control and software build/release pipelines with Azure DevOps.

