# Transfer Learning with Azure ML & MLOps

1. Create a training pipeline with Azure ML.
2. Publish this pipeline so it can be used to control and automate the training process - including retraining later on.
3. Use Azure DevOps to automate the release of your model once it is ready for E2E deployment.

# Files in this repo
- mlpipeline.py (sets up and publishes a reusable ML pipeline)
- train.py (standard mobilenet/imagenet script)
- register.py (registers the model with the ML service)
- infenv.yml (serialized conda file used for deployment)
- score.py (entry script provided to Azure ML)
- inferenceConfig.json (config needed to package ML model)
- deploymentConfig.json (config needed to deploy ML model)
