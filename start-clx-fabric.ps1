$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env.fabric.local")) {
    Write-Host "Missing .env.fabric.local. Copy .env.fabric.local.example and set real local values." -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting Kloud with CLX fabric override..." -ForegroundColor Cyan
$services = @(
    "clx",
    "clx-i",
    "alba",
    "albi",
    "jona",
    "curiosity",
    "web",
    "ai-global-9999",
    "traefik"
)
docker compose -f docker-compose.yml -f docker-compose.clx.fabric.yml up -d --build --no-deps $services

Write-Host "CLX inference services are included in this startup profile." -ForegroundColor Cyan

Write-Host "Service snapshot:" -ForegroundColor Cyan
docker compose -f docker-compose.yml -f docker-compose.clx.fabric.yml ps
