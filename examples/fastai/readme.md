# Training & deploying a FastAI model with Azure ML

This example will walk you through training, exporting, and deploying a FastAI model on Azure.

```cli
az ml model register -n pets-resnet34 -p fastaimodel.pkl
az ml model deploy -n myservice -m pets-resnet34:1 --ic inferenceconfig.json
```
