#!/bin/sh

## this script sets up the Azure Machine Learning service workspace using the Azure CLI

## YAML file parser (Adapted from: https://gist.github.com/pkuczynski/8665367)
parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

## BEGIN
echo "CREATING WORKSPACE, ASSIGNING ROLES"

## it tags the resource group and resources
## it also adds user and team

# eval $(parse_yaml config.yml "config_")
CUSTOM_YAML="$1"

## READ YAML file
if [ "$CUSTOM_YAML" != '' ]
then
  eval $(parse_yaml $CUSTOM_YAML "config_")
else
  eval $(parse_yaml config.yml "config_")
fi

## script requires Azure CLI with the Azure ML extension to be installed

SUBSCRIPTION_ID=${config_workspace_subscription}
CUSTOM_NAME=${config_workspace_custom_name}
DEPARTMENT_NAME=${config_workspace_department:0:4}
TEAM_NAME=${config_workspace_team:0:10}
LOCATION=${config_workspace_region}
LOCATION_ABBR=${config_workspace_region_abbv:0:2}
DEVENVIRONMENT=${config_workspace_environment:0:3}
TEAM_LEAD=${config_workspace_admin}
TEAM_SECURITY_GROUP=${config_workspace_security_group}
ADLS=${config_workspace_adls}

if [ "$CUSTOM_NAME" != '' ]
then
  resourcegroup_name=$CUSTOM_NAME
  resource_name=$CUSTOM_NAME
  resource_name=${resource_name:0:19}
else
  resourcegroup_name=$DEPARTMENT_NAME-$TEAM_NAME-$LOCATION-$DEVENVIRONMENT
  resource_name=$DEPARTMENT_NAME$TEAM_NAME$LOCATION_ABBR$DEVENVIRONMENT
  resource_name=${resource_name:0:19}
fi

echo 'RESOURCE GROUP: '$resourcegroup_name
echo 'resource_name: '$resource_name

read -p "Press 'y' to continue " CONTINUE_NOW
if [ "$CONTINUE_NOW" != 'y' ]
then
    exit 1
fi

echo "logging into Azure"
az login

echo "setting subscription to "$SUBSCRIPTION_ID
az account set --subscription $SUBSCRIPTION_ID

## create resource group
resource_exists=$(az group exists --name $resourcegroup_name)
if [ "$resource_exists" == 'false' ]
then
    echo "created: " $resourcegroup_name
    az group create --name $resourcegroup_name --location $LOCATION

else
	echo "resource group not created"
fi

az group update -n $resourcegroup_name --set tags.dept=$DEPARTMENT_NAME tags.team=$TEAM_NAME tags.owner=$TEAM_LEAD tags.expires=2019-06-30 tags.location=$LOCATION

workspace_name=$resource_name"ws"
workspace_storage_account_name=$resource_name"work"
workspace_storage_account_name=${workspace_storage_account_name:0:23}

data_storage_account_name=$resource_name"data"
data_storage_account_name=${data_storage_account_name:0:23}

container_registry_name=$resource_name"cr"
container_registry_name=${container_registry_name:0:23}

key_vault_name=$resource_name"kv"
key_vault_name=${key_vault_name:0:23}


## create storage accounts
storage_name_available=$(az storage account check-name --name $workspace_storage_account_name | jq .nameAvailable)
if [ $storage_name_available == 'true' ]
then
    echo $workspace_storage_account_name" is available"
else
	echo $workspace_storage_account_name" is not available: perhaps shorten team name or make it more unique"
	exit 1
fi

storage_name_available=$(az storage account check-name --name $workspace_storage_account_name | jq .nameAvailable)
if [ $storage_name_available  == 'true' ]
then
    echo $data_storage_account_name" is available"
else
	echo $data_storage_account_name" is not available: shorten team name or make it more unique"
	exit 1
fi


## this storage account is for Azure ML results and logs

echo "creating storage account "$workspace_storage_account_name
az storage account create --name $workspace_storage_account_name \
                        --resource-group $resourcegroup_name \
                        --location $LOCATION \
                        --sku Standard_LRS \
                        --kind StorageV2

workspace_storage_id=$(az storage account show -n $workspace_storage_account_name --query id | tr -d '"')
workspace_storage_key=$(az storage account keys list -g $resourcegroup_name -n $workspace_storage_account_name --query [0].value | tr -d '"')

## this storage account is for the user data

echo "creating storage account "$data_storage_account_name
az storage account create --name $data_storage_account_name \
                        --resource-group $resourcegroup_name \
                        --location $LOCATION \
                        --sku Standard_LRS \
                        --kind StorageV2

data_storage_account_id=$(az storage account show -n $data_storage_account_name -g $resourcegroup_name --query id | tr -d '"')
data_storage_account_key=$(az storage account keys list -g $resourcegroup_name -n $data_storage_account_name --query [0].value | tr -d '"')
az resource tag --name $data_storage_account_name --resource-group $resourcegroup_name --tags dept=$DEPARTMENT_NAME team=$TEAM_NAME owner=$TEAM_LEAD expires=2019-06-30 location=$LOCATION role=data --resource-type "Microsoft.Storage/storageAccounts"

## if Azure Data Lake Storage is required

ADLS="${ADLS,,}"
if [ "$ADLS" == 'y' ]
then
	data_lake_store_name=$resource_name"big"
	data_lake_store_name=${data_lake_store_name:0:23}
	echo "creating data lake account "$data_lake_store_name

	az storage account create --name $data_lake_store_name \
							--resource-group $resourcegroup_name \
							--location $LOCATION \
							--sku Standard_LRS \
							--kind StorageV2 #\
							#--hierarchical-namespace true

	data_lake_storage_account_id=$(az storage account show -n $data_lake_store_name --query id | tr -d '"')
	data_lake_storage_account_key=$(az storage account keys list -g $resourcegroup_name -n $data_lake_store_name --query [0].value | tr -d '"')
	az resource tag --name $data_lake_store_name --resource-group $resourcegroup_name --tags dept=$DEPARTMENT_NAME team=$TEAM_NAME owner=$TEAM_LEAD expires=2019-06-30 location=$LOCATION role=bigdata --resource-type "Microsoft.Storage/storageAccounts"
fi

## create key vault

echo "creating key vault "$key_vault_name
az keyvault create --name $key_vault_name --resource-group $resourcegroup_name --location $LOCATION

key_vault_id=$(az keyvault show --name $key_vault_name --resource-group $resourcegroup_name --query id | tr -d '"')

## put keys into key vault

az keyvault key create --vault-name $key_vault_name --name $data_storage_account_name --protection software
az keyvault secret set --name $data_storage_account_name --vault-name $key_vault_name --value $data_storage_account_key

az keyvault key create --vault-name $key_vault_name --name $workspace_storage_account_name --protection software
az keyvault secret set --name $workspace_storage_account_name --vault-name $key_vault_name --value $workspace_storage_key

## create container registry
echo "creating container registry "$container_registry_name
name_available=$(az acr check-name --name $container_registry_name --query nameAvailable)
if [ "$name_available" == 'true' ]
then
	echo "name available for container registry "$container_registry_name
	az acr create --name $container_registry_name --resource-group $resourcegroup_name --sku Basic --location $LOCATION --admin-enabled true
	container_registry_id=$(az acr show --name $container_registry_name --resource-group $resourcegroup_name --query id | tr -d '"')
	echo "container registry created: " $container_registry_name
else
	echo "container registry not available: " $container_registry_name
	exit 1
fi

## create workspace
echo "creating workspace "$workspace_name
## Make sure the ml extension is installed
az extension add -n azure-cli-ml

az ml workspace create --workspace $workspace_name --resource-group $resourcegroup_name --location $LOCATION \
    --verbose --storage-account $workspace_storage_id \
    --keyvault $key_vault_id  \
    --container-registry $container_registry_id

## tag resources
workspace_json=$(az ml workspace show --resource-group $resourcegroup_name --workspace-name $workspace_name)
echo $workspace_json

echo "retrieving the providers"
workspace_provider=$(echo $workspace_json | jq .id | tr -d '"')
echo "using workspace provider id"$workspace_provider

storageAccount_provider=$(echo $workspace_json | jq .storageAccount | tr -d '"')
echo "using storage provider id"$storageAccount_provider

applicationInsights_provider=$(echo $workspace_json | jq .applicationInsights | tr -d '"')
echo "using appInsights provider id"$applicationInsights_provider

containerRegistry_provider=$(echo $workspace_json | jq .containerRegistry | tr -d '"')
echo "using workspace provider id"$containerRegistry_provider

keyVault_provider=$(echo $workspace_json | jq .keyVault | tr -d '"')
echo "using key vault provider id"$keyVault_provider

echo "tagging resources "
## tag resources for workspace as built
az resource tag --id $workspace_provider $storageAccount_provider $applicationInsights_provider $containerRegistry_provider $keyVault_provider --tags dept=$DEPARTMENT_NAME team=$TEAM_NAME owner=$TEAM_LEAD expires=2019-06-30 location=$LOCATION role=AML

##########
# ADD DATA SCIENTIST ROLE
##########
echo "Creating Data Scientist role."
az role definition create --role-definition role_datascientist.json

##########
# SET ADMIN
##########

echo "setting role based access control"

if [ "$TEAM_LEAD" == "" ]
then
    echo "no team lead"
else
	admin=$TEAM_LEAD
	echo "Adding team lead: "$admin

  # grant the team lead Reader permission for the team lead to the resource group
  echo "+ Resource Group (Reader): "$admin
  az role assignment create --role 'Reader' --assignee $admin  --resource-group $resourcegroup_name

  echo "+ Share Workspace: "$admin
	az ml workspace share -w $workspace_name -g $resourcegroup_name --role "Data Scientist" --user $admin

  echo "+ App Insights (Owner): "$admin
	az role assignment create --role 'Owner' --assignee $admin --scope $applicationInsights_provider
  echo "+ Provider Storage Account (Owner): "$admin
  az role assignment create --role 'Storage Blob Data Owner' --assignee $admin --scope $storageAccount_provider
  echo "+ Key Vault (Owner): "$admin
  az role assignment create --role 'Owner' --assignee $admin --scope $keyVault_provider
  echo "+ Container Registry (Owner): "$admin
  az role assignment create --role 'Owner' --assignee $admin --scope $containerRegistry_provider
  echo "+ Data Storage Account (Owner): "$admin
  az role assignment create --role 'Storage Blob Data Owner' --assignee $admin --scope $data_storage_account_id

	if [ $ADLS == 'y' ]
	then
    echo "+ Data Lake Store (Owner): "$admin
    az role assignment create --role 'Owner' --assignee $admin --scope $data_lake_storage_account_id
    fi

    # add access to view the keys, including delete keys or delete or purge secrets
    echo "+ Set Key Vault Policy: "$admin
    az keyvault set-policy --name $key_vault_name --resource-group $resourcegroup_name --upn $admin \
    --key-permissions backup delete create decrypt encrypt get import list purge recover restore sign unwrapKey update verify wrapKey \
    --secret-permissions backup delete purge get list recover restore set
fi

##########
# ADD INDIVIDUAL USER
##########

if [[ -z $INDIDUAL_USER_LEAD ]]
then
	echo "no individual user to add"
else
  read -p  "Who else would you like to add? (e.g. user@domain.com) " OTHER_USER
  $user = "$OTHER_USER"
	#$user = $useralias + "@microsoft.com"
	echo "adding "$user" as Data Scientist"

	# grant reader permission for the team lead to the resource group
	az role assignment create --role 'Reader' --assignee $user  --resource-group $resourcegroup_name

	az ml workspace share -w $workspace_name -g $resourcegroup_name --role "Data Scientist" --user $admin

	az role assignment create --role 'Contributor' --assignee $user --scope $applicationInsights_provider
	az role assignment create --role 'Storage Blob Data Contributor' --assignee $user --scope $storageAccount_provider
	az role assignment create --role 'Contributor' --assignee $user --scope $keyVault_provider
	az role assignment create --role 'Contributor' --assignee $user --scope $containerRegistry_provider
	az role assignment create --role 'Storage Blob Data Contributor' --assignee $user --scope $data_storage_account_id
	if [ $ADLS == 'y' ]
	then
		az role assignment create --role 'Contributor' --assignee $user --scope $data_lake_storage_account_id
    fi

    # add access to view the keys, but not delete keys or delete or purge secrets
    az keyvault set-policy --name $key_vault_name --resource-group $resourcegroup_name --upn $user \
    --key-permissions backup create decrypt encrypt get import list purge recover restore sign unwrapKey update verify wrapKey \
    --secret-permissions backup get list recover, restore, set

fi

##########
# SET TEAM USING SECURITY GROUP
##########

if [[ -z $TEAM_SECURITY_GROUP ]]
then
	echo "no team to add"az
else
	echo "adding security group as contributors "$TEAM_SECURITY_GROUP
    az ad group show --group $TEAM_SECURITY_GROUP

    $group_id=$(az ad group show --group $TEAM_SECURITY_GROUP --query objectid)

    echo "adding security group "$group_id" to workspace "$workspace_name
    # az ml workspace share -w $workspace_name -g $resourcegroup_name --role "ML User" --user $group_id ## possibily fails

    az role assignment create --role 'Data Scientist' ---assignee-object-id  $group_id  --scope  $workspace_provider
	az role assignment create --role 'Contributor' --assignee-object-id  $group_id --scope $applicationInsights_provider
	az role assignment create --role 'Storage Blob Data Contributor' --assignee-object-id  $group_id --scope $storageAccount_provider
	az role assignment create --role 'Contributor' --assignee-object-id  $group_id --scope $keyVault_provider
	az role assignment create --role 'Contributor' --assignee-object-id  $group_id --scope $containerRegistry_provider
	az role assignment create --role 'Storage Blob Data Contributor' --assignee-object-id  $group_id --scope $data_storage_account_id

	if [ "$ADLS" == 'y' ]
	then
		az role assignment create --role 'Contributor'--assignee-object-id  $group_id --scope $data_lake_storage_account_id
    fi

    # add access to view the keys, but not delete keys or delete or purge secrets
    az keyvault set-policy --name $key_vault_name --resource-group $resourcegroup_name --object-id $group_id \
    --key-permissions backup create decrypt encrypt get import list purge recover restore sign unwrapKey update verify wrapKey \
    --secret-permissions backup get list recover, restore, set
fi

echo "Welcome to Azure Machine Learning Services "$admin
echo "Here are the variables you need to get started: "
echo "export SUBSCRIPTION_ID=\""$SUBSCRIPTION_ID"\""
echo "export RESOURCE_GROUP=\""$resourcegroup_name"\""
echo "export WORKSPACE_NAME=\""$workspace_name"\""
echo "export WORKSPACE_STORAGE_ACCOUNT=\""$workspace_storage_account_name"\""
echo
echo "Here are so additional resources for you"
echo "YOUR DATA STORAGE ACCOUNT: "$data_storage_account_name
echo "YOUR KEY VAULT: "$key_vault_name
if [ "$ADLS" == 'y' ]
then
    echo "YOUR DATA LAKE STORAGE ACCOUNT: "$data_lake_store_name
fi
echo
echo "done"
