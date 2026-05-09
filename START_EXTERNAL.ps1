#!/usr/bin/env pwsh
# 🚀 KLOUD CLOUD - EXTERNAL WINDOWS LAUNCHER
# Hap çdo shërbim në dritare të jashtme PowerShell
# Kështu VS Code terminali mbetet i lirë për teste

param(
    [switch]$Clean,
    [switch]$DryRun
)

$Root = 'C:\Users\Admin\Desktop\Kloud-cloud'
Set-Location $Root

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  🚀 KLOUD CLOUD - EXTERNAL WINDOWS LAUNCHER          ║" -ForegroundColor Magenta
Write-Host "║     Çdo shërbim hapet në dritare të veçantë             ║" -ForegroundColor Magenta
Write-Host "║     VS Code terminali mbetet i lirë për teste!          ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Magenta

# Services to launch
$Services = @(
    @{
        Name = '⚡ Backend API (8000)'
        Cmd = 'python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload'
        Dir = $Root
        Wait = 3
    }
    @{
        Name = '🌊 Ocean Core (8030)'
        Cmd = 'python ocean_api.py'
        Dir = "$Root\ocean-core"
        Wait = 4
    }
    @{
        Name = '🎨 Frontend (3001)'
        Cmd = 'npm run dev'
        Dir = "$Root\apps\web"
        Wait = 2
    }
)

# Cleanup if requested
if ($Clean) {
    Write-Host "🧹 Mbyll proceset e vjetra..." -ForegroundColor Yellow
    Get-Process -Name python, node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Liro portet
    @(8000, 8030, 3001) | ForEach-Object {
        Get-NetTCPConnection -LocalPort $_ -ErrorAction SilentlyContinue | ForEach-Object {
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
    Write-Host "✅ Proceset u mbyllën`n" -ForegroundColor Green
}

# Launch each service in external window
$count = 0
foreach ($Service in $Services) {
    $count++
    $Name = $Service.Name
    $Cmd = $Service.Cmd
    $Dir = $Service.Dir
    $Wait = $Service.Wait
    
    Write-Host "[$count/$($Services.Count)] $Name..." -ForegroundColor Green
    
    if ($DryRun) {
        Write-Host "  [DRY-RUN] cd '$Dir'; $Cmd`n" -ForegroundColor Yellow
        continue
    }
    
    # Launch in new external PowerShell window
    Start-Process pwsh -ArgumentList @(
        '-NoExit',
        '-NoProfile', 
        '-Command',
        "Set-Location '$Dir'; Write-Host '════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host '  $Name' -ForegroundColor Cyan; Write-Host '════════════════════════════════════════════════════════════' -ForegroundColor Cyan; Write-Host ''; $Cmd"
    )
    
    Write-Host "  ✅ Hapur në dritare të re`n" -ForegroundColor Green
    Start-Sleep -Seconds $Wait
}

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ $count shërbime u hapën në dritare të jashtme!       ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  ⚡ Backend:    http://localhost:8000/docs              ║" -ForegroundColor Cyan
Write-Host "║  🌊 Ocean:      http://localhost:8030/docs              ║" -ForegroundColor Cyan
Write-Host "║  🎨 Frontend:   http://localhost:3001                   ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════════════════╣" -ForegroundColor Yellow
Write-Host "║  💡 Mbyll dritaret për të ndalur shërbimet             ║" -ForegroundColor Yellow
Write-Host "║  🧪 VS Code terminali tani mund të testohet!            ║" -ForegroundColor Yellow
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Test Binary Algebra:" -ForegroundColor Cyan
Write-Host "  http://localhost:8030/api/curiosity/algebra/op?a=255&b=170&op=xor" -ForegroundColor White

