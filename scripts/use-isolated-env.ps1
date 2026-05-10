param(
    [switch]$Quiet,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Command
)

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$isolatedEnv = @{
    NPM_CONFIG_CACHE  = (Join-Path $repoRoot ".npm-cache")
    YARN_CACHE_FOLDER = (Join-Path $repoRoot ".yarn\cache")
    PIP_CACHE_DIR     = (Join-Path $repoRoot ".pip-cache")
    UV_CACHE_DIR      = (Join-Path $repoRoot ".uv-cache")
    CARGO_HOME        = (Join-Path $repoRoot ".cargo-home")
}

foreach ($entry in $isolatedEnv.GetEnumerator()) {
    Set-Item -Path ("Env:{0}" -f $entry.Key) -Value $entry.Value
    if (-not (Test-Path $entry.Value)) {
        New-Item -ItemType Directory -Path $entry.Value -Force | Out-Null
    }
}

if (-not $Quiet) {
    Write-Host "Isolated package environment enabled:" -ForegroundColor Cyan
    foreach ($entry in $isolatedEnv.GetEnumerator() | Sort-Object Key) {
        Write-Host "  $($entry.Key)=$($entry.Value)"
    }
}

if ($Command.Count -gt 0) {
    $commandName = $Command[0]
    $commandArgs = @()
    if ($Command.Count -gt 1) {
        $commandArgs = $Command[1..($Command.Count - 1)]
    }

    & $commandName @commandArgs
    exit $LASTEXITCODE
}