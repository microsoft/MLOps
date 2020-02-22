from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline
from azureml.core.runconfig import RunConfiguration, CondaDependencies, DEFAULT_GPU_IMAGE
from azureml.core import Datastore
import os
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath("./code/ppe/experiment/ml_service/util"))
from workspace import get_workspace
from attach_compute import get_compute


def main():
    load_dotenv()
    workspace_name = os.environ.get("WORKSPACE_NAME")
    resource_group = os.environ.get("RESOURCE_GROUP_NAME")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    tenant_id = os.environ.get("TENANT_ID")
    app_id = os.environ.get("SP_APP_ID")
    app_secret = os.environ.get("SP_APP_SECRET")
    sources_directory_train = os.environ.get("SOURCES_DIR_TRAIN")
    train_script_path = os.environ.get("TRAIN_SCRIPT_PATH")
    evaluate_script_path = os.environ.get("EVALUATE_SCRIPT_PATH")
    generate_report_path = os.environ.get("GENERATE_REPORT_PATH")
    generate_report_name = os.environ.get("GENERATE_REPORT_NAME")
    vm_size = os.environ.get("AML_COMPUTE_CLUSTER_GPU_SKU")
    compute_name = os.environ.get("AML_COMPUTE_CLUSTER_NAME")
    model_name = os.environ.get("MODEL_NAME")
    ckpt_path = os.environ.get("MODEL_CHECKPOINT_PATH")
    build_id = os.environ.get("BUILD_BUILDID")
    pipeline_name = os.environ.get("TRAINING_PIPELINE_NAME")
    epis_datastore = os.environ.get("EPIS_DATASTORE")
    epis_container = os.environ.get("EPIS_CONTAINER")

    aml_workspace = get_workspace(
        workspace_name,
        resource_group,
        subscription_id,
        tenant_id,
        app_id,
        app_secret)
    print(aml_workspace)

    aml_compute = get_compute(
        aml_workspace,
        compute_name,
        vm_size)
    if aml_compute is not None:
        print(aml_compute)

    run_config = RunConfiguration(conda_dependencies=CondaDependencies.create(
        conda_packages=['numpy==1.18.1', 'pandas', 'tensorflow-gpu==2.0.0'],
        pip_packages=['azure', 'azureml-core==1.0.60', 'azureml-tensorboard', 'azure-storage==0.36.0',
                    'tqdm==4.41.1', 'opencv-python==4.1.2.30', 'easydict==1.9', 'matplotlib==3.1.3'])
    )
    run_config.environment.docker.enabled = True
    run_config.environment.docker.gpu_support = True
    run_config.environment.docker.base_image = DEFAULT_GPU_IMAGE

    model_name = PipelineParameter(
        name="model_name", default_value=model_name)
    release_id = PipelineParameter(
        name="release_id", default_value=build_id)

    train_step = PythonScriptStep(
        name="Train Model",
        script_name=train_script_path,
        compute_target=aml_compute,
        source_directory=sources_directory_train,
        arguments=[
            "--release_id", release_id,
            "--model_name", model_name,
            "--ckpt_path", ckpt_path,
            "--datastore", epis_datastore,
            "--storage_container", epis_container,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Train created")

    evaluate_step = PythonScriptStep(
        name="Evaluate Model",
        script_name=evaluate_script_path,
        compute_target=aml_compute,
        source_directory=sources_directory_train,
        arguments=[
            "--release_id", release_id,
            "--model_name", model_name,
            "--ckpt_path", ckpt_path,
            "--datastore", epis_datastore,
            "--storage_container", epis_container,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Evaluate created")

    generate_report_step = PythonScriptStep(
        name="Generate Report Model",
        script_name=generate_report_name,
        compute_target=aml_compute,
        source_directory=generate_report_path,
        arguments=[
            "--release_id", release_id,
            "--model_name", model_name,
            "--ckpt_path", ckpt_path,
            "--datastore", epis_datastore,
            "--storage_container", epis_container,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step generate report created")

    evaluate_step.run_after(train_step)
    generate_report_step.run_after(evaluate_step)
    steps = [train_step, evaluate_step, generate_report_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=pipeline_name,
        description="Model training/retraining pipeline",
        version=build_id
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()