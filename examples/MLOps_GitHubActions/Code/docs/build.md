# Set up your Continuous Integration pipeline 

This repo contains sample training code and GitHub actions code (workflows file). The goal of this exercise is to rebuild and run a Machine Learning pipeline (aka your training pipeline) every time code is changed in the repo. You can use the training files in the repo or add your own. Go through the files and fill inThe build.yml file in the workflows folder contains the logic and conditions for running the actions. 

# Steps

1. Go into pipeline.py and fill in the variables to connect to your Azure Machine Learning resources under the **manage endpoint** section.

2. Move the the workflows folder to the root of the repository or create your own workflow through the **Actions** tab.

3. This build.yml will only trigger GitHub Actions when on the python files changes. To learn more about setting conditions on workflow refer [GitHub Actions documentation](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions)

4. Try it out! Go in and change on of the python files and check out the Actions tab to see the workflow run.
