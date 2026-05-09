param(
    [string]$BaseUrl = "http://127.0.0.1:9080"
)

$ErrorActionPreference = "Continue"

Write-Host "SMOKE START -> $BaseUrl"

try {
    $status = Invoke-RestMethod -Method GET -Uri "$BaseUrl/status?stigma_level=2" -TimeoutSec 10
    Write-Host "PASS /status tide=$($status.tide) ndb=$($status.ndb_score)"
}
catch {
    Write-Host "FAIL /status -> $($_.Exception.Message)"
}

try {
    $sec = Invoke-RestMethod -Method GET -Uri "$BaseUrl/security/status" -TimeoutSec 10
    Write-Host "PASS /security/status risk=$($sec.high_risk) events=$($sec.event_count)"
}
catch {
    Write-Host "FAIL /security/status -> $($_.Exception.Message)"
}

try {
    $events = Invoke-RestMethod -Method GET -Uri "$BaseUrl/security/events?limit=5" -TimeoutSec 10
    $count = if ($events -is [array]) { $events.Count } elseif ($null -eq $events) { 0 } else { 1 }
    Write-Host "PASS /security/events count=$count"
}
catch {
    Write-Host "FAIL /security/events -> $($_.Exception.Message)"
}

$body = @{ ops = @("S", "C"); payload = "AQID"; ttl = 10; stigma_level = 2 } | ConvertTo-Json

try {
    $submit = Invoke-RestMethod -Method POST -Uri "$BaseUrl/submit" -ContentType "application/json" -Body $body -TimeoutSec 10
    Write-Host "PASS POST /submit status=$($submit.status)"
}
catch {
    Write-Host "FAIL POST /submit -> $($_.Exception.Message)"
}

Write-Host "SMOKE END"
