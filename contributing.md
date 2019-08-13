# Adding Community Contributions to the MLOps Repo

- Each new project/contribution should get its own folder. Each folder is self-contained in terms of dependencies. 
- Each folder must have a README file. Examples can be included by creating a subfolder in the ‘examples’ folder or embedding a submodule in the ‘examples’ folder.
- Your subfolder should follow the standardized folder structure format  to store code, data and configuration files.  

# Standardized Folder Structure
- README.md  
- notebook.ipynb (if notebook walkthrough is present)
- code/* 
- data/*  
- configuration/*
- docs/*
- .pipelines/* 

# Setting up automation around community contributions
**This repo is not guaranteed to contain validated samples with CI/CD.** 
We will be enabling validation gauntlets on PRs into this repo going forward.
This will require your PR to update the azure-pipelines.yml file at the root of the repository.
