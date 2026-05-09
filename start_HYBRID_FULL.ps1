# =============================================================================
# KLOUD CLOUD - HYBRID FULL SYSTEM LAUNCHER
# =============================================================================
# Starts ALL microservices in external windows with proper sequencing
# 
# Services launched:
#   - Backend API (8000)
#   - Ocean Core (8030)
#   - Frontend (3000)
#   - Alba Collector (5555)
#   - Albi Processor (6680)
#   - Jona Coordinator (7777)
#   - Alda Server (7070)
#   - Liam Server (7575)
#   - Blerina Reformatter (7680)
#   - AGIEM Core (8080)
# =============================================================================

$ErrorActionPreference = "Continue"
$ROOT = $PSScriptRoot
$VENV = "$ROOT\.venv\Scripts\Activate.ps1"

Write-Host "`n" -NoNewline
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         KLOUD CLOUD - HYBRID FULL SYSTEM LAUNCHER             ║" -ForegroundColor Cyan
Write-Host "║    All Microservices + ASI Trinity + Ocean Core + Frontend       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process -Name python, node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Define all services
$services = @(
    # Core Backend
    @{ Name = "Backend API"; Port = 8000; Dir = "apps\api"; Cmd = "python main.py"; Color = "Green" },
    
    # Ocean Core with Hybrid Chat
    @{ Name = "Ocean Core"; Port = 8030; Dir = "ocean-core"; Cmd = "python ocean_api.py"; Color = "Cyan" },
    
    # ASI Trinity
    @{ Name = "Alba Collector"; Port = 5555; Dir = "."; Cmd = "python alba_service_5555.py"; Color = "Magenta" },
    @{ Name = "Albi Processor"; Port = 6680; Dir = "."; Cmd = "python albi_service_6680.py"; Color = "Blue" },
    @{ Name = "Jona Coordinator"; Port = 7777; Dir = "."; Cmd = "python jona_service_7777.py"; Color = "Yellow" },
    
    # Extended Services
    @{ Name = "Alda Server"; Port = 7070; Dir = "."; Cmd = "python alda_server.py"; Color = "DarkCyan" },
    @{ Name = "Liam Server"; Port = 7575; Dir = "."; Cmd = "python liam_server.py"; Color = "DarkMagenta" },
    @{ Name = "Blerina Reformatter"; Port = 7680; Dir = "."; Cmd = "python blerina_reformatter.py"; Color = "DarkYellow" },
    @{ Name = "AGIEM Core"; Port = 8080; Dir = "."; Cmd = "python agiem_core.py"; Color = "DarkGreen" },
    
    # Frontend (last)
    @{ Name = "Frontend"; Port = 3000; Dir = "apps\web"; Cmd = "npm run dev"; Color = "White" }
)

Write-Host ""
Write-Host "🚀 Starting $($services.Count) services..." -ForegroundColor Green
Write-Host ""

foreach ($svc in $services) {
    $fullDir = Join-Path $ROOT $svc.Dir
    $title = "$($svc.Name) [$($svc.Port)]"
    
    # Check if directory exists
    if (-not (Test-Path $fullDir)) {
        Write-Host "⚠️  Directory not found: $fullDir - Skipping $($svc.Name)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "  ▸ Starting $($svc.Name) on port $($svc.Port)..." -ForegroundColor $svc.Color
    
    # Build the command for external window
    if ($svc.Cmd -like "python*") {
        # Python service - activate venv first
        $cmd = "cd '$fullDir'; & '$VENV'; $($svc.Cmd)"
    } else {
        # Node/npm service
        $cmd = "cd '$fullDir'; $($svc.Cmd)"
    }
    
    # Start in external window
    Start-Process -FilePath "pwsh" -ArgumentList "-NoExit", "-Command", $cmd -WindowStyle Normal
    
    # Wait a bit between services
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ ALL SERVICES LAUNCHED                       ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║                                                                  ║" -ForegroundColor Green
Write-Host "║  🌐 Frontend:           http://localhost:3000                    ║" -ForegroundColor White
Write-Host "║  🔧 Backend API:        http://localhost:8000                    ║" -ForegroundColor White
Write-Host "║  🌊 Ocean Core:         http://localhost:8030                    ║" -ForegroundColor Cyan
Write-Host "║  💬 Hybrid Chat:        http://localhost:8030/api/chat/hybrid    ║" -ForegroundColor Cyan
Write-Host "║                                                                  ║" -ForegroundColor Green
Write-Host "║  ASI TRINITY:                                                    ║" -ForegroundColor Magenta
Write-Host "║  📡 Alba Collector:     http://localhost:5555                    ║" -ForegroundColor Magenta
Write-Host "║  🧠 Albi Processor:     http://localhost:6680                    ║" -ForegroundColor Blue
Write-Host "║  🎵 Jona Coordinator:   http://localhost:7777                    ║" -ForegroundColor Yellow
Write-Host "║                                                                  ║" -ForegroundColor Green
Write-Host "║  EXTENDED SERVICES:                                              ║" -ForegroundColor DarkCyan
Write-Host "║  📊 Alda Server:        http://localhost:7070                    ║" -ForegroundColor DarkCyan
Write-Host "║  🦁 Liam Server:        http://localhost:7575                    ║" -ForegroundColor DarkMagenta
Write-Host "║  🌸 Blerina:            http://localhost:7680                    ║" -ForegroundColor DarkYellow
Write-Host "║  🤖 AGIEM Core:         http://localhost:8080                    ║" -ForegroundColor DarkGreen
Write-Host "║                                                                  ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tip: All services are running in separate windows." -ForegroundColor Gray
Write-Host "💡 Close individual windows to stop specific services." -ForegroundColor Gray
Write-Host ""

