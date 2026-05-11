# Kloud Local Commands for Remote Hosting (kloud.aiagi.io)

## 🌐 Remote API Endpoints

### Control Plane (Remote)
```bash
# Bootstrap remote control plane
curl -X POST https://kloud.aiagi.io/api/v1/control-plane/bootstrap

# Start sync loop remotely
curl -X POST https://kloud.aiagi.io/api/v1/control-plane/sync/loop/start?interval_seconds=5

# Check sync status
curl https://kloud.aiagi.io/api/v1/control-plane/sync-loop/status

# Scan all nodes (text format)
curl "https://kloud.aiagi.io/api/v1/control-plane/scan-print?output=text"

# List all nodes (JSON)
curl https://kloud.aiagi.io/api/v1/control-plane/nodes
```

### Sovereign Nodes Health (Remote)
```bash
# Node #1 status
curl https://kloud.aiagi.io/api/v1/nodes/sovereign-node-1/status

# Node #2 status  
curl https://kloud.aiagi.io/api/v1/nodes/sovereign-node-2/status

# Node #3 status
curl https://kloud.aiagi.io/api/v1/nodes/sovereign-node-3/status

# Node #4 status
curl https://kloud.aiagi.io/api/v1/nodes/sovereign-node-4/status
```

### Dashboard API
```bash
# Get dashboard data with filters
curl "https://kloud.aiagi.io/dashboard/api?endpoint=&outcome=&limit=25"

# Get events (adaptive resonance)
curl https://kloud.aiagi.io/api/v1/resonant/events

# Get metrics
curl https://kloud.aiagi.io/api/v1/resonant/metrics
```

## 📊 Local Shell Aliases (Add to PowerShell Profile)

```powershell
# Edit profile
code $PROFILE

# Add these aliases:
function kloud-status {
    curl https://kloud.aiagi.io/api/v1/control-plane/sync-loop/status | jq '.'
}

function kloud-nodes {
    curl https://kloud.aiagi.io/api/v1/control-plane/scan-print?output=text
}

function kloud-events {
    curl https://kloud.aiagi.io/api/v1/resonant/events | jq '.items[-10:]'
}

function kloud-metrics {
    curl https://kloud.aiagi.io/api/v1/resonant/metrics | jq '.'
}

function kloud-dashboard {
    Start-Process "https://kloud.aiagi.io/dashboard"
}
```

Then reload:
```bash
. $PROFILE
```

## 🔐 Authenticated Requests (with API Key)

```bash
# Export API key
$env:KLOUD_API_KEY = "your-api-key-here"

# Use in requests
curl -H "Authorization: Bearer $env:KLOUD_API_KEY" \
  https://kloud.aiagi.io/api/v1/control-plane/bootstrap

# Or with curl directly
curl -H "Authorization: Bearer your-api-key-here" \
  https://kloud.aiagi.io/api/v1/control-plane/nodes
```

## 🌊 Watch Remote TIDE & NDB in Real-Time

```powershell
# Install watch equivalent (local)
# Using a PowerShell loop
while ($true) {
    Clear-Host
    Write-Host "=== Kloud Sovereign Nodes Status ===" -ForegroundColor Cyan
    Write-Host "$(Get-Date)" -ForegroundColor Yellow
    
    curl -s "https://kloud.aiagi.io/api/v1/control-plane/scan-print?output=text"
    
    Write-Host ""
    Write-Host "Refreshing in 5s..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
}
```

Save as `watch-nodes.ps1` and run:
```bash
powershell -File watch-nodes.ps1
```

## 📡 SSH Tunnel to Remote (if Admin Access)

```bash
# Configure SSH in .ssh/config
Host kloud-prod
    HostName kloud.aiagi.io
    User deployment
    IdentityFile ~/.ssh/kloud-deploy-key
    LocalForward 8010 localhost:8010

# Connect
ssh kloud-prod

# Then locally access remote control plane:
curl http://localhost:8010/api/v1/control-plane/bootstrap
```

## 🚀 Deploy to Remote from Local

```bash
# Push changes to master
git push origin master

# Trigger remote deployment workflow
gh workflow run deploy-sovereign-nodes-zero-downtime.yml \
    --ref master

# Check workflow status
gh run list --workflow=deploy-sovereign-nodes-zero-downtime.yml
```

## 📥 Sync Remote Snapshot to Local

```bash
# Download NodeDB snapshot from remote
scp deployment@kloud.aiagi.io:/app/output/nodedb/nodedb_snapshot.json ./local_snapshot.json

# Download membership registry
scp deployment@kloud.aiagi.io:/app/output/nodedb/membership_registry.json ./local_membership.json
```

## 🔄 Local Development with Remote Integration

```bash
# Set remote endpoint for local dev
$env:KLOUD_REMOTE_API = "https://kloud.aiagi.io"
$env:KLOUD_LOCAL_API = "http://localhost:8010"

# Create local proxy (using example)
python -c "
import httpx
import asyncio

async def proxy():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://kloud.aiagi.io/api/v1/control-plane/nodes')
        print(response.json())

asyncio.run(proxy())
"
```

## 🧪 Test Remote Nodes with PayLoad

```bash
# Send event to remote resonant endpoint
curl -X POST https://kloud.aiagi.io/api/v1/resonant/events \
  -H "Content-Type: application/json" \
  -d '{
    "event": "local-test",
    "source": "local-cli",
    "node_id": "node-local-test",
    "tide": "normal",
    "ndb_score": 0.95,
    "value": 42
  }'

# Check if event was received
curl "https://kloud.aiagi.io/api/v1/resonant/events?limit=1"
```

## 🔍 Troubleshoot Remote Connection

```powershell
# Test connectivity
Test-NetConnection -ComputerName kloud.aiagi.io -Port 443

# Check DNS resolution
Resolve-DnsName kloud.aiagi.io

# Test HTTPS endpoint
curl -v https://kloud.aiagi.io/health

# Check remote logs (via SSH)
ssh deployment@kloud.aiagi.io 'tail -f /app/logs/nodedb-control-plane.log'
```

## 📈 Monitor Remote Production

```bash
# One-liner to check all nodes every 30s
for (;;) { 
    Write-Host "`n$(Get-Date)" -ForegroundColor Yellow
    curl -s "https://kloud.aiagi.io/api/v1/control-plane/scan-print?output=text" | 
        Select-String "node-|TIDE|NDB"
    Start-Sleep -Seconds 30
}
```

## 🏠 Local Hosting Alternative (Development)

```bash
# If you need to test locally before deploying to kloud.aiagi.io:

# 1. Start local control plane
python nodedb_control_plane_api.py

# 2. In another terminal, test locally
curl http://localhost:8010/api/v1/control-plane/bootstrap

# 3. Once verified, deploy to prod
git push origin master
# → GitHub Actions triggers → deploys to kloud.aiagi.io
```

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Check remote status | `curl https://kloud.aiagi.io/api/v1/control-plane/sync-loop/status` |
| View all nodes | `curl https://kloud.aiagi.io/api/v1/control-plane/scan-print?output=text` |
| Get events | `curl https://kloud.aiagi.io/api/v1/resonant/events` |
| View dashboard | Open https://kloud.aiagi.io/dashboard |
| Check Node #1 | `curl https://kloud.aiagi.io/api/v1/nodes/sovereign-node-1/status` |
| Deploy from local | `git push origin master` |
| Refresh loop | `curl -X POST https://kloud.aiagi.io/api/v1/control-plane/sync/loop/stop && curl -X POST https://kloud.aiagi.io/api/v1/control-plane/sync/loop/start` |
