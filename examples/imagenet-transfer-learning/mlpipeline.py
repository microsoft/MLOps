#!/usr/bin/env python
"""This training pipeline leverages Azure ML Pipelines to
   retrain and store a mobilenet model"""

from azureml.core import Workspace, Datastore
from azureml.core.compute import AmlCompute, DataFactoryCompute
from azureml.core.runconfig import CondaDependencies, RunConfiguration
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.steps import DataTransferStep

aml_compute_target = "cpu"
data_factory_name = "adf"
default_dataset = "soda_cans_training_data"
project_folder = "."

ws = Workspace.from_config()
ds = ws.get_default_datastore()
source_ds = Datastore.get(ws, 'samplemobilenetimages')

# Declare packages dependencies required in the pipeline (these can also be expressed as a YML file)
cd = CondaDependencies.create(pip_packages=["azureml-defaults", 'tensorflow==1.8.0'])
amlcompute_run_config = RunConfiguration(conda_dependencies=cd)

# Define our computes
data_factory_compute = DataFactoryCompute(ws, data_factory_name)
aml_compute = AmlCompute(ws, aml_compute_target)

# We explicitly declare the data we're using in this training pipeline
source_images = DataReference(datastore=source_ds,
                              data_reference_name="original_images",
                              path_on_datastore=default_dataset)
dest_images = DataReference(datastore=ds,
                            data_reference_name="transferred_images",
                            path_on_datastore='training_images')

training_dataset = DataPath(datastore=source_ds, path_on_datastore=default_dataset)

# Parameters make it easy for us to re-run this training pipeline, including for retraining.
model_variant = PipelineParameter(name="model_variant", default_value='sodacans')
training_dataset_param = (PipelineParameter(name="training_dataset",
                                            default_value=training_dataset),
                          DataPathComputeBinding())

# Copying data into a datastore we manage ensures we can reproduce the model later on.
datatransfer = DataTransferStep(
    name="Copy training data for improved performance and model reproducibility",
    source_data_reference=source_images,
    destination_data_reference=dest_images,
    compute_target=data_factory_compute)

# We pass the trained model from the transfer learning step to the model registration step
model = PipelineData(name="model", datastore=ds, output_path_on_compute="model")
model_id = PipelineData(name="modelId", datastore=ds)

# You'll note this is similar to the code from the notebook.
# We've done some cleanup to reflect the proper parameterization of the steps.
train = PythonScriptStep(name="Train new model via transfer learning",
                         script_name="train.py",
                         compute_target=aml_compute,
                         runconfig=amlcompute_run_config,
                         inputs=[training_dataset_param, dest_images],
                         outputs=[model],
                         source_directory=project_folder,
                         arguments=['--image_dir', training_dataset_param,
                                    '--architecture', 'mobilenet_1.0_224',
                                    '--output_dir', model,
                                    '--output_graph', 'retrained_graph.pb',
                                    '--output_labels', 'output_labels.txt',
                                    '--model_file_name', 'imagenet_2_frozen.pb'
                                   ])

register = PythonScriptStep(name="Register model for deployment",
                            script_name="register.py",
                            compute_target=aml_compute,
                            inputs=[model],
                            arguments=['--dataset_name', model_variant,
                                       '--model_assets_path', model
                                      ],
                            outputs=[model_id],
                            source_directory=project_folder)

steps = [datatransfer, train, register]
pipeline = Pipeline(workspace=ws, steps=steps)
pipeline.validate()

mlpipeline = pipeline.publish(name="Transfer Learning - Training Pipeline",
                              description="Retrain a mobilenet.imagenet model.")

print("Pipeline Published ID:"+mlpipeline.id)

mlpipeline.submit(ws, "sodacanclassifier",
                  pipeline_parameters={"training_dataset":DataPath(datastore=source_ds,
                                                                   path_on_datastore="soda_cans_training_data"),
                                       "model_variant":"sodacans"})

"""
Examples showing you how to train different variants of models, with the same training pipeline.
You'll note we modify the model variants as well.

mlpipeline.submit(ws,"flowersclassifier", 
                  pipeline_parameters={"training_dataset":DataPath(datastore=source_ds,
                                                                   path_on_datastore="flowers_training_data"),
                                       "model_variant":"flowers"}).set_tags(tags)
"""