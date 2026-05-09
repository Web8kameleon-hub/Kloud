# Ultra-Industrial Docker Run Script
# Author: Ledjan Ahmati

param(
    [string]$ComposeFile = "docker-compose.yml",
    [string]$ProjectName = "Kloud-industrial",
    [switch]$Rebuild,
    [switch]$Audit,
    [switch]$Trace
)

Write-Host "[INFO] Starting Ultra-Industrial Docker Run..." -ForegroundColor Cyan
Write-Host "[INFO] Compose File: $ComposeFile" -ForegroundColor Yellow
Write-Host "[INFO] Project Name: $ProjectName" -ForegroundColor Yellow

if ($Rebuild) {
    Write-Host "[ACTION] Rebuilding Docker images..." -ForegroundColor Green
    docker compose -f $ComposeFile -p $ProjectName build
}

Write-Host "[ACTION] Starting Docker Compose..." -ForegroundColor Green
$runCmd = "docker compose -f $ComposeFile -p $ProjectName up"
if ($Audit) {
    Write-Host "[AUDIT] Audit mode enabled." -ForegroundColor Magenta
    $runCmd += " --log-level INFO"
}
if ($Trace) {
    Write-Host "[TRACE] Tracing enabled." -ForegroundColor Magenta
    $runCmd += " --trace"
}
Invoke-Expression $runCmd

Write-Host "[INFO] Docker Compose started. Monitoring containers..." -ForegroundColor Cyan

# Industrial Monitoring & Audit
Write-Host "[METRIKA] Gathering metrics..." -ForegroundColor Blue
$metrics = docker stats --no-stream
Write-Host $metrics

Write-Host "[AUDIT] Listing running containers..." -ForegroundColor Blue
$containers = docker ps
Write-Host $containers

Write-Host "[PROTECTION] Checking for failed containers..." -ForegroundColor Red
$failed = docker ps -a | Select-String "Exited"
if ($failed) {
    Write-Host "[ERROR] Some containers have failed!" -ForegroundColor Red
    Write-Host $failed
} else {
    Write-Host "[OK] All containers running healthy." -ForegroundColor Green
}

Write-Host "[COMPLIANCE] Ultra-Industrial Docker run complete." -ForegroundColor Cyan


