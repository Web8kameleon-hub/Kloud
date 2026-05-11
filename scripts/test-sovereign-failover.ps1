<#
Evaluate sovereign failover order using policy + health checks.

Usage:
  .\scripts\test-sovereign-failover.ps1 -PolicyPath docs/templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json
#>

param(
    [string]$PolicyPath = "docs/templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $PolicyPath)) {
    throw "Policy file not found: $PolicyPath"
}

$policy = Get-Content $PolicyPath -Raw | ConvertFrom-Json
$records = @($policy.records)
$ordered = @()

function Test-Health {
    param([string]$Url)
    try {
        $resp = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5
        return $resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300
    }
    catch {
        return $false
    }
}

foreach ($id in $policy.failover.order) {
    $rec = $records | Where-Object { $_.id -eq $id } | Select-Object -First 1
    if ($null -eq $rec) { continue }
    $healthy = Test-Health -Url $rec.health_url
    $ordered += [pscustomobject]@{
        id        = $rec.id
        endpoint  = $rec.health_url
        target_ip = $rec.value
        weight    = $rec.weight
        region    = $rec.region
        healthy   = $healthy
    }
}

$active = $ordered | Where-Object { $_.healthy -eq $true }
$primary = $active | Select-Object -First 1

Write-Host "=== Sovereign Failover Drill ===" -ForegroundColor Cyan
Write-Host "Domain: $($policy.domain)"
Write-Host "Strategy: $($policy.strategy)"
Write-Host "TTL: $($policy.ttl_seconds)s"
Write-Host ""

$ordered | Format-Table -AutoSize

if ($null -eq $primary) {
    Write-Host "No healthy PoP found. Failover target is unavailable." -ForegroundColor Red
    exit 2
}

Write-Host "Recommended active primary now: $($primary.id) ($($primary.target_ip))" -ForegroundColor Green
exit 0
