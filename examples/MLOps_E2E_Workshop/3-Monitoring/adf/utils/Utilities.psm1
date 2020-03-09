function LogInfo {
    param ($Text)

    WriteToConsole -Text $Text -LogLevel "Info" -ForegroundColor White
}

function LogError {
    param ($Text)

    WriteToConsole -Text $Text -LogLevel "Error" -ForegroundColor Red
}

function LogWarning {
    param ($Text)

    WriteToConsole -Text $Text -LogLevel "Warn" -ForegroundColor Yellow
}

function WriteToConsole {
    param ($Text, $LogLevel, $ForegroundColor)

    Write-Host -ForegroundColor $ForegroundColor "[$(Get-Date)] [$($LogLevel)]`t$($Text)"
}

function Get-MDWResourceGroupName {
    param([parameter(Mandatory=$true)][string]$baseName)

    $resourceGroupName = "$($baseName)-RG"

    return $resourceGroupName
}

function Get-MDWVnetName {
    param([parameter(Mandatory=$true)][string]$baseName)
    
    $vnetName = "$($baseName)-VNet"

    return $vnetName
}

function Get-MDWKeyVaultName {
    param(
        [parameter(Mandatory=$true)][string]$baseName,
        [bool]$encrypted=$false
    )

    $keyVaultName = ""

    if(!$encrypted) {
        $keyVaultName = "$($baseName)-KV"
    } else {
        $keyVaultName = "$($baseName)-KV-Enc"
    }

    return $keyVaultName
}

function Get-MDWDataFactoryName{
    param([parameter(Mandatory=$true)][string]$baseName)

    $dataFactoryName = "$($baseName)-ADF"

    return $dataFactoryName
}

function Get-MDWNetworkSecurityGroupName {
    param([parameter(Mandatory=$true)][string]$baseName)

    $nsgName = "$($baseName)-ADB-NSG"

    return $nsgName
}