#!/usr/bin/env pwsh

<#
╔════════════════════════════════════════════════════════════════════╗
║     KLOUD CLOUD - COMPLETE SYSTEM LAUNCHER                      ║
║     Launches all components: API, Frontend, ALBA, ALBI, JONA       ║
║     Port Layout: 3000 (FE), 8000 (API), 5555-7777 (SaaS)          ║
╚════════════════════════════════════════════════════════════════════╝
#>

param(
    [ValidateSet("full", "saas-only", "app-only", "docker")]
    [string]$Mode = "full",
    
    [switch]$DryRun = $false,
    [switch]$Verbose = $false
)

$Root = (Get-Location).Path
$StartTime = Get-Date

# ═══════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

function Write-Header {
    param([string]$Text)
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $($Text.PadRight(40))  ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝`n" -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Text)
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] $Text" -ForegroundColor Green
}

function Write-Info {
    param([string]$Text)
    Write-Host "  ℹ  $Text" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Text)
    Write-Host "  ✓ $Text" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "  ✗ $Text" -ForegroundColor Red
}

function Test-Port {
    param([int]$Port)
    try {
        $Connection = Test-NetConnection -ComputerName localhost -Port $Port -ErrorAction SilentlyContinue
        return $Connection.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

function Kill-ProcessOnPort {
    param([int]$Port)
    try {
        $Process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($Process) {
            Stop-Process -Id $Process.OwningProcess -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Write-Success "Freed port $Port"
        }
    }
    catch {
        # Port already free
    }
}

function Ensure-Dependencies {
    Write-Section "Checking dependencies..."
    
    # Node.js
    $Node = node --version 2>&1
    if ($?) {
        Write-Success "Node.js: $Node"
    }
    else {
        Write-Error-Custom "Node.js not found - install from nodejs.org"
        exit 1
    }
    
    # Python
    $Python = python --version 2>&1
    if ($?) {
        Write-Success "Python: $Python"
    }
    else {
        Write-Error-Custom "Python not found - install from python.org"
        exit 1
    }
    
    # npm modules
    Write-Info "Checking npm dependencies..."
    npm list -g npm 2>&1 | Out-Null
    if ($?) {
        Write-Success "npm modules available"
    }
}

function Start-Services {
    Write-Section "Cleaning up existing processes..."
    
    $Ports = @(3000, 8000, 5555, 6680, 7777, 9999)
    foreach ($Port in $Ports) {
        if (Test-Port $Port) {
            Write-Info "Port $Port in use - attempting cleanup..."
            Kill-ProcessOnPort $Port
        }
    }
    
    Start-Sleep -Seconds 2
    
    # ═════════════════════════════════════════════════════════════
    # API Service (8000)
    # ═════════════════════════════════════════════════════════════
    
    if ($Mode -in @("full", "app-only")) {
        Write-Section "Starting API Server (Port 8000)..."
        $APICommand = {
            Set-Location $using:Root
            Write-Host "[API] Starting Uvicorn..."
            python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000 2>&1
        }
        
        if ($DryRun) {
            Write-Info "[DRY-RUN] Would execute: python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000"
        }
        else {
            Start-Process pwsh -ArgumentList @('-NoExit', '-Command', "& {$APICommand}")
            Start-Sleep -Seconds 3
            Write-Success "API Server started"
        }
    }
    
    # ═════════════════════════════════════════════════════════════
    # Frontend Service (3000)
    # ═════════════════════════════════════════════════════════════
    
    if ($Mode -in @("full", "app-only")) {
        Write-Section "Starting Frontend (Port 3000)..."
        $FrontendCommand = {
            Set-Location "$using:Root/apps/web"
            $env:NEXT_PUBLIC_API_BASE = "http://localhost:8000"
            $env:NEXT_PUBLIC_ORCHESTRATOR_URL = "http://localhost:9999"
            Write-Host "[FRONTEND] Starting Next.js..."
            npm run dev 2>&1
        }
        
        if ($DryRun) {
            Write-Info "[DRY-RUN] Would execute: npm run dev (in apps/web)"
        }
        else {
            Start-Process pwsh -ArgumentList @('-NoExit', '-Command', "& {$FrontendCommand}")
            Start-Sleep -Seconds 3
            Write-Success "Frontend started"
        }
    }
    
    # ═════════════════════════════════════════════════════════════
    # SAAS SERVICES (5555-7777)
    # ═════════════════════════════════════════════════════════════
    
    if ($Mode -in @("full", "saas-only")) {
        Write-Section "Starting ALBA Collector Service (Port 5555)..."
        $AlbaCommand = {
            Set-Location $using:Root
            Write-Host "[ALBA] Starting service..."
            python alba_service_5555.py 2>&1
        }
        
        if ($DryRun) {
            Write-Info "[DRY-RUN] Would execute: python alba_service_5555.py"
        }
        else {
            Start-Process pwsh -ArgumentList @('-NoExit', '-Command', "& {$AlbaCommand}")
            Start-Sleep -Seconds 2
            Write-Success "ALBA service started"
        }
        
        Write-Section "Starting ALBI Processor Service (Port 6680)..."
        $AlbiCommand = {
            Set-Location $using:Root
            Write-Host "[ALBI] Starting service..."
            python albi_service_6680.py 2>&1
        }
        
        if ($DryRun) {
            Write-Info "[DRY-RUN] Would execute: python albi_service_6680.py"
        }
        else {
            Start-Process pwsh -ArgumentList @('-NoExit', '-Command', "& {$AlbiCommand}")
            Start-Sleep -Seconds 2
            Write-Success "ALBI service started"
        }
        
        Write-Section "Starting JONA Coordinator Service (Port 7777)..."
        $JonaCommand = {
            Set-Location $using:Root
            Write-Host "[JONA] Starting service..."
            python jona_service_7777.py 2>&1
        }
        
        if ($DryRun) {
            Write-Info "[DRY-RUN] Would execute: python jona_service_7777.py"
        }
        else {
            Start-Process pwsh -ArgumentList @('-NoExit', '-Command', "& {$JonaCommand}")
            Start-Sleep -Seconds 2
            Write-Success "JONA service started"
        }
        
        Write-Section "Starting SAAS Orchestrator (Port 9999)..."
        $OrchestratorCommand = {
            Set-Location $using:Root
            Write-Host "[ORCHESTRATOR] Starting service..."
            python saas_services_orchestrator.py 2>&1
        }
        
        if ($DryRun) {
            Write-Info "[DRY-RUN] Would execute: python saas_services_orchestrator.py"
        }
        else {
            Start-Process pwsh -ArgumentList @('-NoExit', '-Command', "& {$OrchestratorCommand}")
            Start-Sleep -Seconds 2
            Write-Success "Orchestrator started"
        }
    }
}

function Show-Dashboard {
    Write-Header "SYSTEM ONLINE - READY TO USE"
    
    Write-Host "📊 FRONTEND:" -ForegroundColor White
    Write-Host "   URL: http://localhost:3000" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📡 API SERVER:" -ForegroundColor White
    Write-Host "   URL: http://localhost:8000" -ForegroundColor Green
    Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "   Health: http://localhost:8000/health" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "⚙️  SAAS SERVICES:" -ForegroundColor White
    Write-Host "   ALBA (Collector):   http://localhost:5555" -ForegroundColor Green
    Write-Host "   ALBI (Processor):   http://localhost:6680" -ForegroundColor Green
    Write-Host "   JONA (Coordinator): http://localhost:7777" -ForegroundColor Green
    Write-Host "   Orchestrator:       http://localhost:9999" -ForegroundColor Green
    Write-Host "   Registry:           http://localhost:9999/registry" -ForegroundColor Green
    Write-Host "   Dashboard:          http://localhost:9999/status/dashboard" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📊 MONITORING:" -ForegroundColor White
    Write-Host "   Prometheus: http://localhost:9090" -ForegroundColor Green
    Write-Host "   Grafana:    http://localhost:3001" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "💾 DATABASE & CACHE:" -ForegroundColor White
    Write-Host "   PostgreSQL: localhost:5432" -ForegroundColor Green
    Write-Host "   Redis:      localhost:6379" -ForegroundColor Green
    Write-Host "   MinIO:      http://localhost:9000" -ForegroundColor Green
    Write-Host ""
    
    $Elapsed = (Get-Date) - $StartTime
    Write-Host "⏱️  Startup time: $($Elapsed.TotalSeconds) seconds" -ForegroundColor Yellow
    Write-Host ""
}

function Show-Help {
    Write-Header "KLOUD LAUNCHER - USAGE"
    Write-Host "Modes:" -ForegroundColor Yellow
    Write-Host "  full        - All services (API, Frontend, ALBA, ALBI, JONA, Orchestrator)" -ForegroundColor Cyan
    Write-Host "  saas-only   - Only SaaS services (ALBA, ALBI, JONA, Orchestrator)" -ForegroundColor Cyan
    Write-Host "  app-only    - Only application (API, Frontend)" -ForegroundColor Cyan
    Write-Host "  docker      - Docker Compose stack" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\launch-all.ps1                 # Full launch" -ForegroundColor Green
    Write-Host "  .\launch-all.ps1 -Mode saas-only # Only SaaS" -ForegroundColor Green
    Write-Host "  .\launch-all.ps1 -DryRun         # Preview commands" -ForegroundColor Green
}

# ═══════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════

Write-Header "KLOUD CLOUD - COMPLETE LAUNCHER"
Write-Info "Mode: $Mode"
Write-Info "Root: $Root"

if ($Verbose) {
    Write-Info "Verbose mode enabled"
}

if ($DryRun) {
    Write-Info "DRY-RUN mode - no actual processes will start"
}

Write-Section "Validating environment..."
Ensure-Dependencies

Write-Section "Starting services ($Mode mode)..."
Start-Services

if (!$DryRun) {
    Start-Sleep -Seconds 2
    Show-Dashboard
}

Write-Host ""
Write-Host "Press Ctrl+C to stop services" -ForegroundColor Yellow
Write-Host ""


