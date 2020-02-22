import os
from dotenv import load_dotenv
from azureml.core import Workspace
from scripts.voc_annotation import convert_voc_annotation
from azureml.core.authentication import ServicePrincipalAuthentication


def main():
    load_dotenv()
    TENANT_ID = os.environ.get('TENANT_ID')
    APP_ID = os.environ.get('SP_APP_ID')
    APP_SECRET = os.environ.get('SP_APP_SECRET')
    WORKSPACE_NAME = os.environ.get("BASE_NAME")+"-aml"
    SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')
    RESOURCE_GROUP = os.environ.get("RESOURCE_GROUP_NAME")
    EPIS_DATASTORE = os.environ.get("EPIS_DATASTORE")
    ANNO_PATH_TRAIN = os.environ.get("ANNO_PATH_TRAIN")
    ANNO_PATH_TEST = os.environ.get("ANNO_PATH_TEST")
    EPIS_CONTAINER = os.environ.get("EPIS_CONTAINER")


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
        convert_voc_annotation(WORKSPACE, EPIS_DATASTORE, "trainval", ANNO_PATH_TRAIN, EPIS_CONTAINER)
        convert_voc_annotation(WORKSPACE, EPIS_DATASTORE, "test", ANNO_PATH_TEST, EPIS_CONTAINER)
    except Exception as caught_error:
        print("Error while download datastore: " + str(caught_error))

if __name__ == '__main__':
    main()