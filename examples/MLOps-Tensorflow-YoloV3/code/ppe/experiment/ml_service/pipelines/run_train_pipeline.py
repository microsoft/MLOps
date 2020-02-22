import os
from azureml.pipeline.core import PublishedPipeline
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication
from dotenv import load_dotenv


def main():
    load_dotenv()
    workspace_name = os.environ.get("WORKSPACE_NAME")
    resource_group = os.environ.get("RESOURCE_GROUP_NAME")
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    tenant_id = os.environ.get("TENANT_ID")
    experiment_name = os.environ.get("EXPERIMENT_NAME")
    model_name = os.environ.get("MODEL_NAME")
    ckpt_path = os.environ.get("MODEL_CHECKPOINT_PATH")
    app_id = os.environ.get('SP_APP_ID')
    app_secret = os.environ.get('SP_APP_SECRET')
    build_id = os.environ.get('BUILD_BUILDID')
    datastore = os.environ.get('EPIS_DATASTORE')
    container_name = os.environ.get('EPIS_CONTAINER')

    service_principal = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=app_id,
            service_principal_password=app_secret)

    aml_workspace = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=service_principal
        )

    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []

    for p in pipelines:
        if p.version == build_id:
            matched_pipes.append(p)

    if(len(matched_pipes) > 1):
        published_pipeline = None
        raise Exception(f"Multiple active pipelines are published for build {build_id}.")
    elif(len(matched_pipes) == 0):
        published_pipeline = None
        raise KeyError(f"Unable to find a published pipeline for this build {build_id}")
    else:
        published_pipeline = matched_pipes[0]

    pipeline_parameters = {"model_name": model_name, "ckpt_path": ckpt_path, "datastore": datastore, "storage_container": container_name}

    response = published_pipeline.submit(
        aml_workspace,
        experiment_name,
        pipeline_parameters)

    run_id = response.id
    print("Pipeline run initiated ", run_id)


if __name__ == "__main__":
    main()