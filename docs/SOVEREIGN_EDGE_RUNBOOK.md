# Sovereign Edge Runbook

## Scope

This runbook is the practical execution guide for the sovereign edge model.

It covers:

- bootstrap and health checks
- PoP readiness checks
- DNS cutover checks
- failover drills
- rollback and recovery

## Preconditions

Before running this guide, confirm:

1. Docker stack is healthy on each target node.
2. Control plane endpoints respond.
3. TLS certificates are valid on edge ingress.
4. You have SSH access to each PoP host.

## Variables

Use these values in PowerShell before execution:

```powershell
$Domain = "kloud.aiagi.io"
$ControlPlane = "https://kloud.aiagi.io"
$Pop1 = "91.98.47.131"
$Pop2 = "62.238.21.125"
$Pop3 = "37.27.216.254"
```

## Step 1: Control Plane Baseline

Check control-plane health:

```powershell
Invoke-RestMethod -Method GET -Uri "$ControlPlane/health"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/sync-loop/status"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/scan-print?limit=50"
```

Expected:

- control plane responds with HTTP 200
- sync-loop running is true
- scan-print returns stable count and no duplicate stale entries

## Step 2: Bootstrap and Sync Loop

Run bootstrap:

```powershell
Invoke-RestMethod -Method POST -Uri "$ControlPlane/api/v1/control-plane/bootstrap"
```

Start or refresh loop:

```powershell
Invoke-RestMethod -Method POST -Uri "$ControlPlane/api/v1/control-plane/sync/loop/start?interval_seconds=5"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/sync-loop/status"
```

## Step 3: Edge PoP Endpoint Checks

Check each PoP runtime and bridge:

```powershell
ssh root@$Pop1 "curl -s http://127.0.0.1:9080/status"
ssh root@$Pop1 "curl -s http://127.0.0.1:9080/health"

ssh root@$Pop2 "curl -s http://127.0.0.1:9080/status"
ssh root@$Pop2 "curl -s http://127.0.0.1:9080/health"

ssh root@$Pop3 "curl -s http://127.0.0.1:9080/status"
ssh root@$Pop3 "curl -s http://127.0.0.1:9080/health"
```

If bridge is used:

```powershell
ssh root@$Pop1 "curl -s http://127.0.0.1:8889/status"
ssh root@$Pop2 "curl -s http://127.0.0.1:8889/status"
ssh root@$Pop3 "curl -s http://127.0.0.1:8889/status"
```

## Step 4: Resonant Write Validation

Validate write acceptance through public control-plane path:

```powershell
$Body = @{ event = "runbook-write-test"; value = 101 } | ConvertTo-Json -Compress
Invoke-RestMethod -Method POST -Uri "$ControlPlane/api/v1/resonant/events/adaptive" -ContentType "application/json" -Body $Body
```

Check state on active runtime:

```powershell
ssh root@$Pop1 "curl -s http://127.0.0.1:9080/state"
```

Expected:

- submitted or accepted status
- state map contains at least one key

## Step 5: DNS and Routing Validation

Validate DNS answers:

```powershell
Resolve-DnsName $Domain
```

Apply DNS policy using Cloudflare integration (phased mode):

```powershell
.\scripts\apply-sovereign-dns-policy-cloudflare.ps1 -ZoneId <ZONE_ID> -ApiToken <CF_API_TOKEN> -DryRun
```

Run failover drill:

```powershell
.\scripts\test-sovereign-failover.ps1
```

Validate public edge health:

```powershell
Invoke-RestMethod -Method GET -Uri "https://$Domain/health"
Invoke-RestMethod -Method GET -Uri "https://$Domain/status"
```

## Step 6: Planned Failover Drill

Simulate PoP 1 outage:

```powershell
ssh root@$Pop1 "docker stop kloud-ai-global-9999"
```

Observe route behavior:

```powershell
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/scan-print?limit=50"
Invoke-RestMethod -Method GET -Uri "https://$Domain/status"
```

Recover PoP 1:

```powershell
ssh root@$Pop1 "docker start kloud-ai-global-9999"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/sync-loop/status"
```

## Step 7: Rollback Procedure

If instability is detected:

1. Route all traffic back to PoP 1 in DNS.
2. Stop writes on degraded PoPs.
3. Keep reads enabled only on healthy node(s).
4. Restart sync-loop.
5. Re-run bootstrap.

Commands:

```powershell
Invoke-RestMethod -Method POST -Uri "$ControlPlane/api/v1/control-plane/bootstrap"
Invoke-RestMethod -Method POST -Uri "$ControlPlane/api/v1/control-plane/sync/loop/start?interval_seconds=5"
```

## Step 8: Operational SLO Checks

Minimum thresholds:

- status availability >= 99.9%
- p95 edge latency <= 100 ms
- write rejection rate <= 1%
- chain integrity failures = 0
- replay rejections stable and explainable

Check metrics:

```powershell
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/resonant/metrics"
```

## Emergency Quick Commands

```powershell
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/sync-loop/status"
Invoke-RestMethod -Method POST -Uri "$ControlPlane/api/v1/control-plane/bootstrap"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/control-plane/scan-print?output=text"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/resonant/status"
Invoke-RestMethod -Method GET -Uri "$ControlPlane/api/v1/resonant/metrics"
```
