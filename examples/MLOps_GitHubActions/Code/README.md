# MLOps
This exercise is designed to add a CI/CD process to an existing machine learning project. 

## Uploading Some Data
To get this to work we need some data. This can be done by downloading a zip file and uploading it to the storage attached to the Azure Machine Learning workspace. Make sure to follow the [instructions](docs/datastore.md) in order to set this up. 

## Set up your CI Actions
The goal behind the CI action is to create a process whereby every time code is changed in our repo, the machine learning pipeline is updated, run, and a model is created. The process is a bit involved but not impossible! Refer to [instructions](docs/build.md) 

## Set up your CD Actions
The deployment action is the delivery process of the CI/CD pipeline. It is often advantageous to seperate the two process in order to control how we deliver our machine learning model (i.e. one version might not work well so we want to avoid releasing it). Refer to [instructions](docs/release.md) 

## Tying it all together!
Now you should be able to make a change to the code and see all of the services work together to product a consumable endpoint which can be used in your software!
