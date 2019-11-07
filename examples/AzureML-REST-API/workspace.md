# AML Workspace REST API SAMPLE

This example shows you how to manage AML workspace using REST API

## All Pre-requisites
 - You have owner permissions to Azure Subscription
 - You have local Python 3 with [requests](https://pypi.org/project/requests/) and [adal](https://pypi.org/project/adal/) packages installed.
 - You have created Azure Application Insights
 -   You have created Azure KeyVault
 -   You have created Azure Storage Account
 -   You have created Azure Container Registry

### Obtain client ID and secret

To authenticate against Azure from REST client, you need to perform App Registration that creates a service principal that can access your workspace with client ID and client secret. 

#### Option 1: Use Portal

Go to [Azure Portal](portal.azure.com), and navigate to __Active Directory__ > __App Registration__. Select __+New registration__ and create new App Registration using default settings. Copy the Application (Client) ID to use in next step.

Then, navigate to the newly created App Registration, select __Certificates & secrets__ and create a new client secret. Copy the client secret to a safe location to use in next step.

Finally to grant , navigate to your Azure Machine Learning Workspace. Go to __Access control (IAM)__, select __Add a role assignment__ and add the App Registration (service principal) as Contributor to your workspace.

#### Option 2: Use Azure CLI

Alternatively, you can use following Azure CLI commands to create the service principal and obtain credentials, and assign the role to the workspace.

```azurecli
# Create the SP
az ad sp create-for-rbac --sdk-auth --name <my-sp-name>

Output:
{
	"clientId": "<my-client-id>",
	"clientSecret": "<my-clent-secret>",
	....
}
```


### Authenticate against Azure

To perform REST call against Azure Machine Learning services, you need to obtain authentication token from Azure management service. Fill the client id, secret, workspace information and your login name in the code below.

```python
import requests
import json
import time
from adal import AuthenticationContext

client_id = "<my-client-id>"
client_secret = "<my-clent-secret>"
user_nmae = "<my-user-name>"

subid = "<my-subscription-id>"
rg = "<my-workspace-resource-group>"

auth_context = AuthenticationContext("https://login.microsoftonline.com/{}.onmicrosoft.com".format(user_name))

resp = auth_context.acquire_token_with_client_credentials("https://management.azure.com/",client_id,client_secret)

token = resp["accessToken"]
```

## Create AML Workspace 


### option 1: using REST API
- Need "token" from Authenticate against Azure
- You have created Azure Application Insights
- You have created Azure KeyVault
- You have created Azure Storage Account
- You have created Azure Container Registry and [enable admin user](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-authentication#admin-account).

```python
container_registry_name = "<your azure container register>"
keyvault_name = "<your azure keyvault>"
application_insights_name = "<your application insight>"
storage_account_name = "<your storage account>"
location_of_workspace = "<region of workspace>"

container_registry_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.ContainerRegistry/registries/{}".format(subid, rg, container_registry_name)
keyvault_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.KeyVault/vaults/{}".format(subid, rg, keyvault_name)
application_insights_id = "/subscriptions/{}/resourceGroups/{}/providers/microsoft.insights/components/{}".format(subid, rg, application_insights_name)
storage_account_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}".format(subid, rg, storage_account_name)

body = {
         'location': location_of_workspace,
         "properties": {
            "friendlyName": freind_name,
            "description": description,
            "containerRegistry": container_registry_id,
            "keyVault": keyvault_id,
            "applicationInsights": application_insights_id,
            "storageAccount": storage_account_id,
         },
         "identity": {
             "type": "systemAssigned"
         },
       }

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
create_workerspace_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}?api-version={}".format(subid, rg, ws, api_verison)
resp = requests.put(create_workerspace_url, headers=header, json=body)
print(resp.__dict__)
```


#### Monitor status of run
You can track the status of create workspace progress

``` python
poll_status_url = resp.headers["Location"]

while True:
    time.sleep(5)
    status = requests.get(poll_status_url, headers=header)
    print(status.content)

```

### option 2: azure portal
It is the easiest way to create aml workspace through azure portal. Here is the [official guide](https://docs.microsoft.com/en-us/azure/machine-learning/service/how-to-manage-workspace).

## Get/Delete/List AML Workspace
 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 
``` python
subid = "<my-subscription-id>"
rg = "<my-workspace-resource-group>"
ws = "<my-workspace-name>"
api_version = "2019-06-01"

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"} # token from azure service principle authetication

get_workerspace_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}?api-version={}".format(subid, rg, ws, api_verison)

delete_workerspace_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}?api-version={}".format(subid, rg, ws, api_verison)

list_workerspace_url = "https://management.azure.com/subscriptions/{}/providers/Microsoft.MachineLearningServices/workspaces?api-version={}".format(subid, api_verison)


# get workspace
resp = requests.get(get_workerspace_url, headers=header)
print(resp.text)

# delete workspace
resp = requests.delete(delete_workerspace_url, headers=header)
print(resp.text)

# List workspace by subscription
resp = requests.get(list_workerspace_url, headers=header)
print(resp.text)
```
