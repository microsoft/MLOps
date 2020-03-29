# Deployment script for machine learning resources
# Run locally to debug changes in the resource configuration
# Use `deploy-infrastructure.yml` for automation of deployments.

# Prompt users for resource group and location
$resourceGroupName = Read-Host -Prompt "Provide a resource group name"
$location = Read-Host -Prompt "Provide a DC location"

# Create a Resource Group
New-AzResourceGroup -Name $resourceGroupName -Location $location

# Deploy Storage Account
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName `
  -TemplateFile $PSScriptRoot/../arm-templates/storage/template.json `
  -TemplateParameterFile $PSScriptRoot/../arm-templates/storage/parameters.dev.json

# Deploy Container Registry
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName `
  -TemplateFile $PSScriptRoot/../arm-templates/containerregistry/template.json `
  -TemplateParameterFile $PSScriptRoot/../arm-templates/containerregistry/parameters.dev.json

# Deploy Application Insights
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName `
  -TemplateFile $PSScriptRoot/../arm-templates/appinsights/template.json `
  -TemplateParameterFile $PSScriptRoot/../arm-templates/appinsights/parameters.dev.json

# Deploy Key Vault
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName `
  -TemplateFile $PSScriptRoot/../arm-templates/keyvault/template.json `
  -TemplateParameterFile $PSScriptRoot/../arm-templates/keyvault/parameters.dev.json

# Deploy Workspace
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName `
  -TemplateFile $PSScriptRoot/../arm-templates/mlworkspace/template.json `
  -TemplateParameterFile $PSScriptRoot/../arm-templates/mlworkspace/parameters.dev.json

# Deploy Compute
New-AzResourceGroupDeployment -ResourceGroupName $resourceGroupName `
-TemplateFile $PSScriptRoot/../arm-templates/mlcompute/template.json `
-TemplateParameterFile $PSScriptRoot/../arm-templates/mlcompute/parameters.dev.json
