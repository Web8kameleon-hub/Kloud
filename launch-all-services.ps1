# KLOUD CLOUD - MASTER LAUNCHER v2.0
# Starton GJITH? servicet n? PWsh terminal t? ve?anta

param(
    [switch]$Clean = $false,
    [switch]$DryRun = $false
)

$Root = 'c:\Users\Admin\Desktop\neurosonix-cloud'
$Services = @()

Write-Host "`n??????????????????????????????????????????????????????????" -ForegroundColor Magenta
Write-Host "?  KLOUD CLOUD - MASTER LAUNCHER v2.0                  ?" -ForegroundColor Magenta
Write-Host "?  Starting ALL services in separate terminals           ?" -ForegroundColor Magenta
Write-Host "??????????????????????????????????????????????????????????`n" -ForegroundColor Magenta

# INFRASTRUCTURE
$Services += @(
    @{ Name='Docker Compose'; Port='multi'; Cmd='docker-compose up -d'; Wait=15 }
)

# CORE
$Services += @(
    @{ Name='Backend API (8000)'; Port=8000; Cmd='python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload'; Wait=5 }
    @{ Name='Frontend (3000)'; Port=3000; Cmd='cd apps\web; npm run dev'; Wait=5 }
)

# TRINITY
$Services += @(
    @{ Name='Alba (5555)'; Port=5555; Cmd='python alba_service_5555.py'; Wait=3 }
    @{ Name='Albi (6680)'; Port=6680; Cmd='python albi_service_6680.py'; Wait=3 }
    @{ Name='Jona (7777)'; Port=7777; Cmd='python jona_service_7777.py'; Wait=3 }
)

# ORCHESTRATION
$Services += @(
    @{ Name='Orchestrator (9999)'; Port=9999; Cmd='python saas_services_orchestrator.py'; Wait=3 }
    @{ Name='ASI Realtime'; Port=0; Cmd='python asi_realtime_engine.py'; Wait=2 }
    @{ Name='Blerina'; Port=0; Cmd='python blerina_reformatter.py'; Wait=2 }
    @{ Name='Pulse Balancer'; Port=0; Cmd='python distributed_pulse_balancer.py'; Wait=2 }
)

# SUPPORT
$Services += @(
    @{ Name='Alba Feeder'; Port=0; Cmd='python alba_feeder_service.py'; Wait=2 }
    @{ Name='Slack Integration'; Port=0; Cmd='python slack_integration_service.py'; Wait=2 }
    @{ Name='AGIEM Core'; Port=0; Cmd='python agiem_core.py'; Wait=2 }
)

# CLEANUP
if ($Clean) {
    Write-Host "`n?? Cleaning..." -ForegroundColor Red
    Get-Process | Where-Object { $_.ProcessName -match 'python|node|npm' } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "`n?? LAUNCHING ALL SERVICES...`n" -ForegroundColor Cyan

$Count = 0
foreach ($Service in $Services) {
    $Count++
    $Name = $Service.Name
    $Cmd = $Service.Cmd
    $Wait = $Service.Wait
    
    Write-Host "[$Count/$($Services.Count)] $Name..." -ForegroundColor Green
    
    if ($DryRun) {
        Write-Host "  [DRY-RUN] $Cmd`n"
        continue
    }
    
    Start-Process pwsh -ArgumentList @('-NoExit', '-NoProfile', '-Command', "cd '$Root'; $Cmd 2>&1")
    
    Write-Host "  ? Launched`n" -ForegroundColor Green
    Start-Sleep -Seconds $Wait
}

Write-Host "`n? ALL SERVICES LAUNCHED`n" -ForegroundColor Green
Write-Host "PORTS: API(8000) FE(3000) Alba(5555) Albi(6680) Jona(7777) Orch(9999)" -ForegroundColor Cyan
Write-Host "`nMonitor terminals - paste errors here for fixing`n" -ForegroundColor Yellow

