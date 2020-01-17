# Submitting a run using REST API

This example shows you how to submit a simple remote run using REST API

## Pre-requisites

 * You have owner permissions to Azure Subscription
 * You have created Azure Machine Learning Workspace
 * The workspace has Machine Learning Compute resource for the remote run.
 * You have local Python 3 with [requests](https://pypi.org/project/requests/) and [adal](https://pypi.org/project/adal/) packages installed.

## Authenticate against Azure

To perform REST call against Azure Machine Learning services, you need to obtain authentication token from Azure management service. To learn how to get an authentication token, use the information in the [Set up authentication for Azure Machine Learning resources and workflows](https://docs.microsoft.com/azure/machine-learning/how-to-setup-authentication) article.

## Create or get an experiment

Oncy you have obtained a token, you can use it to make authorized calls against Azure Machine Learning services. 

First, call run history service to create an experiment under which the run is submitted.

```python
header = {'Authorization': 'Bearer ' + token}

historybase = "history/v1.0/"
resourcebase = "subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/".format(subid,rg,ws)

experiment_name = "new_experiment"

create_experiment = hosturl + historybase + resourcebase + "experiments/{}".format(experiment_name)
resp = requests.post(create_experiment, headers=header)
print(resp.text)
```

You can also get an existing experiment

```python
get_experiment = hosturl + historybase + resourcebase + "experiments/{}".format(experiment_name)
resp = requests.get(get_experiment, headers=header)
print(resp.text)
```

## Prepare files for run

To submit a run, prepare two files: a zip folder that contains your training script, called project.zip, and definition.json file. Place these two files in the working directory of your local Python interpreter.

The project.zip should have following hello.py Python file at its root:

```python
# hello.py
print("Hello!")
```

Use following definition.json file:



```json
{
    "Configuration":{  
       "Script":"hello.py",
       "Arguments":[  
          "234"
       ],
       "SourceDirectoryDataStore":null,
       "Framework":"Python",
       "Communicator":"None",
       "Target":"cpu-cluster",
       "MaxRunDurationSeconds":1200,
       "NodeCount":1,
       "Environment":{  
          "Python":{  
             "InterpreterPath":"python",
             "UserManagedDependencies":false,
             "CondaDependencies":{  
                "name":"project_environment",
                "dependencies":[  
                   "python=3.6.2",
                   {  
                      "pip":[  
                         "azureml-defaults"
                      ]
                   }
                ]
             }
          },
          "Docker":{  
             "BaseImage":"mcr.microsoft.com/azureml/base:intelmpi2018.3-ubuntu16.04"
          }
      },
       "History":{  
          "OutputCollection":true
       }
    }
}
```

## Submit run

Submit a run by making a multi-part POST request against execution service with the 2 files from previous step

```python
executionbase = "execution/v1.0/"
resourcebase = "subscriptions/{}/resourceGroups/{}/providers/Microsoft.MachineLearningServices/workspaces/{}/".format(subid,rg,ws)

start_run = hosturl+ executionbase + resourcebase + "experiments/{}/startrun".format(experiment_name)

run_files = {"runDefinitionFile": ("definition.json", open("definition.json","rb")), "projectZipFile": ("project.zip", open("project.zip","rb"))}

resp = requests.post(start_run, files=run_files, headers=header)

print("response text: ", json.loads(resp.text))
```

## Monitor status of run

You can track the status of the run by polling the run history service.

```python
run_id = json.loads(resp.text)["runId"]

get_run = hosturl + historybase + resourcebase + "experiments/{}/runs/{}".format(experiment_name,run_id)

status = None

while status not in ["Completed", "Failed", "Cancelled"]:
    time.sleep(5)
    resp = requests.get(get_run, headers=header)
    status = json.loads(resp.text)["status"]
    print(status)
```
