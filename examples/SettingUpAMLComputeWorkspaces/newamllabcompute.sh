#!/bin/sh

## this script creates a compute context for the Azure Machine Learning service workspace using the Azure CLI

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

#NODES=${config_compute_nodes}
IFS=', ()][' read -a NODES <<<${config_compute_nodes}
#PRIORITY=${config_compute_priority}
IFS=', ()][' read -a PRIORITY <<<${config_compute_priority}
#vm_size=${config_compute_vm_sku}
IFS=', ()][' read -a vm_size <<<${config_compute_vm_sku}

#resourcegroup_name=$DEPARTMENT_NAME-$TEAM_NAME-$LOCATION-$DEVENVIRONMENT
#resource_name=$DEPARTMENT_NAME$TEAM_NAME$LOCATION$DEVENVIRONMENT

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

#priorityabbr=${PRIORITY:0:3}

##computetarget_name=${vm_size//_/-}"-cluster-"$LOCATION_ABBR-$priorityabbr
#config_compute_cluster_name=${config_compute_cluster_name//_/-}
#computetarget_name=${config_compute_cluster_name:0:15}
IFS=', ()][' read -a computetarget_name <<<${config_compute_cluster_name}

echo "Creating "${#computetarget_name[@]}" compute clusters..."

end=${#computetarget_name[@]}

for ((i=0; i<end; i++))
do
	echo "### Creating compute with the following... ###"
	echo "Cluster Name: "${computetarget_name[i]}
	echo "Maximum number of Nodes: "${NODES[i]}
	echo "VM Size: "${vm_size[i]}
	echo "Priority: "${PRIORITY[i]}
	echo "Resource Group: "$resourcegroup_name
	echo "Workspace: "$workspace_name
	echo "Admin: "$TEAM_LEAD
	#read -p "Review compute target. Press the enter key to continue " -n1 -s
	#echo

	az ml computetarget create amlcompute --name ${computetarget_name[i]} \
		--max-nodes ${NODES[i]} --vm-size ${vm_size[i]} \
		--workspace-name $workspace_name --idle-seconds-before-scaledown 1800 \
		--vm-priority ${PRIORITY[i]} --resource-group $resourcegroup_name -v \
		--admin-username $TEAM_LEAD --admin-user-password $workspace_name

	az ml computetarget show --name ${computetarget_name[i]} \
		--workspace-name $workspace_name --resource-group $resourcegroup_name -v

	tag=${vm_size[i]}_${PRIORITY[i]}=${NODES[i]}
	az resource update --resource-group $resourcegroup_name --name $workspace_name \
		--resource-type "Microsoft.MachineLearningServices/workspaces" --set tags.$tag

	az ml workspace show --resource-group $resourcegroup_name --workspace-name $workspace_name

	az ml computetarget list --resource-group $resourcegroup_name --workspace-name $workspace_name
done

echo "For your users to use in the orientation lab:"
echo "export RESOURCE_GROUP=\"$resourcegroup_name\"
export WORKSPACE=\"$workspace_name\"
export SUBSCRIPTION_ID=\"$SUBSCRIPTION_ID\"
export CLUSTER_NAME=\"$computetarget_name\""
