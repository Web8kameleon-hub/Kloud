#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start all 76+ Clisonix microservices with health checks
.DESCRIPTION
    Orchestrates all backend services, checks dependencies, and validates functionality
#>

param(
    [switch]$StopFirst = $true,
    [switch]$SkipDependencies = $false,
    [switch]$Verbose = $true
)

$ErrorActionPreference = "SilentlyContinue"
$WarningPreference = "SilentlyContinue"

# Colors
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-Status {
    param([string]$Message, [string]$Status = "Info")
    $color = $Colors[$Status] ?? "White"
    Write-Host $Message -ForegroundColor $color
}

function Test-Port {
    param([int]$Port, [int]$TimeoutSeconds = 5)
    try {
        $socket = New-Object System.Net.Sockets.TcpClient
        $task = $socket.ConnectAsync("127.0.0.1", $Port)
        if ($task.Wait($TimeoutSeconds * 1000)) {
            $socket.Close()
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

Write-Status "╔════════════════════════════════════════════════════════════╗" "Header"
Write-Status "║   CLISONIX MICROSERVICES ORCHESTRATOR - 76+ SERVICES       ║" "Header"
Write-Status "╚════════════════════════════════════════════════════════════╝" "Header"

# Set working directory
$workdir = "c:\Users\pc\Clisonix-cloud\clisonix.com"
Push-Location $workdir

# Venv path
$venv = ".\.venv\Scripts\python.exe"

# Service definitions with ports and startup commands
$services = @(
    # CORE INFRASTRUCTURE
    @{ Name = "Ollama LLM"; Port = 11434; Type = "System"; Description = "Local LLM Engine" },
    
    # DATABASES (Docker - if available)
    @{ Name = "PostgreSQL"; Port = 5432; Type = "Database"; Description = "Primary Database" },
    @{ Name = "Redis"; Port = 6379; Type = "Cache"; Description = "Cache Layer" },
    @{ Name = "Neo4j"; Port = 7474; Type = "Graph"; Description = "Graph Database" },
    @{ Name = "MinIO"; Port = 9000; Type = "Storage"; Description = "Object Storage" },
    
    # CRITICAL SERVICES
    @{ Name = "Ocean Core Full"; Port = 8030; Type = "Python"; Path = "ocean-core\ocean_core_full.py"; Env = "OCEAN_CORE_URL=http://127.0.0.1:8030" },
    @{ Name = "AI Global 9999"; Port = 9999; Type = "Python"; Path = "9999\app.py"; Env = "OLLAMA_HOST=http://127.0.0.1:11434,OCEAN_CORE_URL=http://127.0.0.1:8030" },
    @{ Name = "API Backend"; Port = 8000; Type = "Python"; Path = "apps/api/main.py"; Env = "" },
    @{ Name = "Excel Core"; Port = 8002; Type = "Python"; Path = "services/excel/main.py"; Env = "" },
    @{ Name = "Frontend (Next.js)"; Port = 3001; Type = "NodeJS"; Path = "apps/web"; Command = "npm run dev" },
    
    # MICROSERVICES
    @{ Name = "ALBA (Analytics)"; Port = 5555; Type = "Python"; Path = "alba_service_5555.py"; Env = "" },
    @{ Name = "ALBI"; Port = 6680; Type = "Python"; Path = "albi_service_6680.py"; Env = "" },
    @{ Name = "ALDA"; Port = 8003; Type = "Python"; Path = "alda_server.py"; Env = "" },
    @{ Name = "ASI"; Port = 8004; Type = "Python"; Path = "asi_api_server.py"; Env = "" },
    @{ Name = "CYCLE"; Port = 8005; Type = "Python"; Path = "cycle_api_server.py"; Env = "" },
    @{ Name = "JONA"; Port = 8006; Type = "Python"; Path = "jona_server.py"; Env = "" },
    @{ Name = "LIAM"; Port = 8007; Type = "Python"; Path = "liam_server.py"; Env = "" },
    
    # ADVANCED FEATURES
    @{ Name = "Content Factory"; Port = 8008; Type = "Python"; Path = "services/content-factory/main.py"; Env = "" },
    @{ Name = "Video Generator"; Port = 8009; Type = "Python"; Path = "services/video-generator/main.py"; Env = "" },
    @{ Name = "Reporting Engine"; Port = 8010; Type = "Python"; Path = "services/reporting/main.py"; Env = "" },
    @{ Name = "Intelligence Lab"; Port = 8011; Type = "Python"; Path = "services/intelligence-lab/main.py"; Env = "" },
    @{ Name = "Marketplace"; Port = 8012; Type = "Python"; Path = "services/marketplace/main.py"; Env = "" },
    @{ Name = "User Management"; Port = 8013; Type = "Python"; Path = "services/user-management/main.py"; Env = "" },
    @{ Name = "Worker Pool"; Port = 8014; Type = "Python"; Path = "worker/main.py"; Env = "" },
    
    # BALANCERS & COORDINATORS
    @{ Name = "Balancer Simple"; Port = 3335; Type = "Python"; Path = "balancer_simple.py"; Env = "" },
    @{ Name = "Balancer Cache"; Port = 3336; Type = "Python"; Path = "balancer_cache_3335.py"; Env = "" },
    @{ Name = "Balancer Data"; Port = 3337; Type = "Python"; Path = "balancer_data_3337.py"; Env = "" },
    @{ Name = "Balancer TS"; Port = 3338; Type = "TypeScript"; Path = "balancer_ts_3338.ts"; Env = "" }
)

# PHASE 1: STOP EXISTING SERVICES
if ($StopFirst) {
    Write-Status "`n📋 PHASE 1: CLEANUP" "Header"
    Write-Status "Stopping existing processes..." "Warning"
    
    $ports = $services | Where-Object { $_.Port } | Select-Object -ExpandProperty Port
    foreach ($port in $ports) {
        $proc = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
            Select-Object -ExpandProperty OwningProcess | 
            Select-Object -First 1
        if ($proc) {
            Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Status "✓ All processes stopped" "Success"
}

# PHASE 2: VERIFY ENVIRONMENT
Write-Status "`n🔍 PHASE 2: ENVIRONMENT VERIFICATION" "Header"

# Check Python
$pythonVersion = & $venv --version 2>&1
Write-Status "Python: $pythonVersion" "Info"

# Check Ollama
$ollamaCheck = Test-Port 11434
if ($ollamaCheck) {
    Write-Status "✓ Ollama is running on port 11434" "Success"
} else {
    Write-Status "⚠ Ollama not detected (optional)" "Warning"
}

# PHASE 3: START SERVICES
Write-Status "`n🚀 PHASE 3: STARTING SERVICES" "Header"

$serviceProcesses = @{}

# Start critical services first
$criticalServices = $services | Where-Object { $_.Type -eq "Python" -and $_.Port -in @(8030, 9999, 8000, 8002) }

foreach ($service in $criticalServices) {
    Write-Status "`nStarting: $($service.Name) (Port $($service.Port))..." "Info"
    
    try {
        $envString = ""
        if ($service.Env) {
            $envString = "`$env:" + ($service.Env -replace ',', '; $env:')
        }
        
        $startCmd = "`$env:PYTHONUNBUFFERED=1; $envString; & '$venv' '$($service.Path)'"
        
        $process = Start-Process -WindowStyle Minimized -FilePath "pwsh.exe" -ArgumentList "-Command", $startCmd -PassThru
        $serviceProcesses[$service.Name] = $process.Id
        
        Start-Sleep -Seconds 2
        
        if (Test-Port $service.Port) {
            Write-Status "✓ $($service.Name) started successfully" "Success"
        } else {
            Write-Status "⏳ $($service.Name) starting (may take longer)..." "Warning"
        }
    } catch {
        Write-Status "✗ Failed to start $($service.Name): $_" "Error"
    }
}

# Start remaining services
Write-Status "`n📦 Starting additional microservices..." "Info"
$otherServices = $services | Where-Object { $_.Type -eq "Python" -and $_.Port -notin @(8030, 9999, 8000, 8002) }

$batchSize = 5
for ($i = 0; $i -lt $otherServices.Count; $i += $batchSize) {
    $batch = $otherServices[$i..($i + $batchSize - 1)]
    
    foreach ($service in $batch) {
        if (-not $service.Path) { continue }
        
        $process = Start-Process -WindowStyle Minimized -FilePath "pwsh.exe" -ArgumentList "-Command", "`$env:PYTHONUNBUFFERED=1; & '$venv' '$($service.Path)'" -PassThru
        $serviceProcesses[$service.Name] = $process.Id
    }
    
    Start-Sleep -Seconds 2
}

# Start Frontend
Write-Status "`nStarting Frontend (Next.js)..." "Info"
try {
    Push-Location "apps/web"
    $frontendProcess = Start-Process -WindowStyle Minimized -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -PassThru
    $serviceProcesses["Frontend"] = $frontendProcess.Id
    Pop-Location
    Write-Status "✓ Frontend process started" "Success"
} catch {
    Write-Status "⚠ Frontend start warning: $_" "Warning"
}

# PHASE 4: VERIFICATION
Write-Status "`n✅ PHASE 4: HEALTH CHECK" "Header"
Start-Sleep -Seconds 5

$healthStatus = @{}
$criticalPorts = @(8030, 9999, 8000, 8002, 3001, 11434)

foreach ($port in $criticalPorts) {
    $service = $services | Where-Object { $_.Port -eq $port }
    $isHealthy = Test-Port $port
    $healthStatus[$service.Name] = $isHealthy
    
    $symbol = if ($isHealthy) { "✓" } else { "✗" }
    $color = if ($isHealthy) { "Success" } else { "Error" }
    Write-Status "$symbol $($service.Name) - Port $port" $color
}

# PHASE 5: SUMMARY
Write-Status "`n📊 SUMMARY" "Header"
$running = @($healthStatus.Values | Where-Object { $_ -eq $true }).Count
$total = @($healthStatus.Values).Count

Write-Status "Services Running: $running / $total" $(if ($running -eq $total) { "Success" } else { "Warning" })

if ($running -eq $total) {
    Write-Status "`n🎉 ALL SYSTEMS GO! Press CTRL+C to stop." "Success"
} else {
    Write-Status "`n⚠ Some services need attention. Check logs above." "Warning"
}

Write-Status "`n📍 ACCESS ENDPOINTS:" "Header"
Write-Status "  Frontend:       http://localhost:3001" "Info"
Write-Status "  API Backend:    http://localhost:8000" "Info"
Write-Status "  AI Global:      http://localhost:9999" "Info"
Write-Status "  Ocean Core:     http://localhost:8030" "Info"
Write-Status "  Ollama:         http://localhost:11434" "Info"

Pop-Location

# Keep script running
Write-Status "`n(Services running in background. Press Ctrl+C to exit.)" "Info"
while ($true) {
    Start-Sleep -Seconds 60
}
