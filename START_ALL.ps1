# 🚀 ULTRA DYNAMIC STARTUP SCRIPT - NDIZ NJEKOHESISHT
# Fillon: Backend 8000 + Frontend 3001 + Ocean-Core 8030

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "KLOUD ULTRA STARTUP - NJEKOHESISHT" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Kill previous processes
Write-Host "Killing previous processes..." -ForegroundColor Yellow
Get-Process -Name python,node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# START BACKEND 8000
Write-Host "Starting Backend API (port 8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    cd "c:\Users\Admin\Desktop\Kloud-cloud"
    $env:PYTHONPATH = "."
    python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload
} -Name "Backend-8000"

Start-Sleep -Seconds 5

# START OCEAN-CORE 8030 (BEFORE FRONTEND - Ocean needs backend first)
Write-Host "Starting Ocean-Core (port 8030)..." -ForegroundColor Green
$oceanJob = Start-Job -ScriptBlock {
    cd "c:\Users\Admin\Desktop\Kloud-cloud\ocean-core"
    $env:PYTHONPATH = ".."
    python ocean_api.py
} -Name "Ocean-Core-8030"

Start-Sleep -Seconds 4

# START FRONTEND 3001
Write-Host "Starting Frontend Next.js (port 3001)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    cd "c:\Users\Admin\Desktop\Kloud-cloud\apps\web"
    npm run dev
} -Name "Frontend-3001"

Write-Host ""
Write-Host "ALL SERVICES STARTING..." -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Ocean-Core:  http://localhost:8030" -ForegroundColor Cyan
Write-Host "Frontend:    http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Checking logs in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "BACKEND LOGS:" -ForegroundColor Green
Receive-Job -Name "Backend-8000" | Select-Object -Last 5

Write-Host ""
Write-Host "OCEAN-CORE LOGS:" -ForegroundColor Green
Receive-Job -Name "Ocean-Core-8030" | Select-Object -Last 5

Write-Host ""
Write-Host "FRONTEND LOGS:" -ForegroundColor Green
Receive-Job -Name "Frontend-3001" | Select-Object -Last 3

Write-Host ""
Write-Host "Current Status:" -ForegroundColor Cyan
Get-Job | Format-Table -Property Name, State

