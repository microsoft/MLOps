+++
title = "End-to-End Pipeline Example on Azure"
description = "An end-to-end guide to creating a pipeline in Azure that can train, register, and deploy an ML model that can recognize the difference between tacos and burritos"
weight = 50
+++
## Introductions
### Overview of Azure and AKS

Microsoft Azure is an open, flexible, enterprise-grade cloud computing platform running on Microsoft infrastructure. The platform has various services, many of which are extremely useful in a pipeline that works with ML models. 

The [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest) is a set of tools that you can use to interact with Azure from the command line.

Azure Kubernetes Service (AKS) on Azure allows you to deploy containerized applications, within which you describe the resources your application needs, and AKS will manage the underlying resources automatically. This workflow is especially efficient at scale.
### The overall workflow
This guide takes you through using your Kubeflow deployment to build a machine learning (ML) pipeline on Azure. This guide uses a sample pipeline to detail the process of creating an ML workflow from scratch. This guide allows you to create and run a pipeline that processes data, trains a model, and then registers and deploys that model as a webservice. 

 To build your pipeline, you must create and build containers using Docker images. Containers are used to abstract the dependencies for each step of the pipeline. You can manage your containers using [Azure's portal](https://ms.portal.azure.com/#home), specifically using the Container Registry to store the containers in the cloud. Kubelfow pulls the containers from this registry as they are needed in each step of the pipeline.

By following this guide, you will be able to:

- Set up Kubeflow in an AKS Cluster
- Create and compile a pipeline that can:
	- Preprocess data
	- Train a model
	- Register the model to ACR ([Azure Container Registry](https://docs.microsoft.com/en-us/azure/devops/pipelines/languages/acr-template?view=azure-devops))
	- Profile the model to optimize compute resources in AML (Azure Machine Learning)
	- Deploy the model to AML
- Interact with and customize your deployment
- Test and use your deployed model

When your pipeline has finished running, you will be able to see a registered image, model, and deployment in your Azure ML workspace. You will then be able to visit the scoring URI and upload images for scoring in real time.

## Set up your environment
### Download the project files
This tutorial uses the Azure Pipelines example in the Kubeflow examples repo. You can optionally use a pipeline of your own, but several key steps may differ.

Clone the project files and go to the directory containing the [Azure Pipelines (Tacos and Burritos)](https://github.com/kubeflow/examples/tree/master/pipelines) example:
```
git clone https://github.com/kubeflow/examples.git
cd examples/pipelines/azurepipeline
```
As an alternative to cloning, you can download the [Kubeflow examples repository zip file](https://github.com/kubeflow/examples/archive/master.zip).
## Deploy Kubeflow
If you don't already have one, create an Azure account. If you have not used Azure services before, you can recieve up to [1 year of free services and free credits.](https://azure.microsoft.com/en-ca/free/)

> Note: that some of the services used in this guide may not be included in the free services, but can be covered by free credits. 

First, install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest), then follow the instructions in the [guide to deploying Kubeflow on Azure](https://www.kubeflow.org/docs/azure/deploy/install-kubeflow/). 

> Ensure that the agent size you use has the proper memory and storage requirements. For the Azure Pipelines example, **56 GiB** of memory are needed and **premium storage** must be available. Use [this guide](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/sizes) to choose the right agent size for your deployment. (We chose an agent size of Standard_DS13_v2.)

## Configuring Azure resources
### Create an ML workspace in Azure
Throughout your pipeline's run, all of your models, images, and deployments will be pushed to your ML workspace in Azure. Your ML workspace also has support for managing your active deployments, which will be displayed later in this tutorial.

To create an ML workspace:

1. Go to [the Azure portal](portal.azure.com) and click on your resource group. 
2. Select the **add a new resource** option. 
3. Search for **Machine Learning Studio Workspace** and use the default options, taking note of the name you decide for it. 

<img src="/docs/azure/images/creatingWS.PNG" 
    alt="Creating a Workspace"
    class="mt-3 mb-3 p-3 border border-info rounded">

### Create an Azure container registry
Kubeflow uses Docker images to describe each pipeline step's dependencies. You need to create a container registry to store those images in the cloud so that Kubeflow can pull the images as they are needed.

To create a container registry:

1. Go to [the Azure portal](portal.azure.com) and click on your resource group. 
2. From there, select the **add a new resource** option. 
3. Search for **Container Registry** and add it to your resource group.
4. Configure your registry by selecting and noting the name you use for it. Enable an **admin user**, and change the SKU option to **Premium**. 

<img src="/docs/azure/images/createContainerReg.PNG" 
    alt="Creating a Container Registry"
    class="mt-3 mb-3 p-3 border border-info rounded">

### Create a persistent volume claim (PVC)
A persistent volume claim is a dynamically provisioned storage resource attached to a Kubernetes cluster. It is used in the pipeline to store data and files across pipeline steps. 

Using a bash shell, navigate to the `azurepipeline` directory. Use the following commands to create a persistent volume claim for your cluster.
```
cd kubernetes
kubectl apply -f pvc.yaml
```

## Authenticate your service principal
A service principal is used to allow your pipeline to securely interface with your Azure services without having to directly login in the pipeline and use admin privileges. To create a service principal with Contributor access to your Azure account, use the following steps.
### Create an App Registration
To create an app registration:

1. In the Azure Portal, navigate to [**Azure Active Directory**](https://ms.portal.azure.com/#blade/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/Overview). 
2. Select **App registrations** and click **New registration**. Name it, noting the name and use the default options. 
3. Click **Register**. <img src="/docs/azure/images/appReg.PNG" 
    alt="Creating a App Registration"
    class="mt-3 mb-3 p-3 border border-info rounded">

4. You should be redirected to your app registration’s dashboard. Select **Overview** from the sidebar. 
5. Make note of the **Application (client) ID** and the **Directory (tenant) ID**. The client ID is your service principal username. Save these in a secure location. <img src="/docs/azure/images/clientID2.PNG" 
    alt="Client ID location"
    class="mt-3 mb-3 p-3 border border-info rounded">

6. Select **Certificates and Secrets** from the sidebar. 
7. Select **New client secret**. Give the client secret a description and select how long you would like it to remain active for. Once you click the **Add** button, make sure you take note of the client secret value and save it in a secure place. This is your service principal password. <img src="/docs/azure/images/password.PNG" 
    alt="Client secret location"
    class="mt-3 mb-3 p-3 border border-info rounded">

### Add a role assignment
To add a role assignment for your service principal:

1. Go to your resource group page on the Azure Portal. 
2. Select **Access control (IAM)** from the sidebar. Select **Add a role assignment**. 
3. Set the role to **Contributor** and search for the name you gave your app registration in the **Select** dropdown. 
4. Click **Save**. 

<img src="/docs/azure/images/roleAssign.PNG" 
    alt="Creating a Role Assignment"
    class="mt-3 mb-3 p-3 border border-info rounded">

## Creating containers from Docker images
### Install Docker
You need to install Docker to be able to push and pull images to/from your Container registry.

For Windows and WSL: [Guide](https://nickjanetakis.com/blog/setting-up-docker-for-windows-and-wsl-to-work-flawlessly)

For other OS: [Docker Desktop](https://hub.docker.com/?overlay=onboarding)

### Build images
To deploy your code to Kubernetes, you must build your local project’s Docker images and push the containers to your Container Registry so that they are available in the cloud. 

1. Set the path in Container Registry that you want to push the containers to:
`export REGISTRY_PATH=<REGISTRY_NAME>.azurecr.io`

2. Run the following command to authenticate your Container Registry: 
`az acr login --name <REGISTRY_NAME>`

3. Create a version, to be associated with your model each time it runs (change this accordingly): `export VERSION_TAG=1`

Each docker image will be built and uploaded to the cloud using the Container Registry. 

>Note: If you would like to test a container locally, you can use the `docker run -it ${REGISTRY_PATH}<CONTAINER NAME>:$(VERSION_TAG}` before pushing to Container Registry. 
	
	//Starting in the 'code' directory of the azurepipeline folder

	cd preprocess
	docker build . -t ${REGISTRY_PATH}/preprocess:${VERSION_TAG}
	docker push ${REGISTRY_PATH}/preprocess:${VERSION_TAG}

	cd ../training
	docker build . -t ${REGISTRY_PATH}/training:${VERSION_TAG}
	docker push ${REGISTRY_PATH}/training:${VERSION_TAG}

	cd ../register
	docker build . -t ${REGISTRY_PATH}/register:${VERSION_TAG}
	docker push ${REGISTRY_PATH}/register:${VERSION_TAG}

	cd ../profile
	docker build . -t ${REGISTRY_PATH}/profile:${VERSION_TAG}
	docker push ${REGISTRY_PATH}/profile:${VERSION_TAG}

	cd ../deploy
	docker build . -t ${REGISTRY_PATH}/deploy:${VERSION_TAG}
	docker push ${REGISTRY_PATH}/deploy:${VERSION_TAG}

When all of the images are pushed successfully, modify the `pipeline.py` file to use the appropriate image for each pipeline step.

## Running and deploying your pipeline
### Compile
To compile the pipeline, simply open a terminal and navigate to the azurepipeline/code folder. Run the following command to generate a pipeline in the tar.gz format:		
		`python pipeline.py`
### Run and deploy
Upload the pipeline.tar.gz file to the pipelines dashboard on your Kubeflow deployment.

<img src="/docs/azure/images/pipelinedash.PNG" 
    alt="Pipeline Dashboard"
    class="mt-3 mb-3 p-3 border border-info rounded">
 
 Create an experiment and then create a run using the pipeline you just uploaded. 

 <img src="/docs/azure/images/pipelinesInput.png" 
    alt="Pipelines input example"
    class="mt-3 mb-3 p-3 border border-info rounded">

 The finished pipeline should have five completed steps.

 <img src="/docs/azure/images/finishedRunning.PNG" 
    alt="Finished Pipeline"
    class="mt-3 mb-3 p-3 border border-info rounded">

### Pushing images for scoring
Once your pipeline has finished successfully, you can visit the Azure portal to find your deployment url. Go to your ML workspace dashboard and select “Deployments” from the sidebar. Click on the most recent deployment. You should see a link under “Scoring URI”. You can whatever method you know best to send a GET/POST request with an image of a taco or a burrito to this url and it should return whether or not the image is of a taco or a burrito. 

The easiest method is to find a url of an image of a taco or a burrito and append it to your scoring url as follows: `<scoring_url>?image=<image_url>`

<img src="/docs/azure/images/finalOutput.PNG" 
    alt="Final ML model deployment"
    class="mt-3 mb-3 p-3 border border-info rounded">

## Clean up your Azure environment
When you are done, make sure you delete your resource group to avoid extra charges.

	az group delete -n MyResourceGroup
You can optionally choose to delete individual resources on your clusters using the [Azure cluster docs](https://docs.microsoft.com/en-us/azure/service-fabric/service-fabric-tutorial-delete-cluster).

## Next steps
Build your own pipeline using the [Kubeflow Pipelines SDK](/docs/pipelines/sdk/sdk-overview/).