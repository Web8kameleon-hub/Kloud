# Zero-Downtime Deployment Guide - Sovereign Fabric Nodes

## Overview
Deploy Kloud's 4 Sovereign Fabric Nodes (#1-4) with:
- ✅ **Zero downtime** - fluid membership recovery
- ✅ **Live health tracking** - TIDE-aware NDB scoring
- ✅ **Scalability** - unlimited nodes via configuration
- ✅ **Backward compatible** - existing services unchanged

## Pre-Deployment Checklist

```bash
# 1. Verify Python environment
python --version  # Must be 3.13.5+

# 2. Install dependencies
pip install -r requirements/nodedb.txt
pip install httpx aiofiles

# 3. Verify NodeDB is initialized
python -c "from nodendb_stigma import initialize_nodendb; import asyncio; asyncio.run(initialize_nodendb())"

# 4. Check docker-compose is available
docker --version
docker compose version
```

## Deployment Steps (Local)

### Step 1: Start NodeDB Control Plane
```bash
python nodedb_control_plane_api.py &
# Endpoint: http://localhost:8010
# Health check: curl http://localhost:8010/health
```

### Step 2: Bootstrap Control Plane
```bash
curl -X POST http://localhost:8010/api/v1/control-plane/bootstrap
```

Expected response:
```json
{
  "status": "bootstrapped",
  "available_count": 9,
  "registered_services": ["api", "ocean-core", "asi-trinity", "jona-sandbox", "clx-i", "ai-global", "aviation", "sovereign-node-1", "sovereign-node-2", "sovereign-node-3", "sovereign-node-4"]
}
```

### Step 3: Start Health Sync Loop
```bash
curl -X POST http://localhost:8010/api/v1/control-plane/sync/loop/start?interval_seconds=5
```

Expected response:
```json
{
  "status": "started",
  "interval_seconds": 5,
  "cycles": 0
}
```

### Step 4: Verify All Nodes
```bash
curl http://localhost:8010/api/v1/control-plane/scan-print?output=text
```

Expected output (compact format):
```
node-xxx | Sovereign Fabric Node #1 | active | excellent | 0.95
node-yyy | Sovereign Fabric Node #2 | active | good | 0.82
node-zzz | Sovereign Fabric Node #3 | active | good | 0.79
node-aaa | Sovereign Fabric Node #4 | active | fair | 0.68
```

## Deployment Steps (CI/CD)

### GitHub Actions
The workflow file `.github/workflows/deploy-sovereign-nodes-zero-downtime.yml` handles:
- Parallel deployment of nodes #1-4
- Health checks for each node
- Fabric coherence verification
- Snapshot persistence
- Membership registry validation

### Trigger Deployment
```bash
# Push to master
git push origin master

# Or manually trigger
gh workflow run deploy-sovereign-nodes-zero-downtime.yml
```

## Zero-Downtime Strategy

### Fluid Membership Protocol
1. **Join Phase** - New nodes register without stopping existing ones
2. **Sync Phase** - Health and state sync in real-time
3. **Active Phase** - Nodes integrate into topology gradually
4. **Recovery Phase** - Soft isolation and recovery on degradation

### Traffic Routing
```
Client Requests
    │
    ├─→ API (existing) ✅ unchanged
    ├─→ Ocean Core (existing) ✅ unchanged  
    ├─→ ASI Trinity (existing) ✅ unchanged
    │
    └─→ Sovereign Fabric (NEW)
         ├─ Node #1 (fsn1, 50km radius)
         ├─ Node #2 (fsn1, 75km radius)
         ├─ Node #3 (nbg1, 100km radius)
         └─ Node #4 (nbg1, 120km radius)
```

### Monitoring Dashboard
Access real-time metrics:
```bash
# Get JSON format
curl http://localhost:8010/api/v1/control-plane/scan-print

# Get readable text
curl http://localhost:8010/api/v1/control-plane/scan-print?output=text

# Watch with watch command
watch -n 5 'curl -s http://localhost:8010/api/v1/control-plane/scan-print | jq .'
```

## Rollback Strategy (if needed)

### Soft Rollback (disable new nodes)
```bash
# Edit SOVEREIGN_FABRIC_NODES in nodendb_kloud_integration.py
# Set "active": false for any node to disable it

# Then restart control plane
pkill -f "nodedb_control_plane_api"
python nodedb_control_plane_api.py &
```

### Hard Rollback (previous commit)
```bash
git revert HEAD
git push origin master
```

## Monitoring & Metrics

### Key Metrics per Node
- **TIDE**: Low (🟢) / Normal (🟡) / High (🔴) / Critical (⚫)
- **NDB Score**: 0.0-1.0 (quality metric)
- **Security Posture**: Stable / Degraded / Recovering
- **Latency**: ms response time
- **Bandwidth**: kbps utilization
- **CRDT Cardinality**: local state keys
- **Events Tracked**: security events count
- **Region**: fsn1 (Falkenstein) / nbg1 (Nuremberg)
- **Radius**: coverage radius in km

### Health Check Endpoint for Each Node
```bash
curl http://localhost:9001/status  # Node #1
curl http://localhost:9002/status  # Node #2
curl http://localhost:9003/status  # Node #3
curl http://localhost:9004/status  # Node #4
```

## Governance & Safety Gates

Before promoting scaled nodes to production:

1. **Quality Gate** ≥ 0.75
2. **Sync Loop Freshness** ≤ 2x interval
3. **Recovery Queue** not saturated
4. **Critical Node Ratio** ≤ 15%

See `docs/TECHNOLOGY_FIRST_RUNTIME_POLICY.md` for detailed safety rules.

## Performance Baselines

Expected response times (localhost):
- Cold start: 1-2s per node
- Health sync: 100-300ms per cycle
- Full topology scan: 200-500ms

With 4 nodes running:
- Total sync cycle: ~500ms
- Throughput: 1000+ requests/sec

## Troubleshooting

### Node not responding
```bash
# Check health
curl -v http://localhost:900<N>/status

# Check logs
docker logs kloud-sovereign-node-<N>

# Restart node
docker restart kloud-sovereign-node-<N>
```

### NodeDB sync loop stuck
```bash
# Check loop status
curl http://localhost:8010/api/v1/control-plane/sync-loop/status

# Restart loop
curl -X POST http://localhost:8010/api/v1/control-plane/sync-loop/stop
sleep 2
curl -X POST http://localhost:8010/api/v1/control-plane/sync-loop/start
```

### Add a 5th Node
Edit `SOVEREIGN_FABRIC_NODES` in `nodendb_kloud_integration.py`:
```python
5: {
    "name": "Expansion Node #5",
    "port": 9005,
    "host": "localhost",
    "scheme": "http",
    "region": "nbg1",
    "radius_km": 150,
    "description": "Fifth sovereign node",
    "active": True,
},
```

Then restart control plane.

## Support

- Control Plane API docs: `http://localhost:8010/docs`
- Architecture: `docs/KLOUD_NATIVE_RUNTIME_FILE_MAP.md`
- Recovery protocol: `docs/NODENDB_FLUID_MEMBERSHIP_RECOVERY_PROTOCOL.md`
- Safety policy: `docs/TECHNOLOGY_FIRST_RUNTIME_POLICY.md`
