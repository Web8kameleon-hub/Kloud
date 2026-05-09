#!/usr/bin/env pwsh
# ═══════════════════════════════════════════════════════════════════════════════
# KLOUD CLOUD - QUICK START (Ocean Core + Backend + Frontend)
# ═══════════════════════════════════════════════════════════════════════════════

$ErrorActionPreference = "Continue"
$Root = "c:\Users\Admin\Desktop\Kloud-cloud"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "              KLOUD CLOUD - QUICK START                     " -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. Ocean Core (Port 8030)
Write-Host "[1/3] Starting Ocean Core (Port 8030)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd $Root\ocean-core; python ocean_api.py"
Start-Sleep -Seconds 3

# 2. Backend API (Port 8000)
Write-Host "[2/3] Starting Backend API (Port 8000)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd $Root\apps\api; npm run dev"
Start-Sleep -Seconds 3

# 3. Frontend (Port 3000)
Write-Host "[3/3] Starting Frontend (Port 3000)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd $Root\apps\web; npm run dev"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "              [OK] KLOUD CLOUD STARTED                      " -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  Services:" -ForegroundColor Cyan
Write-Host "    Ocean Core  -> http://127.0.0.1:8030" -ForegroundColor White
Write-Host "    Backend API -> http://127.0.0.1:8000" -ForegroundColor White
Write-Host "    Frontend    -> http://127.0.0.1:3000" -ForegroundColor White
Write-Host ""
Write-Host "  Quick Tests:" -ForegroundColor Cyan
Write-Host "    curl http://127.0.0.1:8030/api/info" -ForegroundColor DarkGray
Write-Host "    curl http://127.0.0.1:8000/health" -ForegroundColor DarkGray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green

