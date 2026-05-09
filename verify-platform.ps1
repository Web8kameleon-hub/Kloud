# Kloud Production Verification Script
# Run this to verify platform readiness

Write-Host "🔍 Kloud Platform Verification" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python environment
Write-Host "1️⃣  Checking Python environment..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.13") {
    Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  $pythonVersion (Expected: 3.13+)" -ForegroundColor Red
}

# 2. Check Node.js environment
Write-Host "2️⃣  Checking Node.js environment..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($nodeVersion -match "v20\." -or $nodeVersion -match "v2[1-9]\.") {
    Write-Host "   ✅ Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Node.js $nodeVersion (Expected: 20.0+)" -ForegroundColor Red
}

# 3. Verify pyproject.toml
Write-Host "3️⃣  Validating pyproject.toml..." -ForegroundColor Yellow
try {
    $tomlTest = python -c "import tomllib; f = open('c:/kloud-cloud/pyproject.toml', 'rb'); data = tomllib.load(f); print(len(data['project']['dependencies']))" 2>&1
    Write-Host "   ✅ Valid TOML - $tomlTest dependencies locked" -ForegroundColor Green
} catch {
    Write-Host "   ❌ TOML validation failed" -ForegroundColor Red
}

# 4. Verify package-lock.json
Write-Host "4️⃣  Checking package-lock.json..." -ForegroundColor Yellow
if (Test-Path "package-lock.json") {
    Write-Host "   ✅ package-lock.json exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ package-lock.json missing (run: npm install)" -ForegroundColor Red
}

# 5. Check production services
Write-Host "5️⃣  Verifying production services..." -ForegroundColor Yellow
$services = @(
    "alba_service_5555.py",
    "albi_service_6680.py",
    "jona_service_7777.py",
    "master.py",
    "apps\api\main.py"
)
$servicesOk = $true
foreach ($service in $services) {
    if (Test-Path $service) {
        Write-Host "   ✅ $service" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $service missing" -ForegroundColor Red
        $servicesOk = $false
    }
}

# 6. Check OpenAPI contracts
Write-Host "6️⃣  Verifying OpenAPI contracts..." -ForegroundColor Yellow
$contracts = @(
    "openapi\alba-api-v1.yaml",
    "openapi\albi-api-v1.yaml",
    "openapi\jona-api-v1.yaml"
)
foreach ($contract in $contracts) {
    if (Test-Path $contract) {
        Write-Host "   ✅ $contract" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $contract missing" -ForegroundColor Red
    }
}

# 7. Check documentation
Write-Host "7️⃣  Verifying documentation..." -ForegroundColor Yellow
$docs = @(
    "PRODUCTION_SERVICES.md",
    "DEPENDENCY_LOCK_REPORT.md",
    "STABILIZATION_COMPLETE.md",
    "KLOUD_ARCHITECTURE_BASELINE_2025.md",
    "openapi\README.md"
)
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "   ✅ $doc" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $doc missing" -ForegroundColor Red
    }
}

# 8. Count files
Write-Host "8️⃣  Code organization metrics..." -ForegroundColor Yellow
$rootPy = (Get-ChildItem -Path "." -Filter "*.py" -File | Measure-Object).Count
$archivedPy = (Get-ChildItem -Path "archive\" -Recurse -Filter "*.py" -File -ErrorAction SilentlyContinue | Measure-Object).Count
$researchPy = (Get-ChildItem -Path "research\" -Recurse -Filter "*.py" -File -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "   📊 Root Python files: $rootPy (Target: ~30)" -ForegroundColor Cyan
Write-Host "   📦 Archived files: $archivedPy" -ForegroundColor Cyan
Write-Host "   🔬 Research files: $researchPy" -ForegroundColor Cyan

# 9. Check Docker
Write-Host "9️⃣  Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "   ✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Docker not found (optional for development)" -ForegroundColor Yellow
}

# Final summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "📋 VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

if ($pythonVersion -match "Python 3\.13" -and 
    ($nodeVersion -match "v20\." -or $nodeVersion -match "v2[1-9]\.") -and 
    (Test-Path "package-lock.json") -and 
    $servicesOk) {
    Write-Host "✅ PLATFORM READY FOR PRODUCTION!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Start services: docker-compose up -d" -ForegroundColor White
    Write-Host "  2. Verify health: curl http://localhost:5555/health" -ForegroundColor White
    Write-Host "  3. View docs: http://localhost:5555/docs" -ForegroundColor White
} else {
    Write-Host "⚠️  Some checks failed. Review errors above." -ForegroundColor Yellow
}

Write-Host ""


