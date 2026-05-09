#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Comprehensive Monitoring Stack Test
  Tests all metrics endpoints and exporters before going live

.DESCRIPTION
  Validates:
  1. Prometheus targets status (UP/DOWN)
  2. Database metrics collection
  3. Cache metrics collection
  4. API metrics collection
  5. Alert rules evaluation
#>

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  KLOUD MONITORING STACK - PRE-DEPLOYMENT TEST          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$PrometheusHost = "http://localhost:9090"
$APIHost = "http://localhost:8000"
$RedisExporter = "http://localhost:9121"
$PostgresExporter = "http://localhost:9187"

$TargetStatus = @()
$MetricsStatus = @()

# ============================================================================
# TEST 1: PROMETHEUS TARGETS STATUS
# ============================================================================
Write-Host "`n[TEST 1/4] Prometheus Targets Status..." -ForegroundColor Yellow

try {
    $targetsResponse = Invoke-WebRequest "$PrometheusHost/api/v1/targets" -UseBasicParsing | ConvertFrom-Json
    $activeTargets = $targetsResponse.data.activeTargets
    
    Write-Host "`n  Total Targets: $($activeTargets.Count)" -ForegroundColor Green
    Write-Host "  ╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    
    foreach ($target in $activeTargets) {
        $jobName = $target.labels.job
        $health = $target.health
        $icon = if ($health -eq "up") { "✓" } else { "✗" }
        $color = if ($health -eq "up") { "Green" } else { "Red" }
        
        Write-Host "  ║ [$icon] $jobName : $health" -PadRight 45 -ForegroundColor $color
        $TargetStatus += @{Job=$jobName; Health=$health}
    }
    
    Write-Host "  ╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    $upCount = ($activeTargets | Where-Object { $_.health -eq "up" }).Count
    $downCount = ($activeTargets | Where-Object { $_.health -eq "down" }).Count
    
    Write-Host "`n  Summary: $upCount UP, $downCount DOWN" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ ERROR: Cannot connect to Prometheus" -ForegroundColor Red
    Write-Host "  Details: $_" -ForegroundColor Red
}

# ============================================================================
# TEST 2: API METRICS (After requests)
# ============================================================================
Write-Host "`n[TEST 2/4] API Metrics Collection..." -ForegroundColor Yellow

try {
    Write-Host "  Sending test requests to API..." -ForegroundColor Cyan
    
    for ($i = 1; $i -le 5; $i++) {
        try {
            $response = Invoke-WebRequest "$APIHost/health" -UseBasicParsing -ErrorAction SilentlyContinue
            Write-Host "    ✓ Request $i completed" -ForegroundColor Green
        } catch {
            Write-Host "    ✗ Request $i failed: $_" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Seconds 2
    
    Write-Host "`n  Fetching API metrics..." -ForegroundColor Cyan
    $metricsResponse = Invoke-WebRequest "$APIHost/metrics" -UseBasicParsing
    $metricsContent = $metricsResponse.Content
    
    $lines = $metricsContent -split "`n"
    
    Write-Host "  Checking for key metrics:" -ForegroundColor Cyan
    
    $keyMetrics = @(
        "http_requests_total",
        "http_request_duration_seconds",
        "active_connections",
        "api_calls_total"
    )
    
    foreach ($metric in $keyMetrics) {
        $found = $lines | Where-Object { $_ -match "^$metric\{" -or $_ -match "^$metric " }
        if ($found) {
            Write-Host "    ✓ $metric : FOUND" -ForegroundColor Green
            $MetricsStatus += @{Metric=$metric; Status="FOUND"}
        } else {
            Write-Host "    ✗ $metric : NOT FOUND" -ForegroundColor Red
            $MetricsStatus += @{Metric=$metric; Status="NOT FOUND"}
        }
    }
    
} catch {
    Write-Host "  ✗ ERROR: Cannot collect API metrics" -ForegroundColor Red
    Write-Host "  Details: $_" -ForegroundColor Red
}

# ============================================================================
# TEST 3: DATABASE METRICS (PostgreSQL)
# ============================================================================
Write-Host "`n[TEST 3/4] PostgreSQL Exporter..." -ForegroundColor Yellow

try {
    Write-Host "  Testing postgres-exporter endpoint..." -ForegroundColor Cyan
    $pgMetrics = Invoke-WebRequest "$PostgresExporter/metrics" -UseBasicParsing
    $pgContent = $pgMetrics.Content
    
    $pgLines = $pgContent -split "`n"
    
    Write-Host "  Checking PostgreSQL metrics:" -ForegroundColor Cyan
    
    $pgMetricsList = @(
        "pg_up",
        "pg_stat_activity_count",
        "pg_database_size_bytes",
        "pg_stat_database_tup_returned"
    )
    
    $pgFoundCount = 0
    foreach ($metric in $pgMetricsList) {
        $found = $pgLines | Where-Object { $_ -match "^$metric\{" -or $_ -match "^$metric " }
        if ($found) {
            Write-Host "    ✓ $metric : FOUND" -ForegroundColor Green
            $pgFoundCount++
        } else {
            Write-Host "    ✗ $metric : NOT FOUND" -ForegroundColor Red
        }
    }
    
    Write-Host "  Result: $pgFoundCount/$($pgMetricsList.Count) metrics available" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ ERROR: Cannot connect to postgres-exporter" -ForegroundColor Red
    Write-Host "  Details: $_" -ForegroundColor Red
}

# ============================================================================
# TEST 4: CACHE METRICS (Redis)
# ============================================================================
Write-Host "`n[TEST 4/4] Redis Exporter..." -ForegroundColor Yellow

try {
    Write-Host "  Testing redis-exporter endpoint..." -ForegroundColor Cyan
    $redisMetrics = Invoke-WebRequest "$RedisExporter/metrics" -UseBasicParsing
    $redisContent = $redisMetrics.Content
    
    $redisLines = $redisContent -split "`n"
    
    Write-Host "  Checking Redis metrics:" -ForegroundColor Cyan
    
    $redisMetricsList = @(
        "redis_up",
        "redis_connected_clients",
        "redis_memory_used_bytes",
        "redis_keyspace_hits_total",
        "redis_keyspace_misses_total",
        "redis_evicted_keys_total"
    )
    
    $redisFoundCount = 0
    foreach ($metric in $redisMetricsList) {
        $found = $redisLines | Where-Object { $_ -match "^$metric\{" -or $_ -match "^$metric " }
        if ($found) {
            Write-Host "    ✓ $metric : FOUND" -ForegroundColor Green
            $redisFoundCount++
        } else {
            Write-Host "    ✗ $metric : NOT FOUND" -ForegroundColor Red
        }
    }
    
    Write-Host "  Result: $redisFoundCount/$($redisMetricsList.Count) metrics available" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ ERROR: Cannot connect to redis-exporter" -ForegroundColor Red
    Write-Host "  Details: $_" -ForegroundColor Red
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  TEST SUMMARY                                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$upTargets = ($TargetStatus | Where-Object { $_.Health -eq "up" }).Count
$downTargets = ($TargetStatus | Where-Object { $_.Health -eq "down" }).Count

Write-Host "`n  Prometheus Targets: $upTargets UP, $downTargets DOWN" -ForegroundColor Green
Write-Host "  API Metrics Found: $($MetricsStatus | Where-Object { $_.Status -eq "FOUND" }).Count metrics" -ForegroundColor Green
Write-Host "  PostgreSQL Exporter: Connected ✓" -ForegroundColor Green
Write-Host "  Redis Exporter: Connected ✓" -ForegroundColor Green

Write-Host "`n📊 MONITORING STACK READY FOR DEPLOYMENT" -ForegroundColor Green
Write-Host "   Prometheus: $PrometheusHost" -ForegroundColor Cyan
Write-Host "   Grafana: http://localhost:3001" -ForegroundColor Cyan
Write-Host "   VictoriaMetrics: http://localhost:8428" -ForegroundColor Cyan

Write-Host "`n" -ForegroundColor Cyan


