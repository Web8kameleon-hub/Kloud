# ============================================================
# KLOUD 75 MICROSERVICES - DOCKER STARTUP SCRIPT
# Data: 30 Janar 2026
# ============================================================

param(
    [switch]$Build,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Logs,
    [string]$Service = ""
)

$ErrorActionPreference = "Continue"
$ComposeFile = "docker-compose.75-microservices.yml"

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║           KLOUD CLOUD - 75 MICROSERVICES                 ║
║                   Docker Manager v1.0                        ║
╠══════════════════════════════════════════════════════════════╣
║  Categories:                                                 ║
║    - Databases (5)      - AI & Ollama (3)                   ║
║    - ASI Trinity (4)    - Core Engines (7)                  ║
║    - Personas (1)       - AGIEM & DataSources (9)           ║
║    - Laboratories (23)  - SaaS & Marketplace (3)            ║
║    - Services (8)       - Frontend & Gateway (3)            ║
║    - Monitoring (5)     - Cognitive & Additional (4)        ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check if docker is running
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker is not running! Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

if ($Stop) {
    Write-Host "`n🛑 Stopping all 75 containers..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile down
    Write-Host "✅ All containers stopped." -ForegroundColor Green
    exit 0
}

if ($Status) {
    Write-Host "`n📊 Container Status:" -ForegroundColor Yellow
    docker-compose -f $ComposeFile ps
    
    $running = (docker-compose -f $ComposeFile ps -q 2>$null | Measure-Object).Count
    Write-Host "`n📈 Running: $running / 75 containers" -ForegroundColor Cyan
    exit 0
}

if ($Logs) {
    if ($Service) {
        Write-Host "`n📝 Logs for $Service :" -ForegroundColor Yellow
        docker-compose -f $ComposeFile logs -f $Service
    } else {
        Write-Host "`n📝 Logs for all services:" -ForegroundColor Yellow
        docker-compose -f $ComposeFile logs -f --tail=100
    }
    exit 0
}

# Default: Start containers
Write-Host "`n🚀 Starting 75 Microservices..." -ForegroundColor Green

if ($Build) {
    Write-Host "🔨 Building containers first..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile build
}

# Start in phases to avoid overwhelming resources
Write-Host "`n📦 Phase 1: Starting Infrastructure (Databases + AI)..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d postgres redis neo4j victoriametrics minio ollama

Start-Sleep -Seconds 5

Write-Host "📦 Phase 2: Starting AI Services..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d ollama-multi-api ocean-core

Start-Sleep -Seconds 3

Write-Host "📦 Phase 3: Starting ASI Trinity + Core Engines..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d alba albi jona asi
docker-compose -f $ComposeFile up -d alphabet-layers liam alda alba-idle blerina cycle-engine saas-orchestrator

Start-Sleep -Seconds 2

Write-Host "📦 Phase 4: Starting Personas + AGIEM + DataSources..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d personas agiem
docker-compose -f $ComposeFile up -d datasource-europe datasource-americas datasource-asia datasource-india datasource-africa datasource-oceania datasource-central-asia datasource-antarctica

Start-Sleep -Seconds 2

Write-Host "📦 Phase 5: Starting Laboratories (23)..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d `
    lab-elbasan lab-tirana lab-durres lab-vlore lab-shkoder lab-korce lab-saranda `
    lab-prishtina lab-kostur lab-athens lab-rome lab-zurich lab-beograd lab-sofia `
    lab-zagreb lab-ljubljana lab-vienna lab-prague lab-budapest lab-bucharest `
    lab-istanbul lab-cairo lab-jerusalem

Start-Sleep -Seconds 2

Write-Host "📦 Phase 6: Starting Services + SaaS..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d saas-api marketplace economy
docker-compose -f $ComposeFile up -d reporting excel behavioral analytics neurosonix aviation multi-tenant quantum

Start-Sleep -Seconds 2

Write-Host "📦 Phase 7: Starting Frontend + Monitoring + Cognitive..." -ForegroundColor Cyan
docker-compose -f $ComposeFile up -d api web traefik
docker-compose -f $ComposeFile up -d prometheus grafana loki jaeger tempo
docker-compose -f $ComposeFile up -d agent-telemetry cognitive-engine adaptive-router health-monitor

Write-Host "`n" -NoNewline
Write-Host "═" * 60 -ForegroundColor Green
Write-Host "✅ ALL 75 MICROSERVICES STARTED!" -ForegroundColor Green
Write-Host "═" * 60 -ForegroundColor Green

Write-Host "`n📊 Quick Status Check:" -ForegroundColor Cyan
$running = (docker-compose -f $ComposeFile ps -q 2>$null | Measure-Object).Count
Write-Host "   Running Containers: $running / 75" -ForegroundColor Yellow

Write-Host "`n🌐 Key URLs:" -ForegroundColor Cyan
Write-Host "   • API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "   • Web Frontend:    http://localhost:3000" -ForegroundColor White
Write-Host "   • Ocean Core:      http://localhost:8030" -ForegroundColor White
Write-Host "   • Ollama Multi:    http://localhost:4444" -ForegroundColor White
Write-Host "   • Grafana:         http://localhost:3001" -ForegroundColor White
Write-Host "   • Health Monitor:  http://localhost:8099" -ForegroundColor White

Write-Host "`n📝 Commands:" -ForegroundColor Cyan
Write-Host "   • Status: .\start-docker-75.ps1 -Status" -ForegroundColor White
Write-Host "   • Stop:   .\start-docker-75.ps1 -Stop" -ForegroundColor White
Write-Host "   • Logs:   .\start-docker-75.ps1 -Logs" -ForegroundColor White
Write-Host "   • Logs [service]: .\start-docker-75.ps1 -Logs -Service alba" -ForegroundColor White

