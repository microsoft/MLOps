#!/bin/sh

## this script assigns users in an Azure Machine Learning service workspace to the Data Scientist role using the Azure CLI

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
echo "ADDING COMPUTE TO A WORKSPACE"

# eval $(parse_yaml config.yml "config_")
CUSTOM_YAML="$1"

## READ YAML file
if [ "$CUSTOM_YAML" != '' ]
then
  eval $(parse_yaml $CUSTOM_YAML "config_")
else
  eval $(parse_yaml config.yml "config_")
fi

SUBSCRIPTION_ID=${config_workspace_subscription}
CUSTOM_NAME=${config_workspace_custom_name}
DEPARTMENT_NAME=${config_workspace_department:0:4}
TEAM_NAME=${config_workspace_team:0:10}
LOCATION=${config_workspace_region}
LOCATION_ABBR=${config_workspace_region_abbv:0:2}
DEVENVIRONMENT=${config_workspace_environment:0:3}
TEAM_LEAD=${config_workspace_admin}
ADLS=${config_workspace_adls}


#########################
## Get Resource Names  ##
#########################

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

#workspace_name=${config_compute_workspace}
workspace_name=$resource_name"ws"

workspace_storage_account_name=$resource_name"work"
workspace_storage_account_name=${workspace_storage_account_name:0:23}

data_storage_account_name=$resource_name"data"
data_storage_account_name=${data_storage_account_name:0:23}

container_registry_name=$resource_name"cr"
container_registry_name=${container_registry_name:0:23}

key_vault_name=$resource_name"kv"
key_vault_name=${key_vault_name:0:23}

echo 'resourcegroup_name: '$resourcegroup_name
echo 'WORKSPACE: '$workspace_name

echo "resourcename: "$resource_name
echo "workspacename: "$workspace_name
echo "location: "$LOCATION
echo "location abbreviation: "$LOCATION_ABBR

az login
az account set --subscription $SUBSCRIPTION_ID

## validate resource group exists
resource_exists=$(az group exists --name $resourcegroup_name)
if [ "$resource_exists" == 'false' ]
then
	echo "resource group does not exist: " $resourcegroup_name
	exit 1
fi

#########################
## Get Workspace Info  ##
#########################

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


#########################
##	 Add Team Leads	   ##
#########################

## Parse user list to add to Team Lead role
IFS=', ()][' read -a teamleads <<<${config_roles_team_leads}

echo "Assigning "${#teamleads[@]}" users to Team Lead role..."

tlend=${#teamleads[@]}

for ((i=0; i<tlend; i++))
do
	admin=${teamleads[i]}
	
	echo "Adding Team Lead: "$admin
	echo "Resource Group: "$resourcegroup_name
	echo "Workspace: "$workspace_name

	

	## grant the team lead Reader permission for the team lead to the resource group
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
	data_storage_account_id=$(az storage account show -n $data_storage_account_name -g $resourcegroup_name --query id | tr -d '"')
	#data_storage_account_key=$(az storage account keys list -g $resourcegroup_name -n $data_storage_account_name --query [0].value | tr -d '"')
	az role assignment create --role 'Storage Blob Data Owner' --assignee $admin --scope $data_storage_account_id

	if [ "$ADLS" == 'y' ]
	then
		data_lake_store_name=$resource_name"big"
		data_lake_store_name=${data_lake_store_name:0:23}
		data_lake_storage_account_id=$(az storage account show -n $data_lake_store_name --query id | tr -d '"')
		#data_lake_storage_account_key=$(az storage account keys list -g $resourcegroup_name -n $data_lake_store_name --query [0].value | tr -d '"')
		echo "+ Data Lake Store (Owner): "$admin
		az role assignment create --role 'Owner' --assignee $admin --scope $data_lake_storage_account_id
    fi

    # add access to view the keys, including delete keys or delete or purge secrets
    echo "+ Set Key Vault Policy: "$admin
	az keyvault set-policy --name $key_vault_name --resource-group $resourcegroup_name --upn $admin \
    --key-permissions backup delete create decrypt encrypt get import list purge recover restore sign unwrapKey update verify wrapKey \
    --secret-permissions backup delete purge get list recover restore set
done


#########################
## Add Data Scientists ##
#########################

## Parse user list to add to Data Scientist role
IFS=', ()][' read -a datascientists <<<${config_roles_data_scientists}

echo "Assigning "${#datascientists[@]}" users to Data Scientist role..."

dsend=${#datascientists[@]}

for ((i=0; i<dsend; i++))
do
	user=${datascientists[i]}
	echo "Adding Data Scientist: "$user
	echo "Resource Group: "$resourcegroup_name
	echo "Workspace: "$workspace_name
	
	# grant reader permission for the team lead to the resource group
	az role assignment create --role 'Reader' --assignee $user  --resource-group $resourcegroup_name

	az ml workspace share -w $workspace_name -g $resourcegroup_name --role "Data Scientist" --user $admin

	az role assignment create --role 'Contributor' --assignee $user --scope $applicationInsights_provider
	az role assignment create --role 'Storage Blob Data Contributor' --assignee $user --scope $storageAccount_provider
	az role assignment create --role 'Contributor' --assignee $user --scope $keyVault_provider
	az role assignment create --role 'Contributor' --assignee $user --scope $containerRegistry_provider
	
	data_storage_account_id=$(az storage account show -n $data_storage_account_name -g $resourcegroup_name --query id | tr -d '"')
	#data_storage_account_key=$(az storage account keys list -g $resourcegroup_name -n $data_storage_account_name --query [0].value | tr -d '"')
	az role assignment create --role 'Storage Blob Data Contributor' --assignee $user --scope $data_storage_account_id
	
	if [ "$ADLS" == 'y' ]
	then
		data_lake_store_name=$resource_name"big"
		data_lake_store_name=${data_lake_store_name:0:23}
		data_lake_storage_account_id=$(az storage account show -n $data_lake_store_name --query id | tr -d '"')
		#data_lake_storage_account_key=$(az storage account keys list -g $resourcegroup_name -n $data_lake_store_name --query [0].value | tr -d '"')
		az role assignment create --role 'Contributor' --assignee $user --scope $data_lake_storage_account_id
    fi

    # add access to view the keys, but not delete keys or delete or purge secrets
    az keyvault set-policy --name $key_vault_name --resource-group $resourcegroup_name --upn $user \
    --key-permissions backup create decrypt encrypt get import list purge recover restore sign unwrapKey update verify wrapKey \
    --secret-permissions backup get list recover restore set
	
	
done


export WORKSPACE=\"$workspace_name\"
export SUBSCRIPTION_ID=\"$SUBSCRIPTION_ID\"
export CLUSTER_NAME=\"$computetarget_name\""
