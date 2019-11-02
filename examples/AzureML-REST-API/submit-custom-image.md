# Submitting a Run with a custom docker image

This example shows you

* How to submit a run with a custom docker image

## Pre-requisites

 * [Follow the getting started example](./rest-submit-run.md) to generate relevant data and to understand basic call patterns.


## Prepare files for run

To submit a run, prepare two files: a zip folder that contains your training script, called project.zip, and definition.json file. Place these two files in the working directory of your local Python interpreter.

The project.zip should have [this code_runner.py](./code_runner.py) Python file at its root.


Use the following definition.json file to submit a program that takes in a command line and executes it inside the custom image (note the "BaseImageRegistry" section below):

```json
{
    "Configuration":{
       "Script":"code_runner.py",
       "Arguments":[
          "/code/in_custom_image/custom_binary",
          "firstArg",
          "--secondArg",
          "Value"
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
                   "python=3.6.2"
                ]
             }
          },
          "Docker":{
             "BaseImage":"mycustomimage:1.0",
             "BaseImageRegistry":{
                "Address": "myregistry.azurecr.io",
                "Username": "username",
                "Password": "password"
             }
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
