# Kloud Native Runtime — Learning Path

**Audience:** Engineers, operators, and platform teams joining the Kloud ecosystem.  
**Goal:** Understand and operate the full native stack — WWWMMM → NDB → STIGMA → NodeDB → Fluid Resonance → Tide.  
**Format:** 4 phases — read, interpret, integrate, operate.

---

## Overview: What is the Native Runtime Stack?

The Kloud native runtime is a self-regulating fabric. Each layer has a specific role:

```
WWWMMM → NDB → STIGMA → NodeDB (Fluid) → Resonance → Tide
  │         │       │          │               │          │
gate     measure  trace     register       unify       gate
traffic  quality  memory    services       health      action
```

| Module                    | Full Name                    | What It Does                                                                                           |
| ------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------ |
| **WWWMMM**                | Wide-band Quality Gate       | Validates every response before promotion. If quality fails, traffic is blocked or re-routed.          |
| **NDB**                   | NanoDecibel Score            | Measures signal resonance quality as a numeric band (0.0–1.0). Tracks drift over time via `ndb_delta`. |
| **STIGMA**                | Behavioral Trace Index (BTI) | Persistent memory imprint of operational events. Used for audit, risk scoring, and incident recovery.  |
| **STIGMA Memory / Cloud** | Trace Storage Layer          | Long-lived preservation of STIGMA history. Enables state recovery without replay gaps.                 |
| **NodeDB**                | Node Repository              | Adaptive registry that discovers any service dynamically. No rigid per-service handlers.               |
| **NodeDB Fluid**          | Membership Recovery          | Graceful re-entry of failed nodes. Maintains fabric continuity under partial failure.                  |
| **Resonance / Rezonance** | Global Health Profile (PFD)  | Propagation Field Dynamics — a unified health index that aggregates NDB, Tide, and STIGMA signals.     |
| **Tide**                  | Operational Pressure Band    | Three-level pressure system (Low / Normal / High) that governs gating and allowed actions.             |

---

## Phase 1 — Concepts (10 min read)

### 1.1 NDB — How to Think About It

NDB is not a log. NDB is a **resonance measurement** — like a signal-to-noise ratio for a service.

- `ndb_score` — current quality: `0.0` (dead) to `1.0` (perfect)
- `ndb_delta` — rate of change: positive = improving, negative = degrading
- `ndb_threshold` — minimum acceptable quality before Tide escalates

**Quality bands:**

| Value | NDBQuality  | Meaning                         |
| ----- | ----------- | ------------------------------- |
| 1.0   | `EXCELLENT` | Fully healthy, peak performance |
| 0.8   | `GOOD`      | Normal operation                |
| 0.6   | `FAIR`      | Acceptable, monitor closely     |
| 0.3   | `POOR`      | Degraded, recovery recommended  |
| 0.0   | `CRITICAL`  | Offline or unresponsive         |

### 1.2 STIGMA — How to Think About It

STIGMA is not a log line. STIGMA is a **persistent behavioral imprint**.

When a service changes state (crash, recovery, anomaly, high-load event), STIGMA records a trace that survives restarts. This trace is used to:
- Classify risk level (is this a pattern or a one-off?)
- Reconstruct history after failure
- Feed Resonance with context about past behavior

**StigmaState lifecycle:**

```
INITIALIZING → READY → ACTIVE → DEGRADED → RECOVERING → ACTIVE
                                          ↓
                                        OFFLINE (if recovery fails)
```

### 1.3 WWWMMM — The Gate

WWWMMM is the validation checkpoint. No response is promoted to users without passing this gate.

- In CI/CD: enforced as env var `WWWMMM_AUTORUN=true`
- At runtime: enforced on adapter traffic before promotion
- Verdict logged: `wwwmmm_verdict: "pass"` or `"bypassed"`
- Profile tag: `PRIMARY_RESONANT_PROFILE=wwwmmm-ndb-stigma-tide-rezonance-nanogrid`

If WWWMMM is bypassed, traffic can still flow — but it is treated as **unverified** and must not be promoted to 25%+ rollout.

### 1.4 Tide — Pressure Levels

Tide governs what actions are allowed based on system-wide pressure.

| Level    | Meaning           | Allowed Actions                 |
| -------- | ----------------- | ------------------------------- |
| `Low`    | System is healthy | All operations including writes |
| `Normal` | Nominal load      | Standard operations             |
| `High`   | Under pressure    | Read-only or gated writes       |

Tide is computed from: NDB scores across all nodes, recovery queue depth, sync loop freshness.

### 1.5 Resonance — The Unified Signal

Resonance (PFD — Propagation Field Dynamics) is the top-level health score. It aggregates:
- Average NDB quality across all nodes
- Active STIGMA trace severity
- Current Tide pressure
- NodeDB membership stability

Think of Resonance as the "vital sign" of the entire fabric. If Resonance drops, the stack shifts into hybrid fallback mode.

---

## Phase 2 — Reading Metrics

### 2.1 Reading a Node's Status

Every registered node exposes a state object. Learn to read it:

```python
{
  "node_id": "node-a1b2c3d4e5",
  "service_name": "FastAPI Backend",
  "service_type": "FastAPI",
  "stigma_state": "active",          # StigmaState — lifecycle position
  "ndb_quality": "good",             # NDBQuality — resonance band
  "ndb_delta": 0.05,                 # Positive = improving
  "tide_pressure": 0.6,              # 0.0 (calm) to 1.0 (max pressure)
  "last_heartbeat": "2026-05-15T...", # Freshness check
  "metrics": {
    "latency_ms": 15,
    "throughput_rps": 500
  }
}
```

**Quick diagnosis rules:**

| Observation                                        | What It Means                                         |
| -------------------------------------------------- | ----------------------------------------------------- |
| `ndb_quality: critical` + `stigma_state: degraded` | Node is failing, recovery should trigger              |
| `ndb_delta: -0.12` (negative and large)            | Quality dropping fast — watch closely                 |
| `tide_pressure: 0.9`                               | Fabric under heavy pressure — writes may be gated     |
| `stigma_state: recovering`                         | Automatic recovery in progress — do not force restart |
| `ndb_quality: excellent` + `tide_pressure: 0.1`    | Fabric is healthy and idle                            |

### 2.2 Reading a Resonance Status Response

From `/resonant/status` (Rust node API):

```json
{
  "state": "native",
  "tide": "Normal",
  "ndb_score": 0.84,
  "ndb_delta": 0.02,
  "ndb_threshold": 0.75,
  "stigma_level": "low",
  "high_risk": false,
  "event_count": 3,
  "trace_id": "trc-9f3a21",
  "trace_state": "stable"
}
```

**If `high_risk: true`** — a BTI (STIGMA) trace has been classified as a behavioral anomaly. Investigate `event_count` and `trace_id` before any deployment.

### 2.3 Reading WWWMMM Gate Output

```json
{
  "wwwmmm_gate_enabled": true,
  "wwwmmm_verdict": "pass"
}
```

- `verdict: "pass"` — response is clean, promotable
- `verdict: "bypassed"` — gate was skipped, traffic is unverified
- `gate_enabled: false` — gate is disabled entirely (never acceptable in production)

---

## Phase 3 — First Integration (Developers)

### 3.1 Register a New Service with NodeDB

```python
from nodendb_stigma import initialize_nodendb, register_service_with_nodedb

async def startup():
    nodedb = await initialize_nodendb()

    import my_service_module
    node = await register_service_with_nodedb(
        my_service_module,
        "My Service Name"
    )
    print(f"Registered: {node.node_id} | State: {node.stigma_state}")
```

NodeDB will automatically discover:
- Service type (FastAPI, Flask, Django, worker, etc.)
- Public endpoints and methods
- Health check patterns
- Environment requirements

### 3.2 Report NDB Quality from a Service

```python
from nodendb_stigma import get_nodedb, NDBQuality

async def report_health(node_id: str, quality: NDBQuality):
    nodedb = await get_nodedb()
    await nodedb.update_node_quality(node_id, quality, delta=0.05)
```

Call this from your health check loop, not just on failures. Continuous reporting keeps Resonance accurate.

### 3.3 Add STIGMA Trace on a Significant Event

```python
from nodendb_stigma import get_nodedb, StigmaState

async def on_anomaly_detected(node_id: str):
    nodedb = await get_nodedb()
    await nodedb.transition_node_state(
        node_id,
        StigmaState.DEGRADED,
        reason="anomaly_detected"
    )
    # STIGMA will record this trace automatically
```

Do not manually write to STIGMA storage — always transition state through NodeDB. This ensures trace integrity.

### 3.4 Check Tide Before a Write Operation

```python
from nodendb_stigma import get_nodedb

async def safe_write(node_id: str, data: dict):
    nodedb = await get_nodedb()
    node = await nodedb.get_node(node_id)

    if node.tide_pressure > 0.8:
        raise RuntimeError("Fabric under high pressure — write deferred")

    # proceed with write
    await write_to_storage(data)
```

---

## Phase 4 — Operating the Fabric (Operators)

### 4.1 Normal Startup Order

```
1. Bootstrap control-plane (9999/app.py)
2. Initialize NodeDB (nodendb_stigma.py)
3. Register all services
4. Start sync loop
5. Validate resonance metrics and tide stability
6. Enable WWWMMM gate
7. Begin traffic at 5% — verify wwwmmm_verdict: "pass"
8. Expand to 25% only after 3+ stable cycles
```

### 4.2 Health Gates — Native Mode Stays Active If:

| Gate                 | Threshold      |
| -------------------- | -------------- |
| Global quality score | >= 0.75        |
| Critical node ratio  | <= 0.15        |
| Sync loop freshness  | <= 2× interval |
| Recovery queue       | Not saturated  |

### 4.3 When to Switch to Hybrid Fallback

Switch to hybrid old modus when **any** of these persist across 3 consecutive cycles:

- Global quality score < 0.50
- Critical node ratio > 0.30
- Sync loop stalled > 3 intervals
- Same node recovery failure > 2 times

**Do not hard-stop native mode.** Shift traffic gradually. Keep collecting native metrics during fallback. Recovery orchestration stays active.

### 4.4 Return to Native Mode

Return only when **all** of these are true for **5 consecutive cycles**:

- Global quality score >= 0.80
- Critical node ratio <= 0.10
- Sync loop healthy and stable
- No active hard failures

### 4.5 Quick Diagnostic Commands

```bash
# Check resonance status
curl http://localhost:9999/resonant/status

# Check WWWMMM gate state
curl http://localhost:9999/health | jq '.wwwmmm_gate_enabled, .wwwmmm_verdict'

# Check all node states via control plane
curl http://localhost:<nodedb_port>/nodes | jq '.[].stigma_state'

# Check Tide pressure
curl http://localhost:9999/status | jq '.tide'
```

---

## Quick Reference Card

```
STACK ORDER:    WWWMMM → NDB → STIGMA → NodeDB → Resonance → Tide

NDB BANDS:      excellent(1.0) > good(0.8) > fair(0.6) > poor(0.3) > critical(0.0)

STIGMA STATES:  INITIALIZING → READY → ACTIVE → DEGRADED → RECOVERING → ACTIVE
                                                           ↘ OFFLINE

TIDE LEVELS:    Low (healthy) | Normal (nominal) | High (gated)

WWWMMM RULE:    Never promote to 25%+ without verdict: "pass"

FALLBACK RULE:  Shift gradually. Never hard-cut native mode.

RESONANCE API:  GET /resonant/status  →  ndb_score, tide, stigma_level, high_risk
```

---

## Further Reading

| Document                                      | Topic                                                    |
| --------------------------------------------- | -------------------------------------------------------- |
| `docs/RESONANT_CORE.md`                       | Canonical field definitions and rollout strategy         |
| `docs/NODENDB_STIGMA_GUIDE.md`                | Full NodeDB integration guide with code examples         |
| `docs/NODENDB_FLUID_REFERENCE_EXAMPLES.md`    | Reference patterns for fluid membership                  |
| `docs/TECHNOLOGY_FIRST_RUNTIME_POLICY.md`     | Native-first mandate, fallback triggers, return criteria |
| `docs/HYBRID_OLD_MODUS_FALLBACK_RUNBOOK.md`   | Step-by-step fallback and recovery runbook               |
| `docs/RESONANT_PHASE1_25PERCENT_CHECKLIST.md` | Checklist before expanding to 25% rollout                |
| `nodendb_stigma.py`                           | Source of truth for all enums, classes, and logic        |
