import requests
from azure.mgmt.resource import Deployment
from azure.mgmt.resource import DeploymentProperties
from azure.mgmt.resource import DeploymentMode
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

deployment_name = 'pythontesting'

template = """{
    "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "location": {
            "type": "String",
            "metadata": {
                "description": "Region where the resources will be deployed"
            },
            "allowedValues": [
                "East US",
                "East US 2",
                "East Asia",
                "West US",
                "West Europe",
                "Southeast Asia",
                "South Central US",
                "East US 2",
                "Japan East",
                "Japan West",
                "Central US",
                "Brazil South"
            ]
        },
        "vpnType": {
            "type": "String",
            "metadata": {
                "description": "Route based (Dynamic Gateway) or Policy based (Static Gateway)"
            },
            "defaultValue": "RouteBased",
            "allowedValues": [
                "RouteBased",
                "PolicyBased"
            ]
        },
        "localGatewayName": {
            "type": "string",
            "defaultValue": "localGateway",
            "metadata": {
                "description": "Arbitrary name for gateway resource representing your local/on-prem gateway"
            }
        },
        "localGatewayIpAddress": {
            "type": "string",
            "metadata": {
                "description": "Public IP of your local/on-prem gateway"
            }
        },
        "localAddressPrefix": {
            "type": "string",
            "metadata": {
                "description": "CIDR block representing the address space of your local/on-prem network's Subnet"
            }
        },
        "virtualNetworkName": {
            "type": "string",
            "defaultValue": "azureVnet",
            "metadata": {
                "description": "Arbitrary name for the Azure Virtual Network"
            }
        },
        "azureVNetAddressPrefix": {
            "type": "string",
            "defaultValue": "10.3.0.0/16",
            "metadata": {
                "description": "CIDR block representing the address space of the Azure VNet"
            }
        },
        "subnetName": {
            "type": "string",
            "defaultValue": "Subnet1",
            "metadata": {
                "description": "Aribtrary name for the Azure Subnet"
            }
        },
        "subnetPrefix": {
            "type": "string",
            "metadata": {
                "description": "CIDR block for VM subnet, subset of azureVNetAddressPrefix address space"
            }
        },
        "gatewaySubnetPrefix": {
            "type": "string",
            "defaultValue": "10.3.200.0/29",
            "metadata": {
                "description": "CIDR block for gateway subnet, subsset of azureVNetAddressPrefix address space"
            }
        },
        "gatewayPublicIPName": {
            "type": "string",
            "defaultValue": "azureGatewayIP",
            "metadata": {
                "description": "Aribtary name for public IP resource used for the new azure gateway"
            }
        },
        "gatewayName": {
            "type": "string",
            "defaultValue": "azureGateway",
            "metadata": {
                "description": "Arbitrary name for the new gateway"
            }
        },
        "connectionName": {
            "type": "string",
            "defaultValue": "Azure2Other",
            "metadata": {
                "description": "Arbitrary name for the new connection between Azure VNet and other network"
            }
        },
        "sharedKey": {
            "type": "string",
            "metadata": {
                "description": "Shared key (PSK) for IPSec tunnel"
            }
        },
        "vmName": {
            "type": "string",
            "defaultValue": "node-1",
            "metadata": {
                "description": "Name of the sample VM to create"
            }
        },
        "vmSize": {
            "type": "string",
            "defaultValue": "Standard_A1",
            "allowedValues": [
                "Standard_A1",
                "Standard_A2",
                "Standard_A3",
                "Standard_A6",
                "Standard_A7",
                "Standard_A8",
                "Standard_A9",
                "Standard_A10",
                "Standard_A11",
                "Standard_D2",
                "Standard_D3",
                "Standard_D4",
                "Standard_D11",
                "Standard_D12",
                "Standard_D13",
                "Standard_D14"
            ],
            "metadata": {
                "description": "Size of the Virtual Machine."
            }
        },
        "adminUsername": {
            "type": "string",
            "metadata": {
                "description": "Username for sample VM"
            }
        },
        "adminPassword": {
            "type": "securestring",
            "metadata": {
                "description": "User password for sample VM"
            }
        },
        "newStorageAccountName": {
            "type": "string",
            "metadata": {
                "description": "Storage Account Name for VM Disk"
            }
        },
        "storageAccountType": {
            "type": "string",
            "allowedValues": [
                "Standard_LRS",
                "Standard_GRS",
                "Standard_RAGRS",
                "Premium_LRS"
            ],
            "metadata": {
                "description": "The type of the Storage Account created"
            },
            "defaultValue": "Standard_LRS"
        }
    },
    "variables": {
        "imagePublisher": "Canonical",
        "imageOffer": "UbuntuServer",
        "imageSKU": "14.04.2-LTS",
        "vnetID": "[resourceId('Microsoft.Network/virtualNetworks', parameters('virtualNetworkName'))]",
        "gatewaySubnetRef": "[concat(variables('vnetID'),'/subnets/','GatewaySubnet')]",
        "subnetRef": "[concat(variables('vnetID'),'/subnets/',parameters('subnetName'))]",
        "nicName": "[concat(parameters('vmName'), '-nic')]",
        "vmStorageAccountContainerName": "vhds",
        "OSDiskName": "osDisk",
        "vmPublicIPName": "[concat(parameters('vmName'), '-publicIP')]",
        "api-version": "2015-06-15",
        "storage-api-version": "2015-05-01-preview"
    },
    "resources": [
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Network/localNetworkGateways",
            "name": "[parameters('localGatewayName')]",
            "location": "[parameters('location')]",
            "properties": {
                "localNetworkAddressSpace": {
                    "addressPrefixes": [
                        "[parameters('localAddressPrefix')]"
                    ]
                },
                "gatewayIpAddress": "[parameters('localGatewayIpAddress')]"
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "name": "[parameters('connectionName')]",
            "type": "Microsoft.Network/connections",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[concat('Microsoft.Network/virtualNetworkGateways/', parameters('gatewayName'))]",
                "[concat('Microsoft.Network/localNetworkGateways/', parameters('localGatewayName'))]"
            ],
            "properties": {
                "virtualNetworkGateway1": {
                    "id": "[resourceId('Microsoft.Network/virtualNetworkGateways', parameters('gatewayName'))]"
                },
                "localNetworkGateway2": {
                    "id": "[resourceId('Microsoft.Network/localNetworkGateways', parameters('localGatewayName'))]"
                },
                "connectionType": "IPsec",
                "routingWeight": 10,
                "sharedKey": "[parameters('sharedKey')]"
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Network/virtualNetworks",
            "name": "[parameters('virtualNetworkName')]",
            "location": "[parameters('location')]",
            "properties": {
                "addressSpace": {
                    "addressPrefixes": [
                        "[parameters('azureVNetAddressPrefix')]"
                    ]
                },
                "subnets": [
                    {
                        "name": "[parameters('subnetName')]",
                        "properties": {
                            "addressPrefix": "[parameters('subnetPrefix')]"
                        }
                    },
                    {
                        "name": "GatewaySubnet",
                        "properties": {
                            "addressPrefix": "[parameters('gatewaySubnetPrefix')]"
                        }
                    }
                ]
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[parameters('gatewayPublicIPName')]",
            "location": "[parameters('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Network/publicIPAddresses",
            "name": "[variables('vmPublicIPName')]",
            "location": "[parameters('location')]",
            "properties": {
                "publicIPAllocationMethod": "Dynamic"
            }
        },
        {
            "apiVersion": "[variables('storage-api-version')]",
            "name": "[parameters('newStorageAccountName')]",
            "location": "[parameters('location')]",
            "type": "Microsoft.Storage/storageAccounts",
            "properties": {
                "accountType": "[parameters('storageAccountType')]"
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Network/virtualNetworkGateways",
            "name": "[parameters('gatewayName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[concat('Microsoft.Network/publicIPAddresses/', parameters('gatewayPublicIPName'))]",
                "[concat('Microsoft.Network/virtualNetworks/', parameters('virtualNetworkName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "properties": {
                            "privateIPAllocationMethod": "Dynamic",
                            "subnet": {
                                "id": "[variables('gatewaySubnetRef')]"
                            },
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses',parameters('gatewayPublicIPName'))]"
                            }
                        },
                        "name": "vnetGatewayConfig"
                    }
                ],
                "gatewayType": "Vpn",
                "vpnType": "[parameters('vpnType')]",
                "enableBgp": "false"
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Network/networkInterfaces",
            "name": "[variables('nicName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[concat('Microsoft.Network/publicIPAddresses/', variables('vmPublicIPName'))]",
                "[concat('Microsoft.Network/virtualNetworks/', parameters('virtualNetworkName'))]",
                "[concat('Microsoft.Network/virtualNetworkGateways/', parameters('gatewayName'))]"
            ],
            "properties": {
                "ipConfigurations": [
                    {
                        "name": "ipconfig1",
                        "properties": {
                            "privateIPAllocationMethod": "Dynamic",
                            "publicIPAddress": {
                                "id": "[resourceId('Microsoft.Network/publicIPAddresses',variables('vmPublicIPName'))]"
                            },
                            "subnet": {
                                "id": "[variables('subnetRef')]"
                            }
                        }
                    }
                ]
            }
        },
        {
            "apiVersion": "[variables('api-version')]",
            "type": "Microsoft.Compute/virtualMachines",
            "name": "[parameters('vmName')]",
            "location": "[parameters('location')]",
            "dependsOn": [
                "[concat('Microsoft.Storage/storageAccounts/', parameters('newStorageAccountName'))]",
                "[concat('Microsoft.Network/networkInterfaces/', variables('nicName'))]"
            ],
            "properties": {
                "hardwareProfile": {
                    "vmSize": "[parameters('vmSize')]"
                },
                "osProfile": {
                    "computerName": "[parameters('vmName')]",
                    "adminUsername": "[parameters('adminUsername')]",
                    "adminPassword": "[parameters('adminPassword')]"
                },
                "storageProfile": {
                    "imageReference": {
                        "publisher": "[variables('imagePublisher')]",
                        "offer": "[variables('imageOffer')]",
                        "sku": "[variables('imageSKU')]",
                        "version": "latest"
                    },
                    "osDisk": {
                        "name": "osdisk1",
                        "vhd": {
                            "uri": "[concat('http://',parameters('newStorageAccountName'),'.blob.core.windows.net/',variables('vmStorageAccountContainerName'),'/',variables('OSDiskName'),'.vhd')]"
                        },
                        "caching": "ReadWrite",
                        "createOption": "FromImage"
                    }
                },
                "networkProfile": {
                    "networkInterfaces": [
                        {
                            "id": "[resourceId('Microsoft.Network/networkInterfaces',variables('nicName'))]"
                        }
                    ]
                }
            }
        }
    ]
}"""

# Note: when specifying values for parameters, omit the outer elements $schema, contentVersion, parameters

region = "West US"
parameters = '{"location": { "value": "West US"}, "adminUsername" : {"value" : "ubuntu"}, "localGatewayIpAddress": {"value": "143.112.145.250"}, "localAddressPrefix": {"value": "10.0.0.8/8"}, "localAddressPrefix": {"value": "172.16.0.0/13"}, "azureVNetAddressPrefix": {"value": "10.3.0.0/16"},"subnetPrefix": {"value": "10.3.0.0/24"},"gatewaySubnetPrefix": {"value": "10.3.200.0/29"}, "adminPassword": {"value": "English101"},"newStorageAccountName": {"value": "pythonvpn"},"sharedKey": {"value": "gh74PKRsvTH6DbJC6sSvnRqr8CggXweXmvv6M7TdhwxmbbbcDdppLUfrxPb2HkxXMnfzjcSds25wLwsKLLaSaPpdYNed2cqvZFBKWHpYgCNZQ5Ec2sv8w3vywg5Np2Xr"}}'
group_name = "PythonVpn"
action = resource_client.resource_groups.create_or_update(
    group_name,
    ResourceGroup(
        location='westus',
        tags={
            'env': 'deployed via Python',
        },
    )
)
result = resource_client.deployments.create_or_update(
    group_name,
    deployment_name,
    Deployment(
        properties=DeploymentProperties(
            mode=DeploymentMode.incremental,
            template=template,
            parameters=parameters,
        )
    )
)
