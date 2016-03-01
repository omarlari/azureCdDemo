import requests
import azure
from azure.mgmt.resource import Deployment
from azure.mgmt.resource import DeploymentProperties
from azure.mgmt.resource import DeploymentMode
from azure.mgmt.resource import ParametersLink
from azure.mgmt.resource import TemplateLink
from azure.mgmt.resource import ResourceGroup
from azure.mgmt.common import SubscriptionCloudCredentials
from azure.mgmt.resource import ResourceManagementClient



def get_token_from_client_credentials(endpoint, client_id, client_secret):
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://management.core.windows.net/',
    }
    response = requests.post(endpoint, data=payload).json()
    return response['access_token']

auth_token = get_token_from_client_credentials(
    endpoint='https://login.microsoftonline.com/da67ef1b-ca59-4db2-9a8c-aa8d94617a16/oauth2/token',
    client_id='a956ef55-094c-44ba-8310-1e6ad8417097',
    client_secret='Mi55ion5urfer7',
)

subscription_id = '727d0898-6b7d-4ee6-8280-bac217884ddc'
creds = SubscriptionCloudCredentials(subscription_id, auth_token)

resource_client = ResourceManagementClient(creds)

deployment_name = 'azurecddemo'

template = TemplateLink(
    uri='https://github.com/omarlari/azureCdDemo/blob/master/vnet.json',
)

parameters = ParametersLink(
    uri='https://github.com/omarlari/azureCdDemo/blob/master/vnet.parameters.json',
)

group_name = "azurecddemo"
"""
action = resource_client.resource_groups.create_or_update(
    group_name,
    ResourceGroup(
        location='westus',
        tags={
            'env': 'deployed via Python',
        },
    )
)
"""
result = resource_client.deployments.create_or_update(
    group_name,
    deployment_name,
    Deployment(
        properties=DeploymentProperties(
            mode=DeploymentMode.incremental,
            template_link=template,
            parameters_link=parameters,
        )
    )
)