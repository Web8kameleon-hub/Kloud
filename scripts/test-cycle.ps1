#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Kloud Cloud - Comprehensive Test Cycle
.DESCRIPTION
    Tests all system endpoints and generates a detailed report
#>

param(
    [switch]$Verbose = $false,
    [switch]$SaveReport = $true,
    [int]$Timeout = 30
)

# Color output
function Write-Status {
    param([string]$Message, [ValidateSet('OK', 'ERR', 'WRN', 'INF')][string]$Type = 'INF')
    $colors = @{
        'OK'  = 'Green'
        'ERR' = 'Red'
        'WRN' = 'Yellow'
        'INF' = 'Cyan'
    }
    Write-Host "[$Type] $Message" -ForegroundColor $colors[$Type]
}

# API Test Function
function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method = 'GET',
        [string]$Url,
        [hashtable]$Headers = @{},
        [string]$Body = $null
    )

    try {
        $params = @{
            Uri             = $Url
            Method          = $Method
            Headers         = $Headers
            TimeoutSec      = $Timeout
            UseBasicParsing = $true
        }

        if ($Body) {
            $params['Body'] = $Body
            $params['ContentType'] = 'application/json'
        }

        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
            Write-Status "$Name - SUCCESS ($($response.StatusCode))" 'OK'
            return @{
                Name    = $Name
                Status  = 'PASS'
                Code    = $response.StatusCode
                Time    = Get-Date
            }
        }
    }
    catch {
        Write-Status "$Name - FAILED: $($_.Exception.Message)" 'ERR'
        return @{
            Name    = $Name
            Status  = 'FAIL'
            Error   = $_.Exception.Message
            Time    = Get-Date
        }
    }
}

# Main test suite
Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "KLOUD CLOUD - TEST CYCLE" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "`n"

$results = @()
$startTime = Get-Date

# Test 1: API Health Check
Write-Status "Testing API Health..." 'INF'
$results += Test-Endpoint -Name "API Health Check" -Url "http://localhost:8000/health"

# Test 2: System Status
Write-Status "Testing System Status..." 'INF'
$results += Test-Endpoint -Name "System Status" -Url "http://localhost:8000/api/system-status"

# Test 3: Frontend
Write-Status "Testing Frontend (Next.js)..." 'INF'
$results += Test-Endpoint -Name "Frontend Root" -Url "http://localhost:3000"

# Test 4: API Documentation
Write-Status "Testing API Documentation..." 'INF'
$results += Test-Endpoint -Name "OpenAPI Docs" -Url "http://localhost:8000/docs"

# Test 5: ReDoc
Write-Status "Testing ReDoc..." 'INF'
$results += Test-Endpoint -Name "ReDoc Documentation" -Url "http://localhost:8000/redoc"

# Test 6: OpenAPI Schema
Write-Status "Testing OpenAPI Schema..." 'INF'
$results += Test-Endpoint -Name "OpenAPI Schema" -Url "http://localhost:8000/openapi.json"

# Test 7: MESH Service
Write-Status "Testing MESH Service..." 'INF'
try {
    $meshTest = Test-NetConnection -ComputerName localhost -Port 7777 -WarningAction SilentlyContinue
    if ($meshTest.TcpTestSucceeded) {
        Write-Status "MESH Service (port 7777) - ONLINE" 'OK'
        $results += @{
            Name   = "MESH Service"
            Status = 'PASS'
            Code   = 200
            Time   = Get-Date
        }
    }
}
catch {
    Write-Status "MESH Service - OFFLINE" 'WRN'
}

# Test 8: ORCH Service
Write-Status "Testing ORCH Service..." 'INF'
try {
    $orchTest = Test-NetConnection -ComputerName localhost -Port 5555 -WarningAction SilentlyContinue
    if ($orchTest.TcpTestSucceeded) {
        Write-Status "ORCH Service (port 5555) - ONLINE" 'OK'
        $results += @{
            Name   = "ORCH Service"
            Status = 'PASS'
            Code   = 200
            Time   = Get-Date
        }
    }
}
catch {
    Write-Status "ORCH Service - OFFLINE" 'WRN'
}

# Summary Report
$endTime = Get-Date
$duration = $endTime - $startTime
$passCount = ($results | Where-Object { $_.Status -eq 'PASS' }).Count
$failCount = ($results | Where-Object { $_.Status -eq 'FAIL' }).Count
$totalCount = $results.Count

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "TEST RESULTS SUMMARY" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

Write-Host "`nTotal Tests: $totalCount" -ForegroundColor Cyan
Write-Host "Passed: $passCount" -ForegroundColor Green
Write-Host "Failed: $failCount" -ForegroundColor $(if ($failCount -gt 0) { 'Red' } else { 'Green' })
Write-Host "Duration: $($duration.TotalSeconds)s" -ForegroundColor Cyan

$successRate = if ($totalCount -gt 0) { [math]::Round(($passCount / $totalCount) * 100, 2) } else { 0 }
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -eq 100) { 'Green' } else { 'Yellow' })

# Detailed Results
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "DETAILED TEST RESULTS" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

$results | ForEach-Object {
    $statusColor = if ($_.Status -eq 'PASS') { 'Green' } else { 'Red' }
    Write-Host "`n[$($_.Status)] $($_.Name)" -ForegroundColor $statusColor
    if ($_.Code) { Write-Host "  Status Code: $($_.Code)" -ForegroundColor Cyan }
    if ($_.Error) { Write-Host "  Error: $($_.Error)" -ForegroundColor Red }
}

# Save report if requested
if ($SaveReport) {
    $reportPath = "c:\kloud-cloud\logs\test-cycle-$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').json"
    $reportDir = Split-Path $reportPath
    if (-not (Test-Path $reportDir)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    }

    $report = @{
        Timestamp   = Get-Date -Format 'o'
        Duration    = $duration.TotalSeconds
        TotalTests  = $totalCount
        Passed      = $passCount
        Failed      = $failCount
        SuccessRate = $successRate
        Results     = $results
    }

    $report | ConvertTo-Json | Set-Content -Path $reportPath -Encoding UTF8
    Write-Status "Test report saved: $reportPath" 'OK'
}

Write-Host "`n========================================`n" -ForegroundColor Magenta

# Exit with appropriate code
exit $(if ($failCount -eq 0) { 0 } else { 1 })


