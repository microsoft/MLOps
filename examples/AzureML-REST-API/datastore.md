# AML DATASTORE REST API SAMPLE

This example shows you how to manage AML datastore using REST API.

## All Pre-requisites
 * You have owner permissions to Azure Subscription
 * You have created azure machine learning workspace
 * You have created a azure storage account
 * You have local Python 3 with [requests](https://pypi.org/project/requests/) and [adal](https://pypi.org/project/adal/) packages installed.

###  Obtain client ID and secret

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

## Register datastore to an AML workspace

 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 - [Detail Document](https://review.docs.microsoft.com/en-us/rest/api/machinelearningservices/data/create/create).
 ``` python
# general config
subid = "<subscription-id>"
rg = "<workspace-resource-group>"
ws = "<workspace-name>"
```

Next section will show how to register a existed **azure blob** container to AML workspace as a datastore.
```python
datastore_name = "<datastore name>"

# such as AzureBlob,AzureFile, AzureDataLake, 
# get more info: https://review.docs.microsoft.com/en-us/rest/api/machinelearningservices/data/create/create#datastoretype
datastore_type = "AzureBlob" 

# this section is an existed azure blob config section
storage_account = "<storage account>" 
container_name = "<container name>"
subid_of_storage_account = "<subscription id of storage account >"
resource_group_of_storage_account = "<resource group id of storage account>"
location_of_aml_workspace = "<location>" # location of aml workspace
# different storage type has different credential requirement
# get more info: https://review.docs.microsoft.com/en-us/rest/api/machinelearningservices/data/create/create#azurestoragecredentialtypes
credential_type =  "AccountKey"
credential = "<storage account key>"

body = {
   "name": datastore_name,
   "dataStoreType": datastore_type,
   "azureStorageSection":{
      "accountName": storage_account,
      "containerName": container_name,
      "credentialType": credential_type,
      "credential": credential,
      "subscriptionId": subid_of_storage_account,
      "resourceGroup": resource_group_of_storage_account,
   }
}

# Here is two optional parameters.
create_if_not_exists = "false" # default is false
skip_validation = "false" # default is false
```
Send request.
```
header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
create_datastore_url = "https://{}.experiments.azureml.net/datastore/v1.0/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/datastores?createIfNotExists={}&skipValidation={}".format(location_of_aml_workspace, subid, rg, ws, create_if_not_exists, skip_validation)
resp = requests.post(create_datastore_url, headers=header, json=body)

print resp.text
```

## Get AML datastore from AML worksapce
 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 - Need a registered AML datastore
```python
subid =  "<subscription-id>" 
rg =  "<workspace-resource-group>" 
ws =  "<workspace-name>" 

datastore_name = "<datastore name>"
location_of_aml_workspace = "<location of aml workspace>"

get_datastore_url = "https://{}.experiments.azureml.net/datastore/v1.0/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/datastores/{}".format(location_of_aml_workspace, subid, rg, ws, datastore_name)
resp = requests.get(get_datastore_url, headers=header)

print resp.text
```


## Unregister AML datastore from AML worksapce
 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 - Need a registered AML datastore



Unregistering a datastore from AML workspace is not equal to deleting it, after unregistering done, storage account and data are still exist.
```python
subid = "<subscription-id>" 
rg = "<workspace-resource-group>" 
ws = "<workspace-name>" 

datastore_name = "<datastore name>"
location_of_aml_workspace = "<location of aml workspace>"

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
delete_datastore_url = "https://{}.experiments.azureml.net/datastore/v1.0/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/datastores/{}".format(location_of_aml_workspace, subid, rg, ws, datastore_name)
resp = requests.delete(delete_datastore_url, headers=header)

print resp.text
```
