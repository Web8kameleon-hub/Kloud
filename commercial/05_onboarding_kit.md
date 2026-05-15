# Kloud Sovereign Fabric Suite
## Client Onboarding Kit
### Version 1.0 · May 2026

---

Welcome to **Kloud Sovereign Fabric**.  
This onboarding kit guides your team from zero to a fully operational sovereign node in 30 minutes or less.

---

## SECTION 1 — OVERVIEW

### What you are deploying

A **Kloud Sovereign Node** is an autonomous runtime that:
- Stores state persistently using CRDT (Conflict-free Replicated Data Types)
- Monitors all operations via STIGMA behavioral telemetry
- Tracks cognitive deviation via NDB (Node Deviation Baseline) scoring
- Measures environmental pressure via TIDE (fabric tension)
- Exposes a real-time **Control Surface** for operational visibility

Your node runs entirely on **your infrastructure**. Kloud does not access your data.

---

### The Control Surface

Once deployed, you access your node at:

```
http://[YOUR_HOST]:[PORT]/control
```

You will see:
- TIDE status (Low / Medium / High)
- NDB score (deviation from baseline)
- STIGMA security trace (L1/L2/L3)
- Latency, bandwidth, node load
- CRDT state key cardinality
- Full operations event log

---

## SECTION 2 — PRE-DEPLOYMENT CHECKLIST

Before deploying, confirm the following:

### Infrastructure Requirements

| Requirement | Minimum                   | Recommended      |
| ----------- | ------------------------- | ---------------- |
| CPU         | 2 vCPU                    | 4+ vCPU          |
| RAM         | 2 GB                      | 8 GB             |
| Disk        | 20 GB SSD                 | 100 GB SSD       |
| OS          | Ubuntu 22.04+ / Debian 12 | Ubuntu 22.04 LTS |
| Network     | 100 Mbps                  | 1 Gbps           |
| Open Ports  | 80, 443, [NODE_PORT]      | –                |
| Docker      | 24+                       | Latest stable    |
| Python      | 3.13+                     | 3.13.5           |

### Access Requirements
- [ ] SSH access to target server
- [ ] Docker + Docker Compose installed
- [ ] Your Kloud API key (from welcome email)
- [ ] Your Kloud Node ID (from welcome email)
- [ ] DNS record or IP for accessing the node

---

## SECTION 3 — DEPLOYMENT (STEP BY STEP)

### Step 1 — Receive Your Credentials

After signing up, you receive an email containing:

```
Node ID:        NODE-XXXX-XXXX
API Key:        kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
Node Secret:    kloud_ns_XXXXXXXXXXXXXXXX
Control Panel:  https://control.kloud.io/node/NODE-XXXX
```

Keep these secure. Never commit them to version control.

---

### Step 2 — Clone & Configure

```bash
# On your server
git clone https://github.com/Web8kameleon-hub/Kloud.git kloud-node
cd kloud-node

# Copy the example env file
cp .env.fabric.local.example .env.fabric.local

# Edit your configuration
nano .env.fabric.local
```

**Minimum required configuration:**

```env
# Node Identity
KLOUD_NODE_ID=NODE-XXXX-XXXX
KLOUD_API_KEY=kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
KLOUD_NODE_SECRET=kloud_ns_XXXXXXXXXXXXXXXX

# Node Settings
KLOUD_NODE_PORT=8080
KLOUD_CONTROL_SURFACE_PORT=9090
KLOUD_ENVIRONMENT=production

# NDB / STIGMA Settings
NDB_THRESHOLD=0.65
STIGMA_DEFAULT_LEVEL=2
TIDE_CHECK_INTERVAL=30

# CRDT Settings
CRDT_PERSISTENCE=true
CRDT_STORAGE_PATH=/data/crdt

# Security
KLOUD_TLS_ENABLED=true
KLOUD_CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

---

### Step 3 — Start the Node

```bash
# Start the sovereign node
docker-compose -f docker-compose.clx.fabric.yml up -d

# Verify containers are running
docker ps | grep kloud

# Check node health
curl http://localhost:8080/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "node_id": "NODE-XXXX-XXXX",
  "ndb_score": 0.041,
  "stigma_state": "STABLE",
  "crdt_keys": 0,
  "tide": "Low",
  "uptime_ms": 1234
}
```

---

### Step 4 — Verify the Control Surface

Open your browser:

```
http://[YOUR_HOST]:9090/control
```

You should see:
- ✅ Node Identity displayed
- ✅ NDB Score (initially ~0.038–0.045)
- ✅ STIGMA State: STABLE
- ✅ TIDE: Low
- ✅ 0 operations events (fresh node)

---

### Step 5 — Submit Your First Write

```bash
# Test the /submit endpoint
curl -X POST http://localhost:8080/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX" \
  -d '{"event": "write-1", "value": 101, "source": "onboarding-test"}'
```

**Expected response:**
```json
{
  "outcome": "accepted",
  "stigma": 2,
  "ndb_score": 0.038,
  "crdt_key": "event:write-1:1234567890",
  "timestamp_ms": 1234567890000
}
```

**What just happened:**
- Your write was accepted and classified at STIGMA L2
- A CRDT entry was created with causal ordering
- The NDB score confirmed no deviation
- The event is now visible in the Control Surface

---

### Step 6 — Verify the CRDT State

```bash
curl http://localhost:8080/status \
  -H "Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX"
```

**Expected response:**
```json
{
  "node_id": "NODE-XXXX-XXXX",
  "crdt_keys": 1,
  "ndb_score": 0.038,
  "stigma_state": "STABLE",
  "tide": "Low",
  "last_event_ms": 1234567890000
}
```

---

## SECTION 4 — UNDERSTANDING YOUR METRICS

### NDB Score — Node Deviation Baseline

| Score Range | Meaning                           | Action Required     |
| ----------- | --------------------------------- | ------------------- |
| 0.00–0.30   | Excellent — no drift              | None                |
| 0.30–0.50   | Good — minor variation            | Monitor             |
| 0.50–0.65   | Caution — approaching threshold   | Review workload     |
| 0.65–1.00   | Alert — deviation above threshold | Investigate         |
| > 1.00      | Critical — anomalous execution    | Immediate attention |

**Your live reading: 0.041 — far below threshold. Excellent.**

---

### STIGMA Classification

| Level | Name     | Meaning                                 | Example Operations       |
| ----- | -------- | --------------------------------------- | ------------------------ |
| L1    | Minimal  | Very low-friction, read-only, trivial   | Health checks, pings     |
| L2    | Standard | Normal operational events               | Reads, standard writes   |
| L3    | Compact  | Elevated, compressed, anomaly candidate | Unusual patterns, bursts |

All your current events are L2 — this is the expected steady state.

---

### TIDE — Fabric Tension

| Level  | Meaning                     | Action        |
| ------ | --------------------------- | ------------- |
| Low    | No environmental pressure   | None          |
| Medium | Peer activity or load spike | Monitor       |
| High   | Significant instability     | Review fabric |

---

### CRDT State Keys

Each write accepted by the fabric creates a CRDT key:
```
event:[EVENT_TYPE]:[TIMESTAMP_MS]
```

These keys are:
- Causally ordered
- Conflict-free (safe to replicate)
- Base64-encoded payload
- Audit-ready (contain source, timestamp_utc, value)

---

## SECTION 5 — CONNECTING TO THE CONTROL SURFACE API

All Control Surface data is accessible via API:

```bash
# Get all operations events
curl http://localhost:8080/events \
  -H "Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX"

# Get fabric metrics
curl http://localhost:8080/metrics \
  -H "Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX"

# Get CRDT local state
curl http://localhost:8080/crdt/state \
  -H "Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX"

# Export events as CSV
curl http://localhost:8080/events/export?format=csv \
  -H "Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX" \
  -o events_export.csv
```

---

## SECTION 6 — TROUBLESHOOTING

### Node not starting

```bash
# Check Docker logs
docker logs kloud-fabric-node --tail 50

# Common issues:
# - Port already in use: change KLOUD_NODE_PORT in .env
# - Missing env vars: double-check .env.fabric.local
# - Permission errors: ensure data/ directory is writable
```

---

### NDB score suddenly high

Possible causes:
1. Unusual traffic pattern — check `/events` log
2. Misconfigured `NDB_THRESHOLD` — review .env
3. Resource pressure on server — check CPU/RAM

```bash
# Check current NDB and events
curl http://localhost:8080/status
curl http://localhost:8080/events?limit=20
```

---

### STIGMA showing L3 events

L3 events indicate something unusual in the execution pattern:

1. Check the operations event log in the Control Surface
2. Look for burst patterns in `/submit` calls
3. Review the `ndb_score` trend over recent events

L3 events do not automatically mean an attack — they indicate elevated attention.

---

### /submit returning errors

```bash
# Check auth
curl -v http://localhost:8080/submit \
  -H "Authorization: Bearer YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"event":"test","value":1,"source":"debug"}'

# Common errors:
# 401: API key incorrect or missing
# 422: Payload missing required fields (event, value, source)
# 503: Node fabric not initialized — wait 30s and retry
```

---

## SECTION 7 — PRODUCTION HARDENING CHECKLIST

Before going live, complete:

- [ ] TLS enabled (`KLOUD_TLS_ENABLED=true`)
- [ ] API key rotated from default
- [ ] CORS restricted to your domains only
- [ ] Firewall: only expose required ports
- [ ] CRDT storage path on persistent volume
- [ ] Monitoring alerts configured (Grafana/Prometheus)
- [ ] Log retention configured
- [ ] Backup for CRDT state data
- [ ] NDB alert threshold reviewed for your workload
- [ ] Contact email set for security alerts

---

## SECTION 8 — SUPPORT & ESCALATION

| Issue Type         | Contact             | Response Time (Pro) |
| ------------------ | ------------------- | ------------------- |
| Deployment help    | support@kloud.io    | 12h                 |
| Security incident  | security@kloud.io   | 2h                  |
| Billing            | billing@kloud.io    | 24h                 |
| Enterprise support | enterprise@kloud.io | Per SLA             |
| General questions  | hello@kloud.io      | 48h                 |

**For P1 Critical issues (node down):**  
Email security@kloud.io with subject line: `[P1] NODE-XXXX-XXXX DOWN`

---

## SECTION 9 — NEXT STEPS AFTER ONBOARDING

Once your node is running:

### Week 1
- [ ] Submit 10+ test writes to build NDB baseline
- [ ] Review STIGMA event classifications
- [ ] Export first CSV event report
- [ ] Share Control Surface access with your team

### Month 1
- [ ] Add a second peer node (Pro/Enterprise)
- [ ] Set up Grafana dashboard for long-term observability
- [ ] Integrate `/submit` endpoint with your application
- [ ] Review NDB drift patterns under real workload

### Month 3
- [ ] Evaluate CRDT replication across peers
- [ ] Configure STIGMA alerts for L3 events
- [ ] Run a load test (see stress testing guide)

---

*Document version: 1.0 · May 2026 · Kloud Sovereign Fabric*  
*For onboarding support: support@kloud.io*  
*© 2026 Kloud · All rights reserved*
