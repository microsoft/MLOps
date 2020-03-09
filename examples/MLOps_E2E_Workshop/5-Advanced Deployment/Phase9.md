# Phase 9: Advanced: Canary deployment

In a production environment, you would want to deploy a new model with a sophisticated deployment strategy instead of a simple "recreate" approach. This will significantly reduce risks related to the deployment and increase the environment stability. In this challenge, we will deploy a scoring image with a ***Canary*** deployment strategy on a Kubernetes environment with Istio service mesh implementation.

## Prerequisites

Before starting this task, make sure you have the following prerequisite requirements:

* AML Workspace with a registered model
* Kubernetes (K8s) cluster with installed and configured Istio
* Kubectl with configured credentials for the Kubernetes cluster
* Container Registry to store scoring images

## Resources

* [Model deployment to AKS cluster with Canary deployment](https://github.com/microsoft/MLOpsPython/blob/master/docs/canary_ab_deployment.md)
* [Install and use Istio in Azure Kubernetes Service (AKS)](https://docs.microsoft.com/azure/aks/servicemesh-istio-install?pivots=client-operating-system-linux)
* [AML SDK. Image package](https://docs.microsoft.com/python/api/azureml-core/azureml.core.image?view=azure-ml-py)
* [Multi-stage pipelines user experience](https://docs.microsoft.com/azure/devops/pipelines/get-started/multi-stage-pipelines-experience?view=azure-devops)
* [Create and target an environment](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/environments?view=azure-devops)
* [Istio. Request Routing](https://istio.io/docs/tasks/traffic-management/request-routing/)
* [Istio. Automatic sidecar Injection](https://istio.io/docs/setup/additional-setup/sidecar-injection/#automatic-sidecar-injection)
* [Kiali. Service mesh observability](https://kiali.io)
* [Helm](https://helm.sh)

## Tasks

1. Setup a CI/CD solution deploying a scoring image to a Kubernetes cluster with Canary deployment strategy
2. Understand the % of traffic deployed to each model via the Azure DevOps pipeline and test via the scoring endpoint.

### Hints

* Follow the [Model deployment to AKS cluster with Canary deployment](https://github.com/microsoft/MLOpsPython/blob/master/docs/canary_ab_deployment.md) guide to complete the challenge
* For the purpose of this challenge, you can use a dummy scoring file so that you can easily identify a scoring image version by the response
* Create a namespace in a K8s cluster to deploy all K8s resources required for this challenge
* Make sure the K8s namespace is labeled with automatic sidecar injection
* Make sure the K8s cluster is configured with your container registry
* Use Helm to deploy all resources to a K8s cluster

### Success Criteria

To successfully complete this task, you must demonstrate: 

* An Azure DevOps pipeline deploying a scoring image to a K8s cluster
* Two scoring containers (old and new) working simultaneously on the K8s cluster
* One scoring endpoint routing user requests to the old and then new scoring containers according to the weights
* That the deploying pipeline updates the routing weights in multiple stages
* ***Stretch Goal***: That the canary deployment pipeline works with the actual safe driving scoring images from the previous challenges


## Reflect

After completing this challenge, consider performing the following activities:

* Analyze the service mesh behavior in the Kiali console
* Enable Istio resources to send direct requests to either old or new scoring containers. For example, depending on a keyword in the request header.
