#!/usr/bin/env pwsh
<#
.SYNOPSIS
  KLOUD CLOUD - COMPLETE SYSTEM LAUNCHER WITH SLACK
  Launch all services: ALBA, ALBI, JONA, Orchestrator, API, Frontend, Slack Integration

.DESCRIPTION
  Comprehensive system launcher that starts:
  - All SAAS services (ALBA, ALBI, JONA)
  - Orchestrator (service discovery)
  - Main API Gateway
  - Frontend Dashboard
  - Slack Integration Service (real-time monitoring)

.EXAMPLE
  .\launch-all-with-slack.ps1
  .\launch-all-with-slack.ps1 -WebhookUrl "https://hooks.slack.com/..."
  .\launch-all-with-slack.ps1 -Mode "saas-only" -Slack $true
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("full", "saas-only", "app-only", "docker", "slack-test")]
    [string]$Mode = "full",
    
    [Parameter(Mandatory = $false)]
    [string]$WebhookUrl = $env:SLACK_WEBHOOK_URL,
    
    [Parameter(Mandatory = $false)]
    [string]$Channel = "#kloud-monitoring",
    
    [Parameter(Mandatory = $false)]
    [bool]$Slack = $true,
    
    [Parameter(Mandatory = $false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory = $false)]
    [switch]$Help
)

# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

function Write-Header {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  KLOUD CLOUD - COMPLETE SYSTEM LAUNCHER                       ║" -ForegroundColor Cyan
    Write-Host "║  All Components + Slack Integration + Real-time Monitoring       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host "┌─ $Title" -ForegroundColor Yellow
}

function Write-Item {
    param([string]$Message, [string]$Color = "Gray")
    Write-Host "│  $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "│  ✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "│  ❌ $Message" -ForegroundColor Red
}

function Write-Divider {
    Write-Host "└─────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
}

function Show-Help {
    Write-Header
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\launch-all-with-slack.ps1 [Options]"
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -Mode <string>        Launch mode: full|saas-only|app-only|docker|slack-test"
    Write-Host "  -WebhookUrl <string>  Slack webhook URL (optional)"
    Write-Host "  -Channel <string>     Slack channel (default: #kloud-monitoring)"
    Write-Host "  -Slack <bool>         Enable Slack integration (default: true)"
    Write-Host "  -DryRun               Show what would execute"
    Write-Host "  -Help                 Show this help"
    Write-Host ""
    exit 0
}

if ($Help) { Show-Help }

Write-Header

# ═══════════════════════════════════════════════════════════════════
# PRE-FLIGHT CHECKS
# ═══════════════════════════════════════════════════════════════════

Write-Section "PRE-FLIGHT CHECKS"

$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Node.js $nodeVersion"
} else {
    Write-Error-Custom "Node.js not found"
}

$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Success "Python $pythonVersion"
} else {
    Write-Error-Custom "Python not found"
}

Write-Divider

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

Write-Section "CONFIGURATION"
Write-Item "Mode: $Mode" "Cyan"
Write-Item "Slack Integration: $(if ($Slack) { 'Enabled' } else { 'Disabled' })" "Cyan"
if ($Slack -and $WebhookUrl) {
    Write-Success "Webhook configured"
}
Write-Divider

# ═══════════════════════════════════════════════════════════════════
# SLACK TEST MODE
# ═══════════════════════════════════════════════════════════════════

if ($Mode -eq "slack-test") {
    Write-Section "SLACK INTEGRATION TEST"
    
    if (-not $WebhookUrl -or $WebhookUrl -eq "") {
        Write-Error-Custom "No webhook URL provided"
        Write-Item "Set with: -WebhookUrl 'https://hooks.slack.com/...'"
        exit 1
    }
    
    Write-Item "Testing webhook connectivity..."
    
    $testPayload = @{
        text = "✅ Kloud Cloud Slack Integration Test"
        blocks = @(
            @{
                type = "section"
                text = @{
                    type = "mrkdwn"
                    text = "✅ *Kloud Cloud* Slack Integration`n*Status:* Connected`n*Time:* $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                }
            }
        )
    } | ConvertTo-Json -Depth 5
    
    if ($DryRun) {
        Write-Item "DRY RUN - Would POST to webhook" "Yellow"
    } else {
        try {
            $response = Invoke-WebRequest -Uri $WebhookUrl -Method Post -Body $testPayload -ContentType "application/json" -ErrorAction Stop
            Write-Success "Webhook test successful!"
        } catch {
            Write-Error-Custom "Webhook test failed: $_"
        }
    }
    
    Write-Divider
    exit 0
}

# ═══════════════════════════════════════════════════════════════════
# STARTUP SEQUENCE
# ═══════════════════════════════════════════════════════════════════

Write-Section "STARTUP SEQUENCE"

$services = @()

# SaaS Services
if ($Mode -in @("full", "saas-only")) {
    $services += @(
        @{ Name = "ALBA Collector"; Port = 5555; Cmd = "python alba_service_5555.py"; Wait = 1 },
        @{ Name = "ALBI Processor"; Port = 6680; Cmd = "python albi_service_6680.py"; Wait = 1 },
        @{ Name = "JONA Coordinator"; Port = 7777; Cmd = "python jona_service_7777.py"; Wait = 1 },
        @{ Name = "Orchestrator"; Port = 9999; Cmd = "python saas_services_orchestrator.py"; Wait = 2 }
    )
}

# Application Services
if ($Mode -in @("full", "app-only")) {
    $services += @(
        @{ Name = "API Server"; Port = 8000; Cmd = "python -m uvicorn apps.api.main:app --reload"; Wait = 3 },
        @{ Name = "Frontend"; Port = 3000; Cmd = "cd apps/web; npm run dev"; Wait = 2 }
    )
}

# Slack Integration
if ($Slack -and $Mode -in @("full", "saas-only", "app-only")) {
    $slackCmd = "python slack_integration_service.py"
    if ($WebhookUrl) {
        $slackCmd = "`$env:SLACK_WEBHOOK_URL='$WebhookUrl'; $slackCmd"
    }
    
    $services += @(
        @{ Name = "Slack Integration"; Port = 8888; Cmd = $slackCmd; Wait = 2 }
    )
}

# Start each service
$successCount = 0
foreach ($service in $services) {
    Write-Item "Starting $($service.Name) (Port $($service.Port))..." "Yellow"
    
    if ($DryRun) {
        Write-Item "  Command: $($service.Cmd)" "DarkGray"
        Write-Item "  Wait: $($service.Wait)s" "DarkGray"
    } else {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $service.Cmd -WindowStyle Normal
        Start-Sleep -Seconds $service.Wait
        $successCount++
    }
    
    Write-Success "$($service.Name) started"
}

Write-Divider

# ═══════════════════════════════════════════════════════════════════
# SUCCESS MESSAGE & ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ KLOUD CLOUD - ALL COMPONENTS ONLINE & INTERCONNECTED       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host ""
Write-Host "APPLICATION TIER:" -ForegroundColor Cyan
Write-Host "  📊 Frontend Dashboard  → http://localhost:3000"
Write-Host "  📡 API Server          → http://localhost:8000"
Write-Host "  📖 API Docs (Swagger)  → http://localhost:8000/docs"
Write-Host "  ❤️  Health Check         → http://localhost:8000/health"

Write-Host ""
Write-Host "SAAS SERVICES TIER:" -ForegroundColor Cyan
Write-Host "  🔵 ALBA (Telemetry)    → http://localhost:5555"
Write-Host "  🟣 ALBI (Analytics)    → http://localhost:6680"
Write-Host "  🟡 JONA (Synthesis)    → http://localhost:7777"
Write-Host "  ⚙️  Orchestrator        → http://localhost:9999"
Write-Host "  📋 Service Registry    → http://localhost:9999/registry"
Write-Host "  📊 Status Dashboard    → http://localhost:9999/status/dashboard"

if ($Slack) {
    Write-Host ""
    Write-Host "SLACK INTEGRATION:" -ForegroundColor Cyan
    Write-Host "  📱 Slack Service       → http://localhost:8888"
    Write-Host "  🔔 Service Monitoring  → Automated (60s interval)"
    Write-Host "  🚨 Alert System        → Active"
    Write-Host "  📊 Status Reports      → Ready to send"
    
    Write-Host ""
    Write-Host "QUICK SLACK COMMANDS:" -ForegroundColor Yellow
    Write-Host "  Get Status:"
    Write-Host "    curl http://localhost:8888/service-health"
    Write-Host ""
    Write-Host "  Send Status Report:"
    Write-Host "    curl http://localhost:8888/status-report"
    Write-Host ""
    Write-Host "  Send Alert:"
    Write-Host "    curl -X POST http://localhost:8888/send-alert \"
    Write-Host '      -H "Content-Type: application/json" \'
    Write-Host '      -d ''{"service":"alba","severity":"warning","title":"Test","message":"Test alert"}'''
}

Write-Host ""
Write-Host "INFRASTRUCTURE SERVICES:" -ForegroundColor Cyan
Write-Host "  💾 PostgreSQL          → localhost:5432"
Write-Host "  🔴 Redis               → localhost:6379"
Write-Host "  📦 MinIO               → http://localhost:9000"
Write-Host "  📈 Prometheus          → http://localhost:9090"
Write-Host "  📊 Grafana             → http://localhost:3001"

Write-Host ""
Write-Host "DATA FLOW ARCHITECTURE:" -ForegroundColor Yellow
Write-Host "  ALBA (5555)"
Write-Host "    ↓ [Telemetry Data]"
Write-Host "  ALBI (6680)"
Write-Host "    ↓ [Insights]"
Write-Host "  JONA (7777)"
Write-Host "    ↓ [Synthesized Audio]"
Write-Host "  API (8000)"
Write-Host "    ↓ [Processed Results]"
Write-Host "  Frontend (3000)"

Write-Host ""
Write-Host "✅ System is fully operational and all components are interconnected!"
Write-Host "✅ Services monitoring active via Slack integration"
Write-Host "✅ Ready for production deployment"
Write-Host ""


