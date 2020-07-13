# AML COMPUTE REST API SAMPLE

This example shows you how to manage AML compute using REST API

## All Pre-requisites
 * You have owner permissions to Azure Subscription
 * You have created azure machine learning workspace
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

## Create/Update AML Compute

 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 - Need a existed Azure Virtual Network
 
 1. Set the basic config
 ``` python
# general config
subid = "<my-subscription-id>"
rg = "<my-workspace-resource-group>"
ws = "<my-workspace-name>"
api_version = "2019-06-01"
```

2. set the compute resource config.
```python
# location, ex: westus2, eastus
location = "<your workspace location>" 

 # compute target type ex: VirtualMachine  AmlCompute
compute_type = "<compute type>"

 # ex: Standard_D1, Standard_F64s_v2
vmSize = "<VmType>"

# ssh account and password for compute
admin_user_name= "<admin>" 
admin_user_passwd= "<nimda123@S>" 

# Dedicated or Low Priority
vmPriority = "<Dedicated>" 

# set basic node schedule policy
maxNodeCount = <maxNumber>
minNodeCount = <lowNumner>

# set node idle time tolerance, time format according to ISO8601
# 1 hour 30 minutes --> PT1H30M
# 5 minutes --> PT5M
# 2 hours --> PT2H
nodeIdleTimeBeforeScaleDown = "PT5M" #  set 5 minutes tolerance

# virtual network id you have created, 
# get more info: https://docs.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview
network_id = "<virtual network id>"

# subnet id of virtual network
subnet_id =  "<default>"
```
3. send request
```
body = {
          "location": location, 
          "properties": {
            "computeType": compute_type,
            "properties": {
              "vmSize": vmSize,
              "vmPriority": vmPriority,
              "scaleSettings": {
                "maxNodeCount": maxNodeCount,
                "minNodeCount": minNodeCount,
                "nodeIdleTimeBeforeScaleDown": nodeIdleTimeBeforeScaleDown
              }
            }
          },
          "userAccountCredentials":{
            "adminUserName": admin_user_name,
            "adminUserPassword": admin_user_passwd
          },
          "subnet":{
            "id":"/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}".format(subid, rg, network_id, subnet_id)
         }
        }

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
create_compute_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/computes/{}?api-version={}".format(subid, rg, ws, compute_name, api_verison)

resp = requests.put(create_compute_url, headers=header, json=body)
print resp.text
```


## Delete AML Compute
 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 - Need a existed AML compute

```python
subid =  "<my-subscription-id>" 
rg =  "<my-workspace-resource-group>" 
ws =  "<my-workspace-name>" 
api_version =  "2019-06-01"

# the compute name 
compute_name = "<to be delete compute name>"

# Action:  Delete or Detach
#'Delete': Delete the underlying compute from workspace
#'Detach': Detach the underlying compute from workspace
underlying_resource_action = "<Delete>"

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
delete_compute_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/computes/{}?api-version={}&underlyingResourceAction={}".format(subid, rg, ws, compute_name, api_verison, underlying_resource_action)

resp = requests.delete(delete_compute_url, headers=header)
print resp.text
```

## Get AML Compute
 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
 - Need a existed AML compute
```python
subid =  "<my-subscription-id>" 
rg =  "<my-workspace-resource-group>" 
ws =  "<my-workspace-name>" 
api_version =  "2019-06-01"

# the compute name 
compute_name = "<compute name>"

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
get_compute_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/computes/{}?api-version={}".format(subid, rg, ws, compute_name, api_verison)

resp = requests.get(get_compute_url, headers=header)
print resp.text
```

## List AML Compute By Worksapce
 - Need "token" from Authenticate against Azure
 - Need a existed AML workspace
```python
subid =  "<my-subscription-id>" 
rg =  "<my-workspace-resource-group>" 
ws =  "<my-workspace-name>" 
api_version =  "2019-06-01"

header = {'Authorization': 'Bearer ' + token, "Content-type": "application/json"}
list_compute_by_workspace_url = "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/computes?api-version={}".format(subid, rg, ws, api_verison)

resp = requests.get(list_compute_by_workspace_url , headers=header)
print resp.text
```

## Reference
[RestAPI Official Guide](https://docs.microsoft.com/en-us/rest/api/azureml/workspacesandcomputes/machinelearningcompute)
