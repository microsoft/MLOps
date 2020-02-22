import sys
import os
import os.path
from dotenv import load_dotenv
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.authentication import ServicePrincipalAuthentication

load_dotenv()

TENANT_ID = os.environ.get('TENANT_ID')
APP_ID = os.environ.get('SP_APP_ID')
APP_SECRET = os.environ.get('SP_APP_SECRET')
MODEL_PATH = os.environ.get('MODEL_PATH')
MODEL_NAME = os.environ.get('MODEL_NAME')
WORKSPACE_NAME = os.environ.get("BASE_NAME")+"-aml"
SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')
RESOURCE_GROUP = os.environ.get("RESOURCE_GROUP_NAME")

if os.path.isfile(MODEL_PATH) is False:
    print("The given model path %s is invalid" % (MODEL_PATH))
    sys.exit(1)

SP_AUTH = ServicePrincipalAuthentication(
    tenant_id=TENANT_ID,
    service_principal_id=APP_ID,
    service_principal_password=APP_SECRET)

WORKSPACE = Workspace.get(
    WORKSPACE_NAME,
    SP_AUTH,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP
)

try:
    MODEL = Model.register(
        model_path=MODEL_PATH,
        model_name=MODEL_NAME,
        description="EPIS Model",
        workspace=WORKSPACE)

    print("Model registered successfully. ID: " + MODEL.id)
except Exception as caught_error:
    print("Error while registering the model: " + str(caught_error))
    sys.exit(1)
