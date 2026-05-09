param(
    [ValidateSet("start-cycle-prod", "stop-cycle", "reload-cycle", "deploy-cycle", "auto-heal", "telemetry-unifim", "dashboard-prod-ready")]
    [string]$Action = "start-cycle-prod"
)

$ErrorActionPreference = "Stop"
$Root = "C:\kloud-cloud"
$ComposeFile = Join-Path $Root "docker-compose.prod.yml"

Set-Location $Root

function Write-Title {
    param([string]$text)
    Write-Host ""
    Write-Host "=== $text ===" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$text)
    Write-Host $text -ForegroundColor Green
}

function Write-Warning {
    param([string]$text)
    Write-Host $text -ForegroundColor Yellow
}

function Write-Error2 {
    param([string]$text)
    Write-Host $text -ForegroundColor Red
}

function Start-CycleProd {
    Write-Title "STARTING FULL PRODUCTION CYCLE (Docker Stack)"
    Write-Host "Composing: $ComposeFile" -ForegroundColor Gray
    
    if (-not (Test-Path $ComposeFile)) {
        Write-Error2 "ERROR: $ComposeFile not found!"
        exit 1
    }
    
    docker compose -f $ComposeFile up -d
    Write-Success "All services requested. Use 'docker compose ps' to inspect state."
    Write-Host ""
    Write-Host "Services running at:" -ForegroundColor Cyan
    Write-Host "  PostgreSQL:    localhost:5432" -ForegroundColor White
    Write-Host "  Redis:         localhost:6379" -ForegroundColor White
    Write-Host "  MinIO:         http://localhost:9000" -ForegroundColor White
    Write-Host "  Prometheus:    http://localhost:9090" -ForegroundColor White
    Write-Host "  Grafana:       http://localhost:3001" -ForegroundColor White
    Write-Host "  API:           http://localhost:8000" -ForegroundColor White
    Write-Host "  Frontend:      http://localhost:3000" -ForegroundColor White
    Write-Host "  Slack:         http://localhost:8888" -ForegroundColor White
}

function Stop-Cycle {
    Write-Title "STOPPING FULL CYCLE"
    docker compose -f $ComposeFile down
    Write-Warning "All containers stopped and network removed."
}

function Reload-Cycle {
    Write-Title "RELOAD CYCLE (restart core services)"
    Write-Host "Restarting: api web alba albi jona orchestrator slack" -ForegroundColor Gray
    docker compose -f $ComposeFile restart api web alba albi jona orchestrator slack
    Write-Success "Core services restarted."
}

function Deploy-Cycle {
    Write-Title "DEPLOY CYCLE (pull/build + up)"
    Write-Host "Building images..." -ForegroundColor Gray
    docker compose -f $ComposeFile build
    Write-Host "Starting containers..." -ForegroundColor Gray
    docker compose -f $ComposeFile up -d
    Write-Success "Deployment completed."
}

function Auto-Heal {
    Write-Title "AUTO-HEAL LOOP (press Ctrl+C to stop)"
    
    $services = @("postgres", "redis", "minio", "prometheus", "grafana",
                  "alba", "albi", "jona", "orchestrator",
                  "api", "web", "slack")
    
    $checkCount = 0
    
    while ($true) {
        $checkCount++
        Write-Host "[Check #$checkCount] $(Get-Date -Format 'HH:mm:ss') - Monitoring services..." -ForegroundColor Gray
        
        foreach ($s in $services) {
            try {
                $state = docker inspect -f '{{.State.Health.Status}}' "kloud-$s" 2>$null
                
                if (-not $state) {
                    continue
                }
                
                if ($state -ne "healthy") {
                    Write-Warning "  Service '$s' is '$state'. Restarting..."
                    docker compose -f $ComposeFile restart $s
                } else {
                    Write-Host "    $s - healthy" -ForegroundColor Green
                }
            }
            catch {
                # ignore errors for services without healthcheck
            }
        }
        
        Write-Host "  Waiting 30 seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds 30
    }
}

function Telemetry-Unifim {
    Write-Title "TELEMETRY UNIFIED CHECK (ALBA -> ALBI -> JONA -> Orchestrator -> API)"
    
    $urls = @(
        @{ name = "ALBA"; url = "http://localhost:5555/health" },
        @{ name = "ALBI"; url = "http://localhost:6680/health" },
        @{ name = "JONA"; url = "http://localhost:7777/health" },
        @{ name = "Orchestrator"; url = "http://localhost:9999/status" },
        @{ name = "API"; url = "http://localhost:8000/health" },
        @{ name = "Slack"; url = "http://localhost:8888/health" }
    )
    
    $allHealthy = $true
    Write-Host ""
    
    foreach ($service in $urls) {
        try {
            Write-Host "Checking $($service.name)..." -ForegroundColor Gray -NoNewline
            $resp = Invoke-WebRequest -Uri $service.url -UseBasicParsing -TimeoutSec 5
            
            if ($resp.StatusCode -eq 200) {
                Write-Success " OK [200]"
            } else {
                Write-Warning " WARNING [$($resp.StatusCode)]"
                $allHealthy = $false
            }
        }
        catch {
            Write-Error2 " FAIL [$($_.Exception.Message)]"
            $allHealthy = $false
        }
    }
    
    Write-Host ""
    if ($allHealthy) {
        Write-Success "All services healthy!"
    } else {
        Write-Warning "Some services may be unhealthy. Check logs."
    }
}

function Dashboard-ProdReady {
    Write-Title "OPENING PRODUCTION DASHBOARD"
    
    Write-Host "Opening Frontend (http://localhost:3000)..." -ForegroundColor Gray
    Start-Process "http://localhost:3000" -ErrorAction SilentlyContinue
    
    Start-Sleep -Milliseconds 500
    
    Write-Host "Opening Grafana (http://localhost:3001)..." -ForegroundColor Gray
    Start-Process "http://localhost:3001" -ErrorAction SilentlyContinue
    
    Start-Sleep -Milliseconds 500
    
    Write-Host "Opening Prometheus (http://localhost:9090)..." -ForegroundColor Gray
    Start-Process "http://localhost:9090" -ErrorAction SilentlyContinue
    
    Write-Success "Frontend, Grafana and Prometheus opened in browser."
}

switch ($Action) {
    "start-cycle-prod"    { Start-CycleProd }
    "stop-cycle"          { Stop-Cycle }
    "reload-cycle"        { Reload-Cycle }
    "deploy-cycle"        { Deploy-Cycle }
    "auto-heal"           { Auto-Heal }
    "telemetry-unifim"    { Telemetry-Unifim }
    "dashboard-prod-ready" { Dashboard-ProdReady }
}


