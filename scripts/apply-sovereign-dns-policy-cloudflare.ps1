<#
Apply sovereign DNS policy template to Cloudflare DNS records.

Default behavior is safe:
- reads policy
- prints planned actions
- only applies when -Apply is specified

Usage examples:
  .\scripts\apply-sovereign-dns-policy-cloudflare.ps1 -ZoneId <zone> -ApiToken <token> -DryRun
  .\scripts\apply-sovereign-dns-policy-cloudflare.ps1 -ZoneId <zone> -ApiToken <token> -Apply
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ZoneId,

    [Parameter(Mandatory = $true)]
    [string]$ApiToken,

    [string]$PolicyPath = "docs/templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json",

    [switch]$Apply,
    [switch]$DryRun,
    [switch]$DisableUnhealthy,
    [switch]$Proxied
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $PolicyPath)) {
    throw "Policy file not found: $PolicyPath"
}

$policy = Get-Content $PolicyPath -Raw | ConvertFrom-Json
$headers = @{
    "Authorization" = "Bearer $ApiToken"
    "Content-Type"  = "application/json"
}

function Invoke-CFJson {
    param(
        [string]$Method,
        [string]$Uri,
        [object]$Body
    )

    if ($DryRun.IsPresent -and -not $Apply.IsPresent) {
        Write-Host "[DryRun] $Method $Uri" -ForegroundColor Yellow
        if ($null -ne $Body) {
            Write-Host ($Body | ConvertTo-Json -Depth 10)
        }
        return $null
    }

    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $headers
    }

    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $headers -Body ($Body | ConvertTo-Json -Depth 10)
}

function Test-Health {
    param(
        [string]$Url
    )

    try {
        $resp = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5
        return $resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300
    }
    catch {
        return $false
    }
}

function Get-RecordName {
    param(
        [string]$RecordName,
        [string]$Domain
    )

    if ($RecordName -eq "@") {
        return $Domain
    }
    if ($RecordName -like "*.$Domain") {
        return $RecordName
    }
    return "$RecordName.$Domain"
}

$listUri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/dns_records?per_page=500"
$existingResp = Invoke-CFJson -Method GET -Uri $listUri -Body $null
$existing = @()
if ($null -ne $existingResp) {
    $existing = @($existingResp.result)
}

$enabledRecords = @($policy.records | Where-Object { $_.enabled -eq $true })

Write-Host "Policy domain: $($policy.domain)" -ForegroundColor Cyan
Write-Host "Enabled records: $($enabledRecords.Count)" -ForegroundColor Cyan

foreach ($rec in $enabledRecords) {
    $fqdn = Get-RecordName -RecordName $rec.name -Domain $policy.domain
    $isHealthy = Test-Health -Url $rec.health_url
    $shouldEnable = $true

    if ($DisableUnhealthy.IsPresent -and -not $isHealthy) {
        $shouldEnable = $false
    }

    Write-Host "- [$($rec.id)] $fqdn -> $($rec.value) healthy=$isHealthy enabled=$shouldEnable" -ForegroundColor Gray

    $match = $existing | Where-Object {
        $_.type -eq $rec.type -and $_.name -eq $fqdn -and $_.content -eq $rec.value
    } | Select-Object -First 1

    $comment = "sovereign-id=$($rec.id);weight=$($rec.weight);region=$($rec.region)"

    if ($null -eq $match) {
        $createUri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/dns_records"
        $body = @{
            type    = $rec.type
            name    = $fqdn
            content = $rec.value
            ttl     = [int]$policy.ttl_seconds
            proxied = $Proxied.IsPresent
            comment = $comment
        }

        if ($shouldEnable) {
            Invoke-CFJson -Method POST -Uri $createUri -Body $body | Out-Null
        }
        else {
            Write-Host "  skipped create because unhealthy and -DisableUnhealthy active" -ForegroundColor DarkYellow
        }
    }
    else {
        $patchUri = "https://api.cloudflare.com/client/v4/zones/$ZoneId/dns_records/$($match.id)"
        $body = @{
            type    = $rec.type
            name    = $fqdn
            content = $rec.value
            ttl     = [int]$policy.ttl_seconds
            proxied = $Proxied.IsPresent
            comment = $comment
        }

        if ($shouldEnable) {
            Invoke-CFJson -Method PATCH -Uri $patchUri -Body $body | Out-Null
        }
        else {
            $disableBody = @{
                type    = $match.type
                name    = $match.name
                content = $match.content
                ttl     = $match.ttl
                proxied = $match.proxied
                comment = "$($match.comment);disabled-by=health"
            }
            Invoke-CFJson -Method PATCH -Uri $patchUri -Body $disableBody | Out-Null
        }
    }
}

Write-Host "Completed. Apply mode: $($Apply.IsPresent). DryRun mode: $($DryRun.IsPresent -and -not $Apply.IsPresent)." -ForegroundColor Green
