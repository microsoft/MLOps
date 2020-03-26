import os
import sys
import json
import argparse
from azureml.core import Workspace, Experiment, Datastore
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.data.data_reference import DataReference
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.pipeline.core import Pipeline, PipelineData, PipelineParameter, PublishedPipeline, PipelineEndpoint
from azureml.pipeline.steps import PythonScriptStep, EstimatorStep
from azureml.train.estimator import Estimator

##############################################################
#    Get Azure Machine Learning Resources                    #
##############################################################
def get_workspace(workspace: str, subscription: str, resource_group: str, tenantId: str, clientId: str, clientSecret: str) -> Workspace:

    svcprincipal = ServicePrincipalAuthentication(tenant_id=tenantId,
                                                  service_principal_id=clientId,
                                                  service_principal_password=clientSecret)
    return Workspace.get(name=workspace, 
                         subscription_id=subscription, 
                         resource_group=resource_group,
                         auth=svcprincipal)

def get_datastore(ws: Workspace, datastore_name: str, container: str, account_name: str, account_key: str) -> Datastore:
    if not datastore_name in ws.datastores:
        Datastore.register_azure_blob_container(workspace=ws, 
                                            datastore_name=datastore_name, 
                                            container_name=container,
                                            account_name=account_name, 
                                            account_key=account_key,
                                            create_if_not_exists=True)
        
    return ws.datastores[datastore_name]

def get_compute(ws: Workspace, compute_target: str) -> ComputeTarget:
    if not compute_target in ws.compute_targets:
        compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_NC6', min_nodes=1, max_nodes=4)
        cluster = ComputeTarget.create(ws, compute_target, compute_config)
        cluster.wait_for_completion(show_output=True)

    return ws.compute_targets[compute_target]

##############################################################
#    Create Pipeline Steps                                   #
##############################################################

# data process step
def process_step(datastore: Datastore, compute: ComputeTarget, path_on_datastore: str) -> (PipelineData, EstimatorStep):
    datapath = DataPath(datastore=datastore, path_on_datastore=path_on_datastore)
    data_path_pipeline_param = (PipelineParameter(name="data", default_value=datapath), DataPathComputeBinding(mode='mount'))

    seer_tfrecords = PipelineData(
        "tfrecords_set",
        datastore=datastore,
        is_directory=True
    )

    prep = Estimator(source_directory='.',
                        compute_target=compute,
                        entry_script='prep.py',
                        use_gpu=True,
                        pip_requirements_file='requirements.txt')

    prepStep = EstimatorStep(
        name='Data Preparation',
        estimator=prep,
        estimator_entry_script_arguments=["--source_path", data_path_pipeline_param, 
                                          "--target_path", seer_tfrecords],
        inputs=[data_path_pipeline_param],
        outputs=[seer_tfrecords],
        compute_target=compute
    )

    return seer_tfrecords, prepStep

def train_step(datastore: Datastore, input_data: PipelineData, compute: ComputeTarget) -> (PipelineData, EstimatorStep):
    seer_training = PipelineData(
        "train",
        datastore=datastore,
        is_directory=True
    )

    train = Estimator(source_directory='.',
                        compute_target=compute,
                        entry_script='train.py',
                        use_gpu=True,
                        pip_requirements_file='requirements.txt')

    trainStep = EstimatorStep(
        name='Model Training',
        estimator=train,
        estimator_entry_script_arguments=["--source_path", input_data, 
                                        "--target_path", seer_training,
                                        "--epochs", 15,
                                        "--batch", 10,
                                        "--lr", 0.001],
        inputs=[input_data],
        outputs=[seer_training],
        compute_target=compute
    )

    return seer_training, trainStep

def register_step(datastore: Datastore, input_data: PipelineData, compute: ComputeTarget, build: str) -> (PipelineData, EstimatorStep):
    seer_model = PipelineData(
        "model",
        datastore=datastore,
        is_directory=True
    )

    register = Estimator(source_directory='.',
                        compute_target=compute,
                        entry_script='register.py')

    registerStep = EstimatorStep(
        name='Model Registration',
        estimator=register,
        estimator_entry_script_arguments=["--source_path", input_data, 
                                          "--target_path", seer_model,
                                          "--build", build],
        inputs=[input_data],
        outputs=[seer_model],
        compute_target=compute
    )

    return seer_model, registerStep

##############################################################
#    Manage Endpoint                                         #
##############################################################
def add_endpoint(ws: Workspace, pipeline: PublishedPipeline, endpoint_name: str) -> PipelineEndpoint:
    endpoint_list = [p.name for p in PipelineEndpoint.list(ws)]
    endpoint = None
    # endpoint does not exist so add
    if endpoint_name in endpoint_list:
        endpoint = PipelineEndpoint.get(workspace=ws, name=endpoint_name)
        endpoint.add_default(pipeline)
    else:
        endpoint = PipelineEndpoint.publish(workspace=ws, name=endpoint_name,
                                                pipeline=pipeline, description="Seer Pipeline Endpoint")
    return endpoint

def parse_args(secrets: str) -> dict:
    args = {
        "datastore_name": "",
        "datastore_path": "",
        "compute_target": "",
        "universal_package": "",
        "subscription": "",
        "storage_account": "",
        "storage_key": "",
        "container": "",
        "resource_group": "",
        "workspace": "",
        "tenantId": "",
        "clientId": "",
        "clientSecret": ""
    }

    variables = {}

    # try to load if its a file
    if os.path.exists(secrets):
        with open(secrets) as f:
            variables = json.load(f)
    # otherwise load straight as string
    else:
        variables = json.loads(secrets)

    for k,v in variables.items():
        if k in args:
            args[k] = v

    return args

##############################################################
#    Main Run                                                #
##############################################################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Seer Pipeline')
    parser.add_argument('-a', '--arguments', help='json file with arguments')
    parser.add_argument('-b', '--build', help='build number')


    args = parser.parse_args()

    print(args.arguments)

    secrets = parse_args(args.arguments)

    # get aml workspace
    ws = get_workspace(secrets["workspace"], secrets["subscription"], secrets["resource_group"], secrets["tenantId"], secrets["clientId"], secrets["clientSecret"])

    # get datastore
    datastore = get_datastore(ws, secrets["datastore_name"], secrets["container"], secrets["storage_account"], secrets["storage_key"])

    # get compute
    compute = get_compute(ws, secrets["compute_target"])

    # prep step
    pdata, pstep = process_step(datastore, compute, secrets["datastore_path"])

    # train step
    tdata, tstep = train_step(datastore, pdata, compute)

    # register step (tag model with version)
    rdata, rstep = register_step(datastore, tdata, compute, args.build)

    # create pipeline from steps
    seer_pipeline = Pipeline(workspace=ws, steps=[pstep, tstep, rstep])
    published_pipeline = seer_pipeline.publish(name="Seer Pipeline", 
        description="Transfer learned image classifier. Uses folders as labels.")

    # add pipeline to endpoint
    endpoint = add_endpoint(ws, published_pipeline, 'seer-endpoint')

    # run pipeline
    pipeline_run = endpoint.submit('seer')                               
    pipeline_run.set_tags(tags={'build': args.build})
    print(f'Run created with ID: {pipeline_run.id}')
