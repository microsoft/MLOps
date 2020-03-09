param(
    [parameter(Mandatory=$true)]
    $ResourceGroupName,
    [parameter(Mandatory=$true)]
    $DataFactoryName,
    [parameter(Mandatory=$true)]
    $PipelineName
)

Import-Module "$($PSScriptRoot)\Utilities.psm1"

$runId = Invoke-AzDataFactoryV2Pipeline -ResourceGroupName $ResourceGroupName -DataFactoryName $DataFactoryName -PipelineName $PipelineName

Write-Host "##vso[task.setvariable variable=AdfPipeline.RunId]$($runId)"

$runDetails = Get-AzDataFactoryV2PipelineRun -ResourceGroupName $ResourceGroupName -DataFactoryName $DataFactoryName -PipelineRunId $runId

while ($runDetails.Status -eq "InProgress") {
    LogInfo "Waiting for the ADF Pipeline $($runDetails.PipelineName) to finish..."

    Start-Sleep -Seconds 5
    
    $runDetails = Get-AzDataFactoryV2PipelineRun -ResourceGroupName $ResourceGroupName -DataFactoryName $DataFactoryName -PipelineRunId $runId
}

if ($runDetails.Status -eq "Succeeded") {
    LogInfo "Data Factory Pipeline $($runDetails.PipelineName) succeeded!"
}
else {
    LogError "Data Factory Pipeline $($runDetails.PipelineName) failed: $($runDetails.Message)"
    throw "Error executing the ADF Pipeline. Check the message above for details."
}