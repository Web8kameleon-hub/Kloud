#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Local CLI for Kloud Remote Hosting (kameleon.life @ 46.62.210.251)
.DESCRIPTION
    Execute local commands against the remote hosted instance WITHOUT SSH.
    All commands use HTTPS API to control sovereign nodes and monitoring.
.EXAMPLE
    .\kloud-remote.ps1 status
    .\kloud-remote.ps1 nodes
    .\kloud-remote.ps1 sync-start
    .\kloud-remote.ps1 event "adaptive-test" 42
    .\kloud-remote.ps1 dashboard
.NOTES
    kameleon.life -> 46.62.210.251 (Hetzner)
    All requests proxied with auto TTL
#>

param(
    [Parameter(Position = 0)]
    [string]$Command,
    
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

$REMOTE_HOST = "kameleon.life"
$REMOTE_IP = "46.62.210.251"
$API_BASE = "https://$REMOTE_HOST"
$TIMEOUT = 15

# Control plane endpoints
$CTRL_PATH = "/api/v1/control-plane"
$RESONANT_PATH = "/api/v1/resonant"
$NANOGRID_PATH = "/api/v1/nanogrid"

# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

function Write-Status {
    param([string]$Message, [string]$Color = "Cyan")
    Write-Host "→ $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warn {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}


function Invoke-KloudAPI {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null,
        [switch]$Raw
    )
    
    try {
        $uri = "$API_BASE$Endpoint"
        $headers = @{
            "Content-Type" = "application/json"
            "User-Agent"   = "Kloud-Remote-CLI/1.0"
        }
        
        if ($env:KLOUD_API_KEY) {
            $headers["Authorization"] = "Bearer $env:KLOUD_API_KEY"
        }
        
        $params = @{
            Uri        = $uri
            Method     = $Method
            Headers    = $headers
            TimeoutSec = $TIMEOUT
        }
        
        if ($Body) {
            $params["Body"] = ($Body | ConvertTo-Json -Depth 10)
        }
        
        Write-Debug "API Call: $Method $uri"
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        if ($Raw) {
            return $response
        }
        
        try {
            return $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
        }
        catch {
            return $response.Content
        }
    }
    catch {
        $errMsg = $_.Exception.Message
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $body = $reader.ReadToEnd()
            $errMsg = "$errMsg`n$body"
        }
        Write-Error-Custom "API Error: $errMsg"
        return $null
    }
}

function Format-Number {
    param([float]$Value)
    return $Value.ToString("0.00")
}

function Get-StateIcon {
    param([string]$State)
    switch ($State.ToLower()) {
        "active" { return "🟢" }
        "degraded" { return "🟡" }
        "recovering" { return "🟠" }
        "error" { return "🔴" }
        default { return "⚫" }
    }
}

function Get-QualityIcon {
    param([string]$Quality)
    switch ($Quality.ToLower()) {
        "excellent" { return "⭐" }
        "good" { return "🟢" }
        "fair" { return "🟡" }
        "poor" { return "🟠" }
        "critical" { return "🔴" }
        default { return "?" }
    }
}

# ════════════════════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ════════════════════════════════════════════════════════════════════════════

function Command-Status {
    Write-Status "Checking remote instance status..."
    Write-Host ""
    
    # Health check
    $health = Invoke-KloudAPI -Endpoint "/health"
    if ($health.status -eq "ok") {
        Write-Success "💚 Remote instance is HEALTHY"
        Write-Host "  Service: $($health.service) | Time: $($health.timestamp_utc)"
    }
    else {
        Write-Error-Custom "Remote instance unreachable"
        return
    }
    
    Write-Host ""
    
    # Sync loop status
    Write-Status "Sync Loop"
    $sync = Invoke-KloudAPI -Endpoint "$CTRL_PATH/sync-loop/status"
    if ($sync) {
        $running = if ($sync.running) { "✓ RUNNING" } else { "⊘ STOPPED" }
        Write-Host "  State: $running"
        Write-Host "  Interval: $($sync.interval_seconds)s"
        Write-Host "  Cycles: $($sync.cycles)"
        Write-Host "  Last: $($sync.last_run_utc)"
    }
    
    Write-Host ""
    Write-Host "Remote: $REMOTE_HOST (→ $REMOTE_IP)" -ForegroundColor Gray
}

function Command-Nodes {
    Write-Status "Fetching node topology..."
    Write-Host ""
    
    $nodes = Invoke-KloudAPI -Endpoint "$CTRL_PATH/scan-print?limit=100"
    if (-not $nodes) { return }
    
    Write-Host "🌐 Fabric: $($nodes.fabric_profile)" -ForegroundColor Cyan
    Write-Host "📊 Total: $($nodes.count) nodes | Time: $($nodes.timestamp_utc)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($nodes.items) {
        foreach ($node in $nodes.items) {
            $icon = Get-StateIcon $node.state
            $qicon = Get-QualityIcon $node.ndb_quality
            
            Write-Host "$icon [$($node.state.ToUpper())] $($node.service)" `
                -ForegroundColor $(if ($node.state -eq "active") { "Green" } else { "Yellow" })
            Write-Host "   $qicon NDB: $($node.ndb_quality) | Quality: $(Format-Number $node.quality_score) | Latency: $($node.response_time_ms)ms"
        }
    }
    
    Write-Host ""
}

function Command-SyncStart {
    Write-Status "Starting health sync loop..."
    
    $result = Invoke-KloudAPI -Endpoint "$CTRL_PATH/sync/loop/start?interval_seconds=5" -Method POST
    if ($result -and ($result.status -eq "started" -or $result.status -eq "already-running")) {
        Write-Success "Sync loop is running (5s interval)"
        Write-Host "  Cycles: $($result.cycles)"
    }
    else {
        Write-Error-Custom "Failed to start sync loop"
    }
}

function Command-SyncStop {
    Write-Status "Stopping health sync loop..."
    
    $result = Invoke-KloudAPI -Endpoint "$CTRL_PATH/sync/loop/stop" -Method POST
    if ($result -and $result.status -eq "stopped") {
        Write-Success "Sync loop stopped"
        Write-Host "  Last: $($result.last_run_utc) | Cycles: $($result.cycles)"
    }
    else {
        Write-Error-Custom "Failed to stop sync loop"
    }
}

function Command-Sync {
    Write-Status "Running one-time health sync..."
    
    $result = Invoke-KloudAPI -Endpoint "$CTRL_PATH/sync" -Method POST
    if ($result -and $result.status -eq "synced") {
        Write-Success "One-time sync complete"
        Write-Host "  Nodes: $($result.nodes_total)"
    }
    else {
        Write-Error-Custom "Sync failed"
    }
}

function Command-Event {
    param([string]$EventName, [string]$Value = "1")
    
    if (-not $EventName) {
        Write-Error-Custom "Usage: kloud-remote event <name> [value]"
        return
    }
    
    Write-Status "Posting resonant event: $EventName = $Value"
    
    $body = @{
        event        = $EventName
        value        = if ([int]::TryParse($Value, [ref]$null)) { [int]$Value } else { $Value }
        timestamp_ms = [int64]([datetime]::UtcNow.Subtract([datetime]'1970-01-01').TotalMilliseconds)
    }
    
    $result = Invoke-KloudAPI -Endpoint "$RESONANT_PATH/events/adaptive" -Method POST -Body $body
    if ($result -and $result.status -eq "ok") {
        Write-Success "Event posted"
    }
    else {
        Write-Error-Custom "Failed to post event"
    }
}

function Command-Dashboard {
    Write-Status "Opening remote dashboard..."
    Write-Host ""
    Write-Host "Dashboard: https://$REMOTE_HOST/dashboard" -ForegroundColor Cyan
    Write-Host ""
    
    Start-Process "https://$REMOTE_HOST/dashboard" -ErrorAction SilentlyContinue
    Write-Success "Opened in browser"
}

function Command-Topology {
    Write-Status "Fetching fabric topology..."
    Write-Host ""
    
    $topo = Invoke-KloudAPI -Endpoint "$CTRL_PATH/topology"
    if (-not $topo) { return }
    
    Write-Host "🌐 Topology: $($topo.fabric_profile)" -ForegroundColor Cyan
    Write-Host "📍 Active Members: $($topo.active_members) / $($topo.nodes_total)"
    Write-Host ""
    
    if ($topo.members) {
        Write-Host "Members:" -ForegroundColor Yellow
        foreach ($member in $topo.members) {
            Write-Host "  └─ $($member.node_id)"
            Write-Host "     Endpoint: $($member.endpoint)"
            Write-Host "     Transport: $($member.transport -join ', ')" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
}

function Command-Bootstrap {
    Write-Status "Bootstrapping remote control plane..."
    
    $result = Invoke-KloudAPI -Endpoint "$CTRL_PATH/bootstrap" -Method POST
    if ($result -and $result.status -eq "bootstrapped") {
        Write-Success "Bootstrap complete"
        Write-Host "  Available: $($result.available_count) services"
        Write-Host "  Services:"
        foreach ($svc in $result.registered_services) {
            Write-Host "    • $svc"
        }
    }
    else {
        Write-Error-Custom "Bootstrap failed"
    }
}

function Command-Watch {
    Write-Status "Watching nodes (Ctrl+C to stop)..."
    Write-Host ""
    
    while ($true) {
        Clear-Host
        Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host "  Kloud Sovereign Nodes Monitor" -ForegroundColor Cyan
        Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Yellow
        Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
        Write-Host ""
        
        $result = Invoke-KloudAPI -Endpoint "$CTRL_PATH/scan-print"
        
        if ($result -and $result.items) {
            foreach ($item in $result.items) {
                $state_emoji = switch ($item.state) {
                    "active" { "✓" }
                    "degraded" { "⚠" }
                    "recovering" { "↻" }
                    default { "✗" }
                }
                
                $tide_emoji = switch ($item.tide) {
                    "low" { "🟢" }
                    "normal" { "🟡" }
                    "high" { "🔴" }
                    default { "⚫" }
                }
                
                $ndb_bars = "━" * [int]($item.quality_score * 10)
                $ndb_empty = "░" * ([int](10 - ($item.quality_score * 10)))
                
                Write-Host "$state_emoji Node: $($item.service)" -ForegroundColor Cyan
                Write-Host "   NDB: $tide_emoji [$ndb_bars$ndb_empty] $($item.ndb_quality)" 
                Write-Host "   Score: $(Format-Number $item.quality_score) | Latency: $($item.response_time_ms)ms"
                Write-Host ""
            }
        }
        
        Write-Host "⟳ Refreshing in 5 seconds... (Ctrl+C to stop)" -ForegroundColor Gray
        Start-Sleep -Seconds 5
    }
}

function Command-Help {
    Write-Host @"
╔════════════════════════════════════════════════════════════════════════════╗
║                  Kloud Remote CLI - Local Commands                         ║
║              (Control https://$REMOTE_HOST @ $REMOTE_IP)            ║
╚════════════════════════════════════════════════════════════════════════════╝

USAGE:
  .\kloud-remote.ps1 <command> [args...]

COMMANDS:
  
  Status & Monitoring:
    status              Display health status & sync loop state
    nodes               List all sovereign nodes with TIDE/NDB metrics
    topology            Show fabric topology and active members
    watch               Real-time node monitoring with refresh (Ctrl+C to stop)
    
  Sync Control:
    sync-start          Start continuous health sync loop (5s interval)
    sync-stop           Stop health sync loop
    sync                Run one-time health synchronization
    
  Events:
    event <name> [val]  Post resonant event (e.g., "test" 42)
    
  Setup:
    bootstrap           Initialize remote control plane
    
  Utilities:
    dashboard           Open remote dashboard in browser
    help                Show this help message
    version             Show version info

EXAMPLES:
  
  # Check remote status
  .\kloud-remote.ps1 status
  
  # List nodes with quality metrics
  .\kloud-remote.ps1 nodes
  
  # Start continuous monitoring
  .\kloud-remote.ps1 sync-start
  
  # Watch live node updates
  .\kloud-remote.ps1 watch
  
  # Post custom event
  .\kloud-remote.ps1 event "adaptive-test" 42
  
  # Open dashboard
  .\kloud-remote.ps1 dashboard

ENVIRONMENT VARIABLES:
  
  KLOUD_API_KEY       API authentication key (optional)
  KLOUD_DEBUG         Enable debug logging

REMOTE ENDPOINTS:

  REST API:           https://$REMOTE_HOST/api/v1/control-plane/*
  Resonant Events:    https://$REMOTE_HOST/api/v1/resonant/*
  Health Check:       https://$REMOTE_HOST/health
  Dashboard:          https://$REMOTE_HOST/dashboard

NOTE:
  All requests go through HTTPS proxy (auto TTL).
  No SSH or direct access needed - local commands only!

"@
}

function Command-Version {
    Write-Host "Kloud Remote CLI v1.0" -ForegroundColor Cyan
    Write-Host "  Remote: https://$REMOTE_HOST (→ $REMOTE_IP)" -ForegroundColor Gray
    Write-Host "  Type: Sovereign Fabric Control" -ForegroundColor Gray
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN DISPATCHER
# ════════════════════════════════════════════════════════════════════════════

if (-not $Command) {
    Command-Help
    exit 0
}

switch ($Command.ToLower()) {
    "status" { Command-Status }
    "nodes" { Command-Nodes }
    "topology" { Command-Topology }
    "sync" { Command-Sync }
    "sync-start" { Command-SyncStart }
    "sync-stop" { Command-SyncStop }
    "event" { Command-Event @Args }
    "bootstrap" { Command-Bootstrap }
    "watch" { Command-Watch }
    "dashboard" { Command-Dashboard }
    "help" { Command-Help }
    "version" { Command-Version }
    default {
        Write-Error-Custom "Unknown command: $Command"
        Write-Host "Run '.\kloud-remote.ps1 help' for usage" -ForegroundColor Gray
        exit 1
    }
}

For detailed documentation, see:
docs/LOCAL_COMMANDS_FOR_REMOTE_HOSTING.md
"@
    }
    
    default {
        if ($Command) {
            Write-Error-Custom "Unknown command: $Command"
        }
        & $PSCommandPath "help"
    }
}

function FormatNumber {
    param([float]$Value)
    return $Value.ToString("0.00")
}
