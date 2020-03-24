# Set up your Continuous Deployment pipeline 

This repo contains sample deployment code and GitHub actions code (workflows file). The goal of this exercise is to take the newly registered model and scoring files from the build workflow and deploy the model as a webservice. The deploy.yml will trigger GitHub Actions when the Azure Function call the GitHub Actions API. The Azure Function will trigger when a new model is registered Go to the Azure Functions folder to set up a trigger to deploy models triggered by new model registrations. 
