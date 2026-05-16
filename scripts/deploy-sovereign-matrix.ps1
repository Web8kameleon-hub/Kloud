#!/usr/bin/env pwsh
<#!
.SYNOPSIS
  Deploy Kloud sovereign stack by node role/profile across Hetzner fabric.

.DESCRIPTION
  Uses docker compose profiles from docker-compose.backend-5-sovereign.yml and
  deploys to one node or all nodes over SSH.

.EXAMPLE
  ./scripts/deploy-sovereign-matrix.ps1 -Target all
  ./scripts/deploy-sovereign-matrix.ps1 -Target compute-fsk -NoBuild
  ./scripts/deploy-sovereign-matrix.ps1 -Target ocean-hq -ComposeFile docker-compose.backend-5-sovereign.yml
    ./scripts/deploy-sovereign-matrix.ps1 -Target compute-fsk -Mode ValidateOnly
    ./scripts/deploy-sovereign-matrix.ps1 -Target ocean-hq -Mode Takeover -NoBuild
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet("all", "ocean-hq", "compute-fsk", "failover-nbg", "edge-hel", "edge-ash", "edge-sin")]
    [string]$Target = "all",

    [Parameter()]
    [string]$ComposeFile = "docker-compose.backend-5-sovereign.yml",

    [Parameter()]
    [string]$RemotePath = "/opt/kloud",

    [Parameter()]
    [string]$SshUser = "root",

    [Parameter()]
    [string]$SshKeyPath = "$HOME/.ssh/id_ed25519_nopwd",

    [Parameter()]
    [switch]$NoBuild,

    [Parameter()]
    [switch]$SkipGitPull,

    [Parameter()]
    [ValidateSet("Deploy", "ValidateOnly", "Takeover")]
    [string]$Mode = "Deploy"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "! $Message" -ForegroundColor Yellow
}

$nodeMap = @{
    "ocean-hq"     = @{ ip = "178.105.52.245"; profile = "hq" }
    "compute-fsk"  = @{ ip = "91.98.47.131"; profile = "compute" }
    "failover-nbg" = @{ ip = "46.224.203.89"; profile = "failover" }
    "edge-hel"     = @{ ip = "37.27.216.254"; profile = "edge" }
    "edge-ash"     = @{ ip = "5.161.114.189"; profile = "edge" }
    "edge-sin"     = @{ ip = "5.223.75.178"; profile = "edge" }
}

if (-not (Test-Path $ComposeFile)) {
    throw "Compose file not found: $ComposeFile"
}

if (-not (Test-Path $SshKeyPath)) {
    throw "SSH key not found: $SshKeyPath"
}

$targets = @()
if ($Target -eq "all") {
    $targets = @("ocean-hq", "compute-fsk", "failover-nbg", "edge-hel", "edge-ash", "edge-sin")
} else {
    $targets = @($Target)
}

Write-Info "Validating compose config locally..."
docker compose -f $ComposeFile config --quiet
Write-Ok "Compose config is valid"

foreach ($node in $targets) {
    $cfg = $nodeMap[$node]
    $ip = [string]$cfg.ip
    $profile = [string]$cfg.profile
    $sshTarget = "$SshUser@$ip"

    Write-Host ""
    Write-Host "==================================================" -ForegroundColor DarkCyan
    $actionLabel = switch ($Mode) {
        "ValidateOnly" { "Validating" }
        "Takeover" { "Takeover deploy" }
        default { "Deploying" }
    }
    Write-Host "$actionLabel $node ($ip) with profile '$profile'" -ForegroundColor Magenta
    Write-Host "==================================================" -ForegroundColor DarkCyan

    $upFlags = if ($NoBuild) { "-d --no-build --remove-orphans" } else { "-d --build --remove-orphans" }
    $upFlagsFallback = $upFlags

    Write-Info "Syncing compose file to ${sshTarget}:$RemotePath/$ComposeFile"
    & ssh -i $SshKeyPath -o BatchMode=yes -o StrictHostKeyChecking=accept-new $sshTarget "mkdir -p '$RemotePath'"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to prepare remote path for $node ($sshTarget)"
    }
    & scp -i $SshKeyPath -o BatchMode=yes -o StrictHostKeyChecking=accept-new $ComposeFile "${sshTarget}:$RemotePath/$ComposeFile"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upload compose file for $node ($sshTarget)"
    }

    $pullCmd = if ($SkipGitPull) {
        "echo 'Skip git pull as requested'"
    } else {
        "if [ -d .git ]; then git pull --ff-only; else echo 'No git repo in remote path, skip pull'; fi"
    }

    $remoteScript = switch ($Mode) {
        "ValidateOnly" {
            (
                "set -e; " +
                "if docker compose version >/dev/null 2>&1; then COMPOSE='docker compose'; " +
                "elif command -v docker-compose >/dev/null 2>&1; then COMPOSE='docker-compose'; " +
                "else echo 'Docker Compose not found'; exit 127; fi; " +
                "cd '$RemotePath'; " +
                "$pullCmd; " +
                "`$COMPOSE -f '$ComposeFile' --profile '$profile' config --quiet; " +
                "echo REMOTE_PROFILE_OK"
            )
        }
        "Takeover" {
            (
                "set -e; " +
                "if docker compose version >/dev/null 2>&1; then COMPOSE='docker compose'; " +
                "elif command -v docker-compose >/dev/null 2>&1; then COMPOSE='docker-compose'; " +
                "else echo 'Docker Compose not found'; exit 127; fi; " +
                "cd '$RemotePath'; " +
                "$pullCmd; " +
                "if [ -f docker-compose.yml ]; then `$COMPOSE -f docker-compose.yml down --remove-orphans || true; fi; " +
                "if ! `$COMPOSE -f '$ComposeFile' --profile '$profile' up $upFlags; then " +
                "echo 'Primary compose command failed, trying COMPOSE_PROFILES fallback'; " +
                "COMPOSE_PROFILES='$profile' `$COMPOSE -f '$ComposeFile' up $upFlagsFallback; " +
                "fi; " +
                "`$COMPOSE -f '$ComposeFile' ps"
            )
        }
        default {
            (
                "set -e; " +
                "if docker compose version >/dev/null 2>&1; then COMPOSE='docker compose'; " +
                "elif command -v docker-compose >/dev/null 2>&1; then COMPOSE='docker-compose'; " +
                "else echo 'Docker Compose not found'; exit 127; fi; " +
                "cd '$RemotePath'; " +
                "$pullCmd; " +
                "if ! `$COMPOSE -f '$ComposeFile' --profile '$profile' up $upFlags; then " +
                "echo 'Primary compose command failed, trying COMPOSE_PROFILES fallback'; " +
                "COMPOSE_PROFILES='$profile' `$COMPOSE -f '$ComposeFile' up $upFlagsFallback; " +
                "fi; " +
                "`$COMPOSE -f '$ComposeFile' ps"
            )
        }
    }

    Write-Info "Running remote deploy commands on $sshTarget"
    & ssh -i $SshKeyPath -o BatchMode=yes -o StrictHostKeyChecking=accept-new $sshTarget $remoteScript
    if ($LASTEXITCODE -ne 0) {
        throw "Remote deployment failed for $node ($sshTarget) with exit code $LASTEXITCODE"
    }
    Write-Ok "Deployment complete for $node"
}

Write-Host ""
Write-Ok "Sovereign matrix deployment finished"
