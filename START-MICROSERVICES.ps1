# ═══════════════════════════════════════════════════════════════════════════════════════════════════
# START-MICROSERVICES.ps1 - Kloud Cloud Full Microservices Startup
# ═══════════════════════════════════════════════════════════════════════════════════════════════════
#
# Script për nisjen e të gjithë microservices në Docker
# 
# Përdorimi:
#   .\START-MICROSERVICES.ps1                    # Start all
#   .\START-MICROSERVICES.ps1 -Profile core      # Start core services only
#   .\START-MICROSERVICES.ps1 -Profile labs      # Start labs only
#   .\START-MICROSERVICES.ps1 -Service alba      # Start single service
#   .\START-MICROSERVICES.ps1 -Stop              # Stop all
#   .\START-MICROSERVICES.ps1 -Status            # Check status
#
# ═══════════════════════════════════════════════════════════════════════════════════════════════════

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("core", "labs", "datasources", "all")]
    [string]$Profile = "all",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "",
    
    [switch]$Stop,
    [switch]$Status,
    [switch]$Build,
    [switch]$Logs,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ComposeFile = "docker-compose.microservices.yml"

# Colors
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Header = "Magenta"
}

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("═" * 80) -ForegroundColor $Colors.Header
    Write-Host $Text -ForegroundColor $Colors.Header
    Write-Host ("═" * 80) -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Step {
    param([string]$Text, [string]$Status = "INFO")
    $color = switch($Status) {
        "OK" { $Colors.Success }
        "ERROR" { $Colors.Error }
        "WARN" { $Colors.Warning }
        default { $Colors.Info }
    }
    $emoji = switch($Status) {
        "OK" { "✅" }
        "ERROR" { "❌" }
        "WARN" { "⚠️" }
        default { "ℹ️" }
    }
    Write-Host "$emoji $Text" -ForegroundColor $color
}

# Service profiles
$Profiles = @{
    core = @(
        "postgres", "redis", "neo4j", "victoriametrics",
        "alba", "albi", "jona", "asi",
        "ocean-core"
    )
    labs = @(
        "lab-elbasan", "lab-tirana", "lab-durres", "lab-vlore", "lab-shkoder",
        "lab-korce", "lab-saranda", "lab-prishtina", "lab-kostur", "lab-athens",
        "lab-rome", "lab-zurich", "lab-beograd", "lab-sofia", "lab-zagreb",
        "lab-ljubljana", "lab-vienna", "lab-prague", "lab-budapest", "lab-bucharest",
        "lab-istanbul", "lab-cairo", "lab-jerusalem"
    )
    datasources = @(
        "datasource-europe", "datasource-americas", "datasource-asia-china",
        "datasource-india-south-asia", "datasource-africa-middle-east",
        "datasource-oceania-pacific", "datasource-central-asia"
    )
    intelligence = @(
        "agiem", "personas", "blerina", "alba-idle"
    )
    saas = @(
        "saas-api", "marketplace", "api", "web"
    )
    services = @(
        "reporting", "excel", "behavioral", "economy", "aviation"
    )
}

Write-Header "🚀 KLOUD CLOUD MICROSERVICES"
Write-Host "📅 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "📁 Compose File: $ComposeFile"
Write-Host ""

# Check if compose file exists
if (-not (Test-Path $ComposeFile)) {
    Write-Step "Compose file not found: $ComposeFile" "ERROR"
    exit 1
}

# Check Docker is running
try {
    docker info | Out-Null
    Write-Step "Docker is running" "OK"
} catch {
    Write-Step "Docker is not running. Please start Docker Desktop." "ERROR"
    exit 1
}

# Handle actions
if ($Clean) {
    Write-Header "🧹 CLEANING ALL CONTAINERS AND VOLUMES"
    docker-compose -f $ComposeFile down -v --remove-orphans
    docker system prune -f
    Write-Step "Cleanup complete" "OK"
    exit 0
}

if ($Stop) {
    Write-Header "🛑 STOPPING ALL SERVICES"
    docker-compose -f $ComposeFile down
    Write-Step "All services stopped" "OK"
    exit 0
}

if ($Status) {
    Write-Header "📊 SERVICE STATUS"
    docker-compose -f $ComposeFile ps
    
    Write-Host ""
    Write-Host "📈 Container Statistics:" -ForegroundColor $Colors.Header
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.Status}}" 2>$null
    exit 0
}

if ($Logs -and $Service) {
    Write-Header "📜 LOGS FOR: $Service"
    docker-compose -f $ComposeFile logs -f $Service
    exit 0
}

# Build if requested
if ($Build) {
    Write-Header "🔨 BUILDING ALL IMAGES"
    docker-compose -f $ComposeFile build --parallel
    Write-Step "Build complete" "OK"
}

# Start services based on profile or single service
if ($Service) {
    Write-Header "🚀 STARTING SINGLE SERVICE: $Service"
    docker-compose -f $ComposeFile up -d $Service
    Write-Step "$Service started" "OK"
} elseif ($Profile -eq "all") {
    Write-Header "🚀 STARTING ALL MICROSERVICES (50+ CONTAINERS)"
    
    # Start in order to respect dependencies
    Write-Step "Starting Databases..." "INFO"
    docker-compose -f $ComposeFile up -d postgres redis neo4j victoriametrics
    Start-Sleep -Seconds 10
    
    Write-Step "Starting ASI Trinity (Alba, Albi, Jona, ASI)..." "INFO"
    docker-compose -f $ComposeFile up -d alba albi jona asi
    Start-Sleep -Seconds 5
    
    Write-Step "Starting Ocean Core..." "INFO"
    docker-compose -f $ComposeFile up -d ocean-core
    Start-Sleep -Seconds 3
    
    Write-Step "Starting Intelligence Layer (AGIEM, Personas, Blerina)..." "INFO"
    docker-compose -f $ComposeFile up -d agiem personas blerina alba-idle
    Start-Sleep -Seconds 3
    
    Write-Step "Starting Data Sources (7 regions)..." "INFO"
    docker-compose -f $ComposeFile up -d `
        datasource-europe datasource-americas datasource-asia-china `
        datasource-india-south-asia datasource-africa-middle-east `
        datasource-oceania-pacific datasource-central-asia
    Start-Sleep -Seconds 3
    
    Write-Step "Starting 23 Laboratories..." "INFO"
    docker-compose -f $ComposeFile up -d `
        lab-elbasan lab-tirana lab-durres lab-vlore lab-shkoder `
        lab-korce lab-saranda lab-prishtina lab-kostur lab-athens `
        lab-rome lab-zurich lab-beograd lab-sofia lab-zagreb `
        lab-ljubljana lab-vienna lab-prague lab-budapest lab-bucharest `
        lab-istanbul lab-cairo lab-jerusalem
    Start-Sleep -Seconds 3
    
    Write-Step "Starting SaaS & Services..." "INFO"
    docker-compose -f $ComposeFile up -d `
        saas-api marketplace api web `
        reporting excel behavioral economy aviation
    
    Write-Step "All services started!" "OK"
} else {
    # Start specific profile
    $services = $Profiles[$Profile]
    if (-not $services) {
        Write-Step "Unknown profile: $Profile" "ERROR"
        exit 1
    }
    
    Write-Header "🚀 STARTING PROFILE: $Profile ($($services.Count) services)"
    docker-compose -f $ComposeFile up -d $services
    Write-Step "Profile '$Profile' started" "OK"
}

# Wait a bit and show status
Start-Sleep -Seconds 5

Write-Header "📊 RUNNING CONTAINERS"
docker-compose -f $ComposeFile ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host ("═" * 80) -ForegroundColor $Colors.Success
Write-Host "✅ KLOUD CLOUD MICROSERVICES STARTED!" -ForegroundColor $Colors.Success
Write-Host ("═" * 80) -ForegroundColor $Colors.Success
Write-Host ""
Write-Host "🔗 Quick Links:" -ForegroundColor $Colors.Info
Write-Host "   • Ocean Core:     http://localhost:8030" -ForegroundColor White
Write-Host "   • Alba IDLE:      http://localhost:8031 (Status Chat)" -ForegroundColor White
Write-Host "   • SaaS API:       http://localhost:8040" -ForegroundColor White
Write-Host "   • Web Frontend:   http://localhost:3000" -ForegroundColor White
Write-Host "   • API Gateway:    http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "🔧 ASI Trinity:" -ForegroundColor $Colors.Info
Write-Host "   • Alba:           http://localhost:5555" -ForegroundColor White
Write-Host "   • Albi:           http://localhost:6680" -ForegroundColor White
Write-Host "   • Jona:           http://localhost:7777" -ForegroundColor White
Write-Host "   • ASI:            http://localhost:9094" -ForegroundColor White
Write-Host ""
Write-Host "📊 Management:" -ForegroundColor $Colors.Info
Write-Host "   • AGIEM:          http://localhost:9300" -ForegroundColor White
Write-Host "   • Personas:       http://localhost:9200" -ForegroundColor White
Write-Host "   • Blerina:        http://localhost:8035" -ForegroundColor White
Write-Host ""
Write-Host "🏛️ Labs (9101-9123)  |  📡 DataSources (9301-9307)" -ForegroundColor $Colors.Info
Write-Host ""
Write-Host "📝 Commands:" -ForegroundColor $Colors.Warning
Write-Host "   .\START-MICROSERVICES.ps1 -Status    # Check status"
Write-Host "   .\START-MICROSERVICES.ps1 -Stop      # Stop all"
Write-Host "   .\START-MICROSERVICES.ps1 -Logs -Service <name>  # View logs"
Write-Host ""

