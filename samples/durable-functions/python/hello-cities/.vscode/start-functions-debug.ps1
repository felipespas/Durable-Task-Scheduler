Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

& .\.venv\Scripts\Activate.ps1

$env:languageWorkers__python__defaultExecutablePath = Join-Path $repoRoot ".venv\Scripts\python.exe"
$env:languageWorkers__python__arguments = "-m debugpy --listen 9091"
$env:AzureWebJobsSecretStorageType = "Files"

func host start
