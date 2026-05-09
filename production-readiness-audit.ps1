#!/usr/bin/env pwsh
# Kloud Cloud - Production Readiness Audit
# Comprehensive platform check before deployment

param(
    [switch]$Detailed = $false
)

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     KLOUD CLOUD - PRODUCTION READINESS AUDIT               ║" -ForegroundColor Cyan
Write-Host "║     Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm')                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$score = 0
$total = 15

# 1. Python Environment
Write-Host "[1/15] Python Environment..." -ForegroundColor Yellow
$pyVer = python --version 2>&1
if ($pyVer -match '3\.13') {
    Write-Host "  ✅ Python $pyVer" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ Python 3.13+ required, found: $pyVer" -ForegroundColor Red
}

# 2. Node.js Environment
Write-Host "`n[2/15] Node.js Environment..." -ForegroundColor Yellow
$nodeVer = node --version 2>&1
if ($nodeVer -match 'v2[0-9]') {
    Write-Host "  ✅ Node.js $nodeVer" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ Node.js 20+ required, found: $nodeVer" -ForegroundColor Red
}

# 3. Python Dependencies
Write-Host "`n[3/15] Python Dependencies..." -ForegroundColor Yellow
if (Test-Path "pyproject.toml") {
    Write-Host "  ✅ pyproject.toml exists" -ForegroundColor Green
    $pipList = pip list 2>&1 | Measure-Object -Line
    Write-Host "  📦 $($pipList.Lines) packages installed" -ForegroundColor Cyan
    $score++
} else {
    Write-Host "  ❌ Missing pyproject.toml" -ForegroundColor Red
}

# 4. Node.js Dependencies
Write-Host "`n[4/15] Node.js Dependencies..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Write-Host "  ✅ node_modules installed" -ForegroundColor Green
    $nmCount = (Get-ChildItem "node_modules" -Directory).Count
    Write-Host "  📦 $nmCount packages" -ForegroundColor Cyan
    $score++
} else {
    Write-Host "  ⚠️ node_modules missing - run: npm install" -ForegroundColor Yellow
}

# 5. Core API Service
Write-Host "`n[5/15] Core API Service..." -ForegroundColor Yellow
if (Test-Path "apps/api/main.py") {
    $lines = (Get-Content "apps/api/main.py").Count
    Write-Host "  ✅ Main API exists ($lines lines)" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ Missing apps/api/main.py" -ForegroundColor Red
}

# 6. Agent Services
Write-Host "`n[6/15] AI Agent Services..." -ForegroundColor Yellow
$agents = @("alba_service_5555.py", "albi_service_6680.py", "jona_service_7777.py", "master.py")
$agentCount = 0
foreach ($agent in $agents) {
    if (Test-Path $agent) {
        $agentCount++
        Write-Host "  ✅ $agent" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing $agent" -ForegroundColor Red
    }
}
if ($agentCount -eq 4) { $score++ }

# 7. Frontend (Next.js)
Write-Host "`n[7/15] Frontend Application..." -ForegroundColor Yellow
if (Test-Path "apps/web") {
    Write-Host "  ✅ Next.js app in apps/web/" -ForegroundColor Green
    if (Test-Path "apps/web/package.json") {
        Write-Host "  ✅ Frontend package.json exists" -ForegroundColor Green
        $score++
    }
} else {
    Write-Host "  ❌ Missing apps/web/" -ForegroundColor Red
}

# 8. Database Configuration
Write-Host "`n[8/15] Database Configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "DATABASE_URL") {
        Write-Host "  ✅ DATABASE_URL configured" -ForegroundColor Green
        $score++
    } else {
        Write-Host "  ⚠️ DATABASE_URL not found in .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️ .env file missing" -ForegroundColor Yellow
}

# 9. Docker Configuration
Write-Host "`n[9/15] Docker Configuration..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Write-Host "  ✅ docker-compose.yml exists" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ❌ Missing docker-compose.yml" -ForegroundColor Red
}

# 10. OpenAPI Contracts
Write-Host "`n[10/15] API Documentation..." -ForegroundColor Yellow
if (Test-Path "openapi") {
    $contracts = Get-ChildItem "openapi/*.yaml" -ErrorAction SilentlyContinue
    if ($contracts.Count -gt 0) {
        Write-Host "  ✅ $($contracts.Count) OpenAPI contracts" -ForegroundColor Green
        $score++
    }
} else {
    Write-Host "  ⚠️ OpenAPI contracts missing" -ForegroundColor Yellow
}

# 11. CI/CD Pipeline
Write-Host "`n[11/15] CI/CD Configuration..." -ForegroundColor Yellow
if (Test-Path ".github/workflows") {
    $workflows = Get-ChildItem ".github/workflows/*.yml" -ErrorAction SilentlyContinue
    Write-Host "  ✅ GitHub Actions configured ($($workflows.Count) workflows)" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️ GitHub Actions not configured" -ForegroundColor Yellow
}

# 12. Observability Documentation
Write-Host "`n[12/15] Observability Documentation..." -ForegroundColor Yellow
if (Test-Path "docs/observability") {
    $docs = Get-ChildItem "docs/observability/*.md" -ErrorAction SilentlyContinue
    Write-Host "  ✅ Observability docs ($($docs.Count) files)" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️ Observability docs missing" -ForegroundColor Yellow
}

# 13. Security Configuration
Write-Host "`n[13/15] Security Configuration..." -ForegroundColor Yellow
$securityFiles = @("API_CONFIG.py", "api_key_middleware.py")
$secCount = 0
foreach ($secFile in $securityFiles) {
    if (Test-Path $secFile) { $secCount++ }
}
if ($secCount -eq 2) {
    Write-Host "  ✅ API security configured" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️ Security configuration incomplete" -ForegroundColor Yellow
}

# 14. Billing Integration
Write-Host "`n[14/15] Billing Integration..." -ForegroundColor Yellow
if (Test-Path "apps/api/billing") {
    Write-Host "  ✅ Stripe billing integrated" -ForegroundColor Green
    $score++
} else {
    Write-Host "  ⚠️ Billing module not found" -ForegroundColor Yellow
}

# 15. Git Repository Status
Write-Host "`n[15/15] Git Repository..." -ForegroundColor Yellow
$gitStatus = git status --porcelain 2>&1
if ($gitStatus) {
    $changedFiles = ($gitStatus | Measure-Object -Line).Lines
    Write-Host "  ⚠️ $changedFiles uncommitted files" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Repository clean" -ForegroundColor Green
    $score++
}

# Final Score
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                     READINESS SCORE                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$percentage = [math]::Round(($score / $total) * 100, 1)
Write-Host "  Score: $score/$total ($percentage%)`n" -ForegroundColor Cyan

if ($percentage -ge 90) {
    Write-Host "  🟢 STATUS: PRODUCTION READY" -ForegroundColor Green
    Write-Host "  Platform is ready for deployment`n" -ForegroundColor Green
} elseif ($percentage -ge 75) {
    Write-Host "  🟡 STATUS: STAGING READY" -ForegroundColor Yellow
    Write-Host "  Platform ready for staging, minor issues to fix`n" -ForegroundColor Yellow
} elseif ($percentage -ge 60) {
    Write-Host "  🟠 STATUS: DEVELOPMENT" -ForegroundColor DarkYellow
    Write-Host "  Platform functional but needs work before production`n" -ForegroundColor DarkYellow
} else {
    Write-Host "  🔴 STATUS: NOT READY" -ForegroundColor Red
    Write-Host "  Critical issues must be resolved`n" -ForegroundColor Red
}

# Recommendations
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    RECOMMENDATIONS                             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$recommendations = @()

if (!(Test-Path "node_modules")) {
    $recommendations += "❗ Run: npm install"
}

if ($gitStatus) {
    $recommendations += "❗ Commit pending changes: git add . && git commit -m 'Pre-launch commit'"
}

if (!(Test-Path ".env")) {
    $recommendations += "❗ Create .env file with production credentials"
}

if (!(Test-Path "docs/observability/grafana-dashboards/chart1.png")) {
    $recommendations += "📊 Add Grafana charts to documentation"
}

if ($recommendations.Count -eq 0) {
    Write-Host "  ✅ No critical issues found!`n" -ForegroundColor Green
} else {
    foreach ($rec in $recommendations) {
        Write-Host "  $rec" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

return $percentage


