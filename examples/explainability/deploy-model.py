from azureml.core import Workspace
from azureml.core.webservice import AciWebservice
from azureml.core.model import InferenceConfig, Model

ws = Workspace.from_config()

scoring_explainer_model = Model(ws, 'IBM_attrition_explainer')
attrition_model = Model(ws, 'IBM_attrition_model')

aciconfig = AciWebservice.deploy_configuration(cpu_cores=1, 
                                               memory_gb=1, 
                                               tags={"data": "IBM_Attrition",  
                                                     "method" : "local_explanation"}, 
                                               description='Explain predictions on employee attrition')
                                               
inference_config = InferenceConfig(entry_script='score.py', 
                                   extra_docker_file_steps='Dockerfile', 
                                   runtime='python', 
                                   conda_file='myenv.yml')

service = Model.deploy(ws, name='predictattrition', models=[scoring_explainer_model, attrition_model], inference_config= inference_config, deployment_config=aciconfig)
