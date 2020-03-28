# Azure DevOps Configuration

To get started:

* Create a new service connection in Azure DevOps of the Azure Resources Manager connection type. Azure DevOps will authenticate with this connection to make deployments to your Azure Subscription.
* In deploy-infra.yml replace <your-serviceconnection> with your created service connection name.
* Adapt globally unique resource names in the ARM parameter files e.g. storage account names to preferred resource names. Note that the workspace and workspace compute resources are updated as well once you update the individual parameter files.
