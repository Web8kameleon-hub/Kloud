#!/usr/bin/env pwsh
<#
===============================================================================
                KLOUD CLOUD - START ALL SERVICES v3.0
                   Ultimate Service Launcher & Orchestrator

  Comprehensive launcher for all Kloud Cloud services with:
  - Intelligent startup sequencing
  - Health monitoring & auto-recovery
  - Multiple deployment modes
  - Real-time service status dashboard

  Usage:  .\start-all.ps1 -Mode full -Clean -Monitor
  Modes:  dev | prod | full | docker | saas | lite | diagnostics
===============================================================================
#>

param(
    [ValidateSet('dev', 'prod', 'full', 'docker', 'saas', 'lite', 'diagnostics', 'help')]
    [string]$Mode = 'full',
    
    [switch]$Clean,
    [switch]$DryRun,
    [switch]$Monitor,
    [switch]$Rebuild,
    [switch]$NoHealthCheck,
    [switch]$Help
)

# ===============================================================================
# CONFIGURATION
# ===============================================================================

$Script:Root = $PSScriptRoot
if (-not $Script:Root) { $Script:Root = Get-Location }
Set-Location $Script:Root

$Script:Config = @{
    Root = $Script:Root
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    LogFile = Join-Path $Script:Root "logs\startup-$(Get-Date -Format 'yyyy-MM-dd').log"
}

$Script:Colors = @{
    Title    = "Magenta"
    Success  = "Green"
    Warning  = "Yellow"
    Error    = "Red"
    Info     = "Cyan"
    Section  = "Blue"
    Accent   = "DarkCyan"
}

$Script:ServicePorts = @{
    "API"              = 8000
    "Frontend"         = 3000
    "ALBA"             = 5555
    "ALBI"             = 6680
    "JONA"             = 7777
    "Orchestrator"     = 9999
    "PostgreSQL"       = 5432
    "Redis"            = 6379
    "MinIO"            = 9000
    "MinIO-Console"    = 9001
    "Prometheus"       = 9090
    "Grafana"          = 3001
    "Loki"             = 3100
    "Victoria-Metrics" = 8428
    "ocean-core"       = 8030
    "Ollama"           = 11434
    "Ollama-Multi-API" = 4444
}

$Script:Services = @{
    Core = @(
        @{ Name = "API Server"; Script = "python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload"; Port = 8000; Priority = 1 }
        @{ Name = "Frontend"; Script = "cd apps\web; npm run dev"; Port = 3000; Priority = 2 }
    )
    AI = @(
        @{ Name = "Ollama Server"; Script = "ollama serve"; Port = 11434; Priority = 0; External = $true }
        @{ Name = "Ollama Multi API"; Script = "cd ocean-core; python ollama_multi_api.py"; Port = 4444; Priority = 1; File = "ocean-core\ollama_multi_api.py" }
    )
    Microservices = @(
        @{ Name = "ALBA"; Script = "python alba_core.py"; Port = 5555; Priority = 3; File = "alba_core.py" }
        @{ Name = "ALBI"; Script = "python albi_core.py"; Port = 6680; Priority = 3; File = "albi_core.py" }
        @{ Name = "JONA"; Script = "python jona_service_7777.py"; Port = 7777; Priority = 3; File = "jona_service_7777.py" }
    )
    Orchestration = @(
        @{ Name = "Orchestrator"; Script = "python saas_services_orchestrator.py"; Port = 9999; Priority = 4; File = "saas_services_orchestrator.py" }
        @{ Name = "ASI Engine"; Script = "python asi_realtime_engine.py"; Port = 0; Priority = 5; File = "asi_realtime_engine.py" }
        @{ Name = "Cycle Engine"; Script = "python cycle_engine.py"; Port = 0; Priority = 5; File = "cycle_engine.py" }
        @{ Name = "Pulse Balancer"; Script = "python distributed_pulse_balancer.py"; Port = 0; Priority = 5; File = "distributed_pulse_balancer.py" }
    )
    Support = @(
        @{ Name = "AGIEM"; Script = "python agiem_core.py"; Port = 0; Priority = 6; File = "agiem_core.py" }
        @{ Name = "Blerina"; Script = "python blerina_reformatter.py"; Port = 0; Priority = 6; File = "blerina_reformatter.py" }
        @{ Name = "Slack Integration"; Script = "python slack_integration_service.py"; Port = 0; Priority = 6; File = "slack_integration_service.py" }
    )
}

# ===============================================================================
# HELPER FUNCTIONS
# ===============================================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    $logDir = Split-Path $Script:Config.LogFile
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $Script:Config.LogFile -Value $logMessage
}

function Show-Banner {
    Clear-Host
    Write-Host "`n===============================================================================" -ForegroundColor $Script:Colors.Title
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "              KLOUD CLOUD - START ALL SERVICES                              " -ForegroundColor $Script:Colors.Title
    Write-Host "                    Ultimate Service Orchestrator                              " -ForegroundColor $Script:Colors.Title
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "  Mode: $($Mode.ToUpper())" -ForegroundColor $Script:Colors.Title
    Write-Host "  Time: $($Script:Config.Timestamp)" -ForegroundColor $Script:Colors.Title
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "===============================================================================`n" -ForegroundColor $Script:Colors.Title
    
    Write-Log "Starting Kloud Cloud in $Mode mode"
}

function Show-Status {
    param(
        [string]$Message,
        [ValidateSet("INFO", "OK", "WAIT", "ERROR", "WARN", "SKIP")]
        [string]$Status = "INFO"
    )
    
    $icons = @{
        "INFO"  = "[i]"
        "OK"    = "[OK]"
        "WAIT"  = "[...]"
        "ERROR" = "[ERROR]"
        "WARN"  = "[WARN]"
        "SKIP"  = "[SKIP]"
    }
    
    $colors = @{
        "INFO"  = $Script:Colors.Info
        "OK"    = $Script:Colors.Success
        "WAIT"  = $Script:Colors.Warning
        "ERROR" = $Script:Colors.Error
        "WARN"  = $Script:Colors.Warning
        "SKIP"  = $Script:Colors.Accent
    }
    
    Write-Host "  $($icons[$Status]) " -NoNewline -ForegroundColor $colors[$Status]
    Write-Host $Message
    Write-Log $Message $Status
}

function Show-Help {
    Write-Host @"
===============================================================================
                        START ALL SERVICES - HELP
===============================================================================

MODES:
  dev            Development mode (Core services only, background jobs)
  prod           Production mode (All services in separate windows)
  full           Full stack (All services with health monitoring)
  docker         Docker Compose mode (Containerized deployment)
  saas           SaaS microservices only (ALBA, ALBI, JONA + Orchestrator)
  lite           Lite mode (API + Frontend only, minimal footprint)
  diagnostics    System diagnostics (Health scan, no service start)

FLAGS:
  -Clean         Terminate existing processes before starting
  -DryRun        Preview what would be executed without starting services
  -Monitor       Enable continuous health monitoring loop
  -Rebuild       Force rebuild Docker images (docker mode only)
  -NoHealthCheck Skip health check probes after startup
  -Help          Show this help message

EXAMPLES:
  .\start-all.ps1                           # Start in full mode
  .\start-all.ps1 -Mode dev -Clean          # Dev mode with cleanup
  .\start-all.ps1 -Mode docker -Rebuild     # Docker rebuild
  .\start-all.ps1 -Mode full -Monitor       # Full stack with monitoring
  .\start-all.ps1 -Mode diagnostics         # System health check only
  .\start-all.ps1 -Mode lite                # Minimal mode (API + Frontend)

STOPPING SERVICES:
  Get-Job | Stop-Job | Remove-Job           # Stop all background jobs
  docker-compose down                        # Stop Docker services
  Get-Process python,node | Stop-Process     # Kill all Python/Node processes

"@ -ForegroundColor $Script:Colors.Info
}

function Test-Prerequisites {
    Write-Host "`n--- PRE-FLIGHT CHECKS ---" -ForegroundColor $Script:Colors.Section
    
    $allPassed = $true
    
    # Check Node.js
    Show-Status "Checking Node.js..." "WAIT"
    try {
        $nodeVersion = node --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Show-Status "Node.js $nodeVersion installed" "OK"
        } else {
            throw
        }
    } catch {
        Show-Status "Node.js not found" "ERROR"
        $allPassed = $false
    }
    
    # Check Python
    Show-Status "Checking Python..." "WAIT"
    try {
        python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Show-Status "Python installed" "OK"
        } else {
            throw
        }
    } catch {
        Show-Status "Python not found" "ERROR"
        $allPassed = $false
    }
    
    # Check Docker (if needed)
    if ($Mode -eq "docker") {
        Show-Status "Checking Docker..." "WAIT"
        try {
            # PSScriptAnalyzer: Variables are used in string interpolation below
            [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseDeclaredVarsMoreThanAssignments', '')]
            $dockerVersion = docker --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Show-Status "Docker: $dockerVersion" "OK"
                
                [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSUseDeclaredVarsMoreThanAssignments', '')]
                $dockerInfo = docker info 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $firstLine = ($dockerInfo -split "`n")[0]
                    Show-Status "Docker daemon: $firstLine" "OK"
                } else {
                    Show-Status "Docker daemon not running" "ERROR"
                    $allPassed = $false
                }
            } else {
                throw
            }
        } catch {
            Show-Status "Docker not found" "ERROR"
            $allPassed = $false
        }
    }
    
    # Check .env file
    Show-Status "Checking configuration..." "WAIT"
    if (Test-Path ".env") {
        Show-Status ".env file found" "OK"
    } else {
        Show-Status ".env not found (will use defaults)" "WARN"
    }
    
    # Check npm dependencies
    if ($Mode -in @("dev", "prod", "full", "lite")) {
        Show-Status "Checking npm dependencies..." "WAIT"
        if (Test-Path "apps\web\node_modules") {
            Show-Status "npm dependencies installed" "OK"
        } else {
            if (-not $DryRun) {
                Show-Status "Installing npm dependencies..." "WAIT"
                Push-Location "apps\web"
                npm install --legacy-peer-deps 2>&1 | Out-Null
                Pop-Location
                Show-Status "npm dependencies installed" "OK"
            } else {
                Show-Status "npm dependencies missing (DRY RUN)" "WARN"
            }
        }
    }
    
    # Check Python packages
    Show-Status "Checking Python packages..." "WAIT"
    if (Test-Path "requirements.txt") {
        Show-Status "requirements.txt found" "OK"
    } else {
        Show-Status "requirements.txt not found" "WARN"
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
    
    if (-not $allPassed) {
        Show-Status "Pre-flight check FAILED! Please install missing dependencies." "ERROR"
        exit 1
    }
    
    return $allPassed
}

function Invoke-Cleanup {
    Write-Host "`n--- CLEANUP PROCESSES ---" -ForegroundColor $Script:Colors.Section
    
    Show-Status "Stopping existing services..." "WAIT"
    
    # Kill Python processes
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Show-Status "Terminated $($pythonProcesses.Count) Python process(es)" "OK"
    } else {
        Show-Status "No Python processes running" "SKIP"
    }
    
    # Kill Node processes
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Show-Status "Terminated $($nodeProcesses.Count) Node.js process(es)" "OK"
    } else {
        Show-Status "No Node.js processes running" "SKIP"
    }
    
    # Stop background jobs
    $jobs = Get-Job -ErrorAction SilentlyContinue
    if ($jobs) {
        $jobs | Stop-Job -ErrorAction SilentlyContinue
        $jobs | Remove-Job -ErrorAction SilentlyContinue
        Show-Status "Removed $($jobs.Count) background job(s)" "OK"
    } else {
        Show-Status "No background jobs running" "SKIP"
    }
    
    # Stop Docker containers (if in docker mode)
    if ($Mode -eq "docker") {
        Show-Status "Stopping Docker containers..." "WAIT"
        docker-compose down 2>&1 | Out-Null
        Show-Status "Docker containers stopped" "OK"
    }
    
    Start-Sleep -Seconds 2
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Test-PortAvailability {
    Write-Host "`n--- PORT AVAILABILITY CHECK ---" -ForegroundColor $Script:Colors.Section
    
    $occupiedPorts = @()
    
    foreach ($service in $Script:ServicePorts.GetEnumerator()) {
        $connection = Get-NetTCPConnection -LocalPort $service.Value -ErrorAction SilentlyContinue
        if ($connection) {
            Show-Status "$($service.Name) (Port $($service.Value)) - IN USE" "WARN"
            $occupiedPorts += $service.Value
        } else {
            Show-Status "$($service.Name) (Port $($service.Value)) - Available" "OK"
        }
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
    
    if ($occupiedPorts.Count -gt 0 -and -not $Clean) {
        Write-Host "`n  WARNING: Some ports are occupied. Use -Clean to free them.`n" -ForegroundColor $Script:Colors.Warning
    }
    
    return $occupiedPorts.Count -eq 0
}

function Start-ServiceWindow {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port,
        [string]$Color = "Cyan"
    )
    
    $scriptBlock = @"
Set-Location '$($Script:Root)'
`$host.UI.RawUI.WindowTitle = 'KLOUD - $Name $(if($Port -gt 0){"($Port)"})'
Write-Host '================================================================' -ForegroundColor $Color
Write-Host '  $($Name.PadRight(60))' -ForegroundColor $Color
if ($Port -gt 0) {
    Write-Host '  Port: $($Port.ToString().PadRight(56))' -ForegroundColor $Color
}
Write-Host '================================================================' -ForegroundColor $Color
Write-Host ''
$Command
"@
    
    Start-Process pwsh -ArgumentList @("-NoExit", "-Command", $scriptBlock)
}

function Start-ServiceJob {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port
    )
    
    $job = Start-Job -Name $Name -ScriptBlock {
        param($Root, $Cmd)
        Set-Location $Root
        Invoke-Expression $Cmd
    } -ArgumentList $Script:Root, $Command
    
    return $job
}

function Start-DevMode {
    Write-Host "`n--- MODE: DEVELOPMENT (Background Jobs) ---" -ForegroundColor $Script:Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start API as background job (port 8000)" "INFO"
        Show-Status "[DRY RUN] Would start Frontend as background job (port 3000)" "INFO"
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    Show-Status "Starting API Server..." "WAIT"
    $apiJob = Start-ServiceJob -Name "API" -Command "python -m uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000" -Port 8000
    Show-Status "API started (Job #$($apiJob.Id))" "OK"
    
    Start-Sleep -Seconds 3
    
    Show-Status "Starting Frontend..." "WAIT"
    $webJob = Start-ServiceJob -Name "Frontend" -Command "cd apps\web; `$env:NEXT_PUBLIC_API_BASE='http://localhost:8000'; npm run dev" -Port 3000
    Show-Status "Frontend started (Job #$($webJob.Id))" "OK"
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Start-ProdMode {
    Write-Host "`n--- MODE: PRODUCTION (Separate Windows) ---" -ForegroundColor $Script:Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start all services in separate windows" "INFO"
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    $servicesToStart = @()
    $servicesToStart += $Script:Services.Core
    $servicesToStart += $Script:Services.Microservices
    $servicesToStart += $Script:Services.Orchestration
    
    $count = 0
    foreach ($service in ($servicesToStart | Sort-Object Priority)) {
        if ($service.Script) {
            # Check if file exists for optional services
            if ($service.File -and -not (Test-Path $service.File)) {
                Show-Status "$($service.Name) - File not found, skipping" "SKIP"
                continue
            }
            
            $count++
            Show-Status "[$count] Starting $($service.Name)..." "WAIT"
            Start-ServiceWindow -Name $service.Name -Command $service.Script -Port $service.Port -Color "Green"
            Start-Sleep -Milliseconds 800
            Show-Status "$($service.Name) window opened" "OK"
        }
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Start-FullMode {
    Write-Host "`n--- MODE: FULL STACK (Complete Deployment) ---" -ForegroundColor $Script:Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start all services in separate windows" "INFO"
        Show-Status "[DRY RUN] Would perform health checks on all endpoints" "INFO"
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    $allServices = @()
    $allServices += $Script:Services.Core
    $allServices += $Script:Services.Microservices
    $allServices += $Script:Services.Orchestration
    $allServices += $Script:Services.Support
    
    $count = 0
    
    foreach ($service in ($allServices | Sort-Object Priority)) {
        if ($service.Script) {
            # Check if file exists for optional services
            if ($service.File -and -not (Test-Path $service.File)) {
                Show-Status "$($service.Name) - File not found, skipping" "SKIP"
                continue
            }
            
            $count++
            Show-Status "[$count] Launching $($service.Name)..." "WAIT"
            Start-ServiceWindow -Name $service.Name -Command $service.Script -Port $service.Port -Color "Cyan"
            Start-Sleep -Milliseconds 600
            Show-Status "$($service.Name) launched" "OK"
        }
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Start-DockerMode {
    Write-Host "`n--- MODE: DOCKER COMPOSE (Containerized Stack) ---" -ForegroundColor $Script:Colors.Section
    
    if (-not (Test-Path "docker-compose.yml")) {
        Show-Status "docker-compose.yml not found" "ERROR"
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would execute: docker-compose up -d" "INFO"
        if ($Rebuild) {
            Show-Status "[DRY RUN] Would rebuild images first" "INFO"
        }
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    if ($Rebuild) {
        Show-Status "Rebuilding Docker images..." "WAIT"
        docker-compose build 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Show-Status "Images rebuilt" "OK"
        } else {
            Show-Status "Image rebuild failed" "ERROR"
        }
    }
    
    Show-Status "Starting Docker Compose stack..." "WAIT"
    docker-compose up -d 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Show-Status "Docker services started" "OK"
    } else {
        Show-Status "Docker startup failed" "ERROR"
    }
    
    Start-Sleep -Seconds 5
    
    Show-Status "Checking container status..." "WAIT"
    docker-compose ps
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Start-SaaSMode {
    Write-Host "`n--- MODE: SAAS MICROSERVICES (ALBA/ALBI/JONA) ---" -ForegroundColor $Script:Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start SaaS microservices" "INFO"
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    $saasServices = $Script:Services.Microservices + $Script:Services.Orchestration
    
    $count = 0
    foreach ($service in ($saasServices | Sort-Object Priority)) {
        if ($service.Script) {
            # Check if file exists
            if ($service.File -and -not (Test-Path $service.File)) {
                Show-Status "$($service.Name) - File not found, skipping" "SKIP"
                continue
            }
            
            $count++
            Show-Status "[$count] Starting $($service.Name)..." "WAIT"
            Start-ServiceWindow -Name $service.Name -Command $service.Script -Port $service.Port -Color "Magenta"
            Start-Sleep -Milliseconds 700
            Show-Status "$($service.Name) started" "OK"
        }
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Start-LiteMode {
    Write-Host "`n--- MODE: LITE (Minimal Footprint) ---" -ForegroundColor $Script:Colors.Section
    
    if ($DryRun) {
        Show-Status "[DRY RUN] Would start API and Frontend only" "INFO"
        Write-Host "---`n" -ForegroundColor $Script:Colors.Section
        return
    }
    
    foreach ($service in $Script:Services.Core) {
        Show-Status "Starting $($service.Name)..." "WAIT"
        Start-ServiceWindow -Name $service.Name -Command $service.Script -Port $service.Port -Color "Yellow"
        Start-Sleep -Seconds 2
        Show-Status "$($service.Name) started" "OK"
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Invoke-HealthChecks {
    if ($NoHealthCheck) {
        Show-Status "Health checks skipped (--NoHealthCheck)" "SKIP"
        return
    }
    
    Write-Host "`n--- HEALTH CHECKS ---" -ForegroundColor $Script:Colors.Section
    
    $endpoints = @(
        @{ Name = "API Health"; URL = "http://localhost:8000/health"; Critical = $true }
        @{ Name = "API Docs"; URL = "http://localhost:8000/docs"; Critical = $false }
        @{ Name = "Frontend"; URL = "http://localhost:3000"; Critical = $true }
    )
    
    $maxRetries = 15
    $retryDelay = 2
    $healthyCount = 0
    
    for ($attempt = 1; $attempt -le $maxRetries; $attempt++) {
        Write-Host "  Attempt $attempt/$maxRetries..." -ForegroundColor $Script:Colors.Info
        $healthyCount = 0
        
        foreach ($endpoint in $endpoints) {
            try {
                $response = Invoke-WebRequest -Uri $endpoint.URL -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Show-Status "$($endpoint.Name) - HTTP $($response.StatusCode)" "OK"
                    $healthyCount++
                }
            } catch {
                if ($attempt -eq $maxRetries -and $endpoint.Critical) {
                    Show-Status "$($endpoint.Name) - Unreachable" "ERROR"
                } elseif ($attempt -eq $maxRetries) {
                    Show-Status "$($endpoint.Name) - Unreachable" "WARN"
                }
            }
        }
        
        if ($healthyCount -eq $endpoints.Count) {
            Write-Host "`n  All services are healthy!`n" -ForegroundColor $Script:Colors.Success
            break
        }
        
        if ($attempt -lt $maxRetries) {
            Start-Sleep -Seconds $retryDelay
        }
    }
    
    if ($healthyCount -lt $endpoints.Count) {
        Write-Host "`n  WARNING: Some services may not be fully ready yet.`n" -ForegroundColor $Script:Colors.Warning
    }
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Invoke-DiagnosticsMode {
    Write-Host "`n--- DIAGNOSTICS: SYSTEM HEALTH SCAN ---" -ForegroundColor $Script:Colors.Section
    
    Write-Host "`nPort Status:" -ForegroundColor $Script:Colors.Section
    foreach ($service in $Script:ServicePorts.GetEnumerator()) {
        $connection = Get-NetTCPConnection -LocalPort $service.Value -ErrorAction SilentlyContinue
        if ($connection) {
            Write-Host "  [ACTIVE] $($service.Name.PadRight(20)) (Port $($service.Value.ToString().PadRight(5)))" -ForegroundColor $Script:Colors.Success
        } else {
            Write-Host "  [------] $($service.Name.PadRight(20)) (Port $($service.Value.ToString().PadRight(5)))" -ForegroundColor $Script:Colors.Info
        }
    }
    
    Write-Host "`nHealth Endpoints:" -ForegroundColor $Script:Colors.Section
    $urls = @(
        "http://localhost:8000/health",
        "http://localhost:8000/docs",
        "http://localhost:3000"
    )
    
    foreach ($url in $urls) {
        try {
            $response = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            Write-Host "  [OK] $url - HTTP $($response.StatusCode)" -ForegroundColor $Script:Colors.Success
        } catch {
            Write-Host "  [FAIL] $url - Unreachable" -ForegroundColor $Script:Colors.Error
        }
    }
    
    Write-Host "`nProcess Status:" -ForegroundColor $Script:Colors.Section
    $pythonCount = (Get-Process -Name "python" -ErrorAction SilentlyContinue).Count
    $nodeCount = (Get-Process -Name "node" -ErrorAction SilentlyContinue).Count
    $jobCount = (Get-Job -ErrorAction SilentlyContinue).Count
    
    Write-Host "  Python processes: $pythonCount" -ForegroundColor $Script:Colors.Info
    Write-Host "  Node.js processes: $nodeCount" -ForegroundColor $Script:Colors.Info
    Write-Host "  Background jobs: $jobCount" -ForegroundColor $Script:Colors.Info
    
    Write-Host "`nProject Files:" -ForegroundColor $Script:Colors.Section
    $checks = @{
        ".env file" = Test-Path ".env"
        "docker-compose.yml" = Test-Path "docker-compose.yml"
        "apps/web/node_modules" = Test-Path "apps\web\node_modules"
        "requirements.txt" = Test-Path "requirements.txt"
    }
    
    foreach ($check in $checks.GetEnumerator()) {
        $status = if ($check.Value) { "[OK]" } else { "[--]" }
        $color = if ($check.Value) { $Script:Colors.Success } else { $Script:Colors.Error }
        Write-Host "  $status $($check.Name): $($check.Value)" -ForegroundColor $color
    }
    
    Write-Host "`nSystem Resources:" -ForegroundColor $Script:Colors.Section
    $os = Get-CimInstance Win32_OperatingSystem
    $cpu = Get-CimInstance Win32_Processor
    $totalRAM = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $freeRAM = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $usedRAM = $totalRAM - $freeRAM
    
    Write-Host "  CPU: $($cpu.Name)" -ForegroundColor $Script:Colors.Info
    Write-Host "  RAM: $usedRAM GB / $totalRAM GB used" -ForegroundColor $Script:Colors.Info
    
    Write-Host "---" -ForegroundColor $Script:Colors.Section
}

function Show-Dashboard {
    Write-Host "`n===============================================================================" -ForegroundColor $Script:Colors.Title
    Write-Host "                         SYSTEM READY                                          " -ForegroundColor $Script:Colors.Title
    Write-Host "===============================================================================" -ForegroundColor $Script:Colors.Title
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "  ENDPOINTS                                                                    " -ForegroundColor $Script:Colors.Title
    Write-Host "  - Frontend:      http://localhost:3000                                       " -ForegroundColor $Script:Colors.Success
    Write-Host "  - API:           http://localhost:8000                                       " -ForegroundColor $Script:Colors.Success
    Write-Host "  - API Docs:      http://localhost:8000/docs                                  " -ForegroundColor $Script:Colors.Success
    Write-Host "  - Health Check:  http://localhost:8000/health                                " -ForegroundColor $Script:Colors.Success
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "  MICROSERVICES                                                                " -ForegroundColor $Script:Colors.Title
    Write-Host "  - ALBA:          Port 5555                                                   " -ForegroundColor $Script:Colors.Info
    Write-Host "  - ALBI:          Port 6680                                                   " -ForegroundColor $Script:Colors.Info
    Write-Host "  - JONA:          Port 7777                                                   " -ForegroundColor $Script:Colors.Info
    Write-Host "  - Orchestrator:  Port 9999                                                   " -ForegroundColor $Script:Colors.Info
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "  MANAGEMENT                                                                   " -ForegroundColor $Script:Colors.Title
    Write-Host "  - View logs:         Get-Job | Receive-Job                                   " -ForegroundColor $Script:Colors.Warning
    Write-Host "  - Stop all jobs:     Get-Job | Stop-Job | Remove-Job                        " -ForegroundColor $Script:Colors.Warning
    Write-Host "  - Stop Docker:       docker-compose down                                     " -ForegroundColor $Script:Colors.Warning
    Write-Host "  - View processes:    Get-Process python,node                                 " -ForegroundColor $Script:Colors.Warning
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "  Log file: $($Script:Config.LogFile)" -ForegroundColor $Script:Colors.Title
    Write-Host "                                                                               " -ForegroundColor $Script:Colors.Title
    Write-Host "===============================================================================`n" -ForegroundColor $Script:Colors.Title
}

function Start-ContinuousMonitoring {
    Write-Host "`n--- CONTINUOUS MONITORING MODE ---" -ForegroundColor $Script:Colors.Section
    Show-Status "Starting continuous health monitoring (Ctrl+C to stop)..." "WAIT"
    Write-Host "---" -ForegroundColor $Script:Colors.Section
    
    $iteration = 0
    while ($true) {
        $iteration++
        Write-Host "`n=== Monitoring Cycle #$iteration ===" -ForegroundColor $Script:Colors.Accent
        Invoke-HealthChecks
        Start-Sleep -Seconds 30
    }
}

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

Show-Banner

if ($Help) {
    Show-Help
    exit 0
}

# Run pre-flight checks
if (-not (Test-Prerequisites)) {
    exit 1
}

# Clean up if requested
if ($Clean) {
    Invoke-Cleanup
}

# Check port availability
Test-PortAvailability | Out-Null

# Execute selected mode
switch ($Mode) {
    "dev"         { Start-DevMode }
    "prod"        { Start-ProdMode }
    "full"        { Start-FullMode }
    "docker"      { Start-DockerMode }
    "saas"        { Start-SaaSMode }
    "lite"        { Start-LiteMode }
    "diagnostics" { Invoke-DiagnosticsMode; exit 0 }
}

# Run health checks (unless in diagnostics mode)
if ($Mode -ne "diagnostics" -and -not $DryRun) {
    Start-Sleep -Seconds 5
    Invoke-HealthChecks
}

# Show dashboard
if (-not $DryRun) {
    Show-Dashboard
}

# Start continuous monitoring if requested
if ($Monitor -and -not $DryRun) {
    Start-ContinuousMonitoring
}

Write-Host "Kloud Cloud is ready! Happy coding!`n" -ForegroundColor $Script:Colors.Success
Write-Log "Startup completed successfully in $Mode mode"

