import sys
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication


def get_workspace(
        name: str,
        resource_group: str,
        subscription_id: str,
        tenant_id: str,
        app_id: str,
        app_secret: str):
    service_principal = ServicePrincipalAuthentication(
        tenant_id=tenant_id,
        service_principal_id=app_id,
        service_principal_password=app_secret)

    try:
        aml_workspace = Workspace.get(
            name=name,
            subscription_id=subscription_id,
            resource_group=resource_group,
            auth=service_principal)

        return aml_workspace
    except Exception as caught_exception:
        print("Error while retrieving Workspace...")
        print(str(caught_exception))
        sys.exit(1)
