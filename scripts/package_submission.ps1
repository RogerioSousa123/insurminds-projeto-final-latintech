$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$artifactDir = Join-Path $projectRoot "Projeto_Final_Artefatos"
$stageDir = Join-Path ([System.IO.Path]::GetTempPath()) ("insurminds_package_" + [guid]::NewGuid().ToString("N"))
$zipPath = Join-Path $artifactDir "InsurMinds_Projeto_Final_Codigo.zip"

New-Item -ItemType Directory -Path $stageDir | Out-Null
try {
    $excluded = @(".venv", ".git", ".pytest_cache", "__pycache__", "data", ".env", "InsurMinds_Projeto_Final_Codigo.zip")
    Get-ChildItem -LiteralPath $projectRoot -Force | Where-Object { $_.Name -notin $excluded } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $stageDir -Recurse -Force
    }
    Get-ChildItem -LiteralPath $stageDir -Recurse -Force -File | Where-Object { $_.Name.StartsWith('~$') } | ForEach-Object {
        $lockPath = [System.IO.Path]::GetFullPath($_.FullName)
        $resolvedStage = [System.IO.Path]::GetFullPath($stageDir)
        if ($lockPath.StartsWith($resolvedStage + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $lockPath -Force
        }
    }
    $stagedPreviousZip = Join-Path $stageDir "Projeto_Final_Artefatos\InsurMinds_Projeto_Final_Codigo.zip"
    if (Test-Path -LiteralPath $stagedPreviousZip) {
        Remove-Item -LiteralPath $stagedPreviousZip -Force
    }
    Compress-Archive -Path (Join-Path $stageDir "*") -DestinationPath $zipPath -Force
    Write-Host "Pacote criado: $zipPath"
}
finally {
    $resolvedTemp = [System.IO.Path]::GetFullPath($stageDir)
    $tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
    if ($resolvedTemp.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $resolvedTemp)) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
