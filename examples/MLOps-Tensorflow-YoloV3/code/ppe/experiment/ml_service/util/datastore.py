import sys
import os
import os.path
from dotenv import load_dotenv
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core import Datastore
from azureml.core.authentication import ServicePrincipalAuthentication

load_dotenv()

TENANT_ID = os.environ.get('TENANT_ID')
APP_ID = os.environ.get('SP_APP_ID')
APP_SECRET = os.environ.get('SP_APP_SECRET')
WORKSPACE_NAME = os.environ.get("BASE_NAME")+"-aml"
SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')
RESOURCE_GROUP = os.environ.get("RESOURCE_GROUP_NAME")
UPDATE_DATA = os.environ.get("UPDATE_DATA")
STORAGE_NAME = os.environ.get("STORAGE_NAME")
EPIS_CONTAINER = os.environ.get("EPIS_CONTAINER")
EPIS_DATASTORE = os.environ.get("EPIS_DATASTORE")
STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")

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
    if UPDATE_DATA:
        Datastore.register_azure_blob_container(WORKSPACE, EPIS_DATASTORE, 
                                                EPIS_CONTAINER, STORAGE_NAME, sas_token=None, 
                                                account_key=STORAGE_ACCOUNT_KEY, protocol=None, endpoint=None, 
                                                overwrite=True, create_if_not_exists=True,
                                                subscription_id=SUBSCRIPTION_ID, resource_group=RESOURCE_GROUP)
        print("Dataset EPIS registered")
    print("Dataset EPIS registered successfully")
except Exception as caught_error:
    print("Error while registering the dataset on datastore: " + str(caught_error))
    sys.exit(1)