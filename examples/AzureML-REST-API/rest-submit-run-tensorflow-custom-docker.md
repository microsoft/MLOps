# Submitting a run using REST API

This example shows you how to submit a simple tesndsorflow mnist job run using REST API with custom Docker.

## Pre-requisites

 * You have owner permissions to Azure Subscription
 * You have created Azure Machine Learning Workspace
 * The workspace has Machine Learning Compute resource for the remote run.
 * You have local Python 3 with [requests](https://pypi.org/project/requests/) and [adal](https://pypi.org/project/adal/) packages installed.

## Obtain client ID and secret

To authenticate against Azure from REST client, you need to perform App Registration that creates a service principal that can access your workspace with client ID and client secret. Go to [Azure Portal](portal.azure.com), and navigate to __Active Directory__ > __App Registration__. Select __+New registration__ and create new App Registration using default settings. Copy the Apllication (Client) ID.

Then, navigate to the newly created App Registration, select __Certificates & secrets__ and create a new client secret. Copy the client secret to a safe location.

Finally to grant , navigate to your Azure Machine Learning Workspace. Go to __Access control (IAM)__, select __Add a role assignment__ and add the App Registration (service principal) as Contributor to your workspace.

## Authenticate against Azure

To perform REST call against Azure Machine Learning services, you need to obtain authentication token from Azure management service. Fill the client id, secret, workspace information and your login name in the code below.

```python
import requests
import json
import time
from adal import AuthenticationContext

client_id = "<my-client-id>"
client_secret = "<my-clent-secret>"

region = "<my-workspace-region>"
subid = "<my-subscription-id>"
ws = "<my-workspace-name>"
rg = "<my-workspace-resource-group>"

hosturl = "https://{}.api.azureml.ms/".format(region)

auth_context = AuthenticationContext("https://login.microsoftonline.com/<my-user-name>.onmicrosoft.com")

resp = auth_context.acquire_token_with_client_credentials("https://management.azure.com/",client_id,client_secret)

token = resp["accessToken"]
```

## Create or get an experiment

Next step is to call run history service to create an experiment under which the run is submitted.

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

The project.zip should have following tf_mnist_train.py Python file at its root:

```python
# tf_mnist_train.py

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
# Load MNIST Data
from tensorflow.examples.tutorials.mnist import input_data
import os
import argparse

from azureml.core.run import Run

# the following 10 lines can be removed once BUG# 241943 is fixed


def get_logger():
    try:
        return Run.get_context()
    except Exception:
        return LocalLogger()


class LocalLogger:
    def log(self, key, value):
        printss("AML-Log:", key, value)


def build_model(x, y_, keep_prob):
    def weight_variable(shape):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def bias_variable(shape):
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)

    def conv2d(x, W):
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def max_pool_2x2(x):
        return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

    W_conv1 = weight_variable([5, 5, 1, 32])
    b_conv1 = bias_variable([32])

    x_image = tf.reshape(x, [-1, 28, 28, 1])

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
    h_pool1 = max_pool_2x2(h_conv1)

    W_conv2 = weight_variable([5, 5, 32, 64])
    b_conv2 = bias_variable([64])

    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2)

    W_fc1 = weight_variable([7 * 7 * 64, 1024])
    b_fc1 = bias_variable([1024])

    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

    W_fc2 = weight_variable([1024, 10])
    b_fc2 = bias_variable([10])

    y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2

    return y_conv


def main():
    # Get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--learning_rate', type=float,
                        default=0.0001, help='learning rate')
    parser.add_argument('--minibatch_size', type=int,
                        default=50, help='minibatch size')
    parser.add_argument('--keep_probability', type=float,
                        default=0.5, help='keep probability for dropout layer')
    parser.add_argument('--num_iterations', type=int,
                        default=1000, help='number of iterations')
    parser.add_argument('--output_dir', type=str, default='./outputs',
                        help='output directory to write checkpoints to')

    args = parser.parse_args()

    # log parameters
    run_logger = get_logger()
    run_logger.log("learning_rate", args.learning_rate)
    run_logger.log("minibatch_size", args.minibatch_size)
    run_logger.log("keep_probability", args.keep_probability)
    run_logger.log("num_iterations", args.num_iterations)

    # Load MNIST data
    mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

    sess = tf.InteractiveSession()

    x = tf.placeholder(tf.float32, shape=[None, 784])
    y_ = tf.placeholder(tf.float32, shape=[None, 10])
    keep_prob = tf.placeholder(tf.float32)

    y_conv = build_model(x, y_, keep_prob)

    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))

    train_step = tf.train.AdamOptimizer(
        args.learning_rate).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))

    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    sess.run(tf.global_variables_initializer())

    for i in range(args.num_iterations):
        batch = mnist.train.next_batch(args.minibatch_size)
        if i % 100 == 0:
            test_acc = accuracy.eval(
                feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})
            train_accuracy = accuracy.eval(
                feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
            print("step %d, training accuracy %g, test accuracy, %g" %
                  (i, train_accuracy, test_acc))

            # log test accuracy to AML
            run_logger.log("Accuracy", float(test_acc))
            run_logger.log("Iterations", i)

        sess.run(train_step, feed_dict={
                 x: batch[0], y_: batch[1], keep_prob: args.keep_probability})

    # Save the trained model
    model_dir = args.output_dir
    model_file = 'model.ckpt'

    os.makedirs(model_dir, exist_ok=True)

    saver = tf.train.Saver()
    saver.save(sess, os.path.join(model_dir, model_file))

    final_test_acc = sess.run(accuracy, feed_dict={
                              x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0})
    run_logger.log("Accuracy", float(final_test_acc))
    run_logger.log("Iterations", args.num_iterations)
    print("test accuracy %g" % final_test_acc)


if __name__ == "__main__":
    main()

```

Use following definition.json file:



```json
{
	"configuration": {
        "script": "project/tf_mnist_train.py",
        "arguments": [
            "--minibatch_size",
            "64",
            "--learning_rate",
            "0.001",
            "--keep_probability",
			"0.5",
            "--output_dir",
            "outputs",
            "--num_iterations",
            "1000"],
        "framework": "Python",
        "communicator": "None",
        "target": "testCompute",
        "maxRunDurationSeconds": null,
        "nodeCount": 1,
        "environment": {
            "python": {
                "interpreterPath": "python",
                "userManagedDependencies": true,
                "condaDependencies": {
                    "name": "project_environment",
                    "dependencies": ["python=3.6.2", {
                            "pip": ["azureml-defaults"]
                        }]
                }
            },
            "environmentVariables": {
                "EXAMPLE_ENV_VAR": "EXAMPLE_VALUE"
            },
            "docker": {
                "baseImage": "tensorflow:1.13-cpu",
                "baseDockerfile": null,
                "arguments": [],
                "baseImageRegistry": {
                    "address": "mycontainer.azurecr.io",
                    "username": "mycontainer",
                    "password": "*********"
				}
            }
        },
        "history": {
            "outputCollection": true,
        }
    },
    "runtype": "experiment"
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
