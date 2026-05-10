$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$launcher = Join-Path $repoRoot "scripts\use-isolated-env.ps1"

$command = @(
    "Set-Location '$repoRoot'"
    "& '$launcher' -Quiet yarn --cwd apps/web dev"
)

$process = Start-Process -FilePath "pwsh" `
    -ArgumentList @(
    "-NoLogo",
    "-NoProfile",
    "-NoExit",
    "-Command",
    ($command -join "; ")
) `
    -WorkingDirectory $repoRoot `
    -PassThru

Write-Host ("Started Yarn Berry frontend in external PowerShell window. PID: {0}" -f $process.Id)