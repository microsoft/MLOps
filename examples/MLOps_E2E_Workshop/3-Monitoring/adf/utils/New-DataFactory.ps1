param(
    [string]$DataFactoryName,
    [string]$ResourceGroupName,
    [string]$Location
)

Import-Module "$($PSScriptRoot)\Utilities.psm1"

LogInfo "Creating Data Factory [$($DataFactoryName)] in Resource Group [$($ResourceGroupName)]..."
if ((Get-AzDataFactoryV2 -Name $DataFactoryName -ResourceGroupName $ResourceGroupName -ErrorAction SilentlyContinue) -eq $null)
{
    LogInfo "`tData Factory [$($DataFactoryName)] Does Not Exist.  Creating..."

    Set-AzDataFactoryV2 `
        -Name $DataFactoryName `
        -Location $Location `
        -ResourceGroupName $ResourceGroupName

    LogInfo "`tData Factory [$($DataFactoryName)] Created!"

}
else
{
    LogInfo "`tData Factory [$($DataFactoryName)] Exists.  Moving On!"
}
