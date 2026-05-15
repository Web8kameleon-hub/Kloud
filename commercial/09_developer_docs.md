# Kloud Sovereign Fabric Suite
## Developer Reference Documentation
### API Reference v1.0 · May 2026

---

## INTRODUCTION

The **Kloud Sovereign Fabric API** exposes a RESTful interface for interacting with your sovereign node. All endpoints accept and return JSON. All requests require authentication via Bearer token.

**Base URL:**
```
https://[YOUR_NODE_HOST]:[PORT]
```

**Authentication:**
```http
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
```

All API keys start with `kloud_sk_live_` for production and `kloud_sk_test_` for test environments.

---

## CORE CONCEPTS

### The Sovereign Node
A Kloud node is a persistent runtime that:
- Accepts and classifies operations via STIGMA
- Commits mutations to a CRDT state store
- Tracks execution deviation via NDB
- Exposes all telemetry in real time

### CRDT State
All accepted writes are committed as CRDT (Conflict-free Replicated Data Type) entries.
Each entry has a unique key: `event:[EVENT_TYPE]:[TIMESTAMP_MS]`

Keys are:
- Causally ordered (later writes never overwrite earlier ones incorrectly)
- Base64-encoded JSON payloads
- Audit-ready (contain event, value, source, timestamp_utc)

### NDB Score
The **Node Deviation Baseline** score measures how far current execution patterns deviate from expected behavior. Range: `0.000` (perfect) → `∞` (anomalous). Threshold default: `0.65`.

### STIGMA Classification
Every operation is classified:
- **L1 Minimal** — trivial, read-only, zero friction
- **L2 Standard** — normal operational events (expected steady state)
- **L3 Compact** — elevated, compressed, requires attention

### Cognitive Telemetry Mini-Glossary

| Proprietary Term | Enterprise Alias                 | Technical Meaning                                    |
| ---------------- | -------------------------------- | ---------------------------------------------------- |
| STIGMA           | Behavioral Trace Index (BTI)     | Behavioral fingerprint attached to each operation    |
| NDB              | Deviation Amplitude Score (DAS)  | Baseline-relative drift score for operation behavior |
| Rezonance        | Propagation Field Dynamics (PFD) | Node-to-node spread pattern of behavioral deviation  |
| TIDE             | Fabric Tension Monitor           | Stability pressure indicator for mesh state          |

Usage convention in API docs:
- First mention: proprietary + alias, e.g. `STIGMA (BTI)`
- Later references: alias is acceptable when context is already established

---

## ENDPOINTS

---

### `GET /health`

Check node health and readiness.

**Authentication:** Not required.

**Request:**
```http
GET /health
```

**Response 200:**
```json
{
  "status": "healthy",
  "node_id": "NODE-0001",
  "ndb_score": 0.041,
  "stigma_state": "STABLE",
  "crdt_keys": 2,
  "tide": "Low",
  "uptime_ms": 416531434,
  "version": "1.0.0"
}
```

**Response fields:**

| Field          | Type    | Description                            |
| -------------- | ------- | -------------------------------------- |
| `status`       | string  | `healthy` or `degraded` or `offline`   |
| `node_id`      | string  | Unique node identifier                 |
| `ndb_score`    | float   | Current NDB deviation score (0.000+)   |
| `stigma_state` | string  | `STABLE`, `ELEVATED`, `ANOMALY`        |
| `crdt_keys`    | integer | Number of committed CRDT state entries |
| `tide`         | string  | `Low`, `Medium`, `High`                |
| `uptime_ms`    | integer | Node uptime in milliseconds            |
| `version`      | string  | Fabric software version                |

---

### `GET /status`

Get detailed node status and fabric metrics.

**Authentication:** Required.

**Request:**
```http
GET /status
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
```

**Response 200:**
```json
{
  "node_id": "NODE-0001",
  "generated_at_ms": 1778861353434,
  "ndb": {
    "score": 0.041,
    "threshold": 0.65,
    "delta": -0.609,
    "state": "STABLE"
  },
  "stigma": {
    "state": "STABLE",
    "total_events": 6,
    "breakdown": {
      "L1": 0,
      "L2": 6,
      "L3": 0
    }
  },
  "tide": "Low",
  "performance": {
    "latency_ms": 16,
    "latency_pct_of_nominal": 6.4,
    "bandwidth_kbps": 0,
    "bandwidth_pct_of_baseline": 0.0,
    "node_load": 0.00,
    "node_utilization_pct": 0.0
  },
  "crdt": {
    "local_map_cardinality": 2
  },
  "peers": {
    "active_count": 1
  }
}
```

---

### `POST /submit`

Submit an operation to the fabric. The operation is classified by STIGMA, scored by NDB, and committed to the CRDT state store if accepted.

**Authentication:** Required.

**Request:**
```http
POST /submit
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
Content-Type: application/json

{
  "event": "write-1",
  "value": 101,
  "source": "my-application"
}
```

**Request body:**

| Field    | Type             | Required | Description                            |
| -------- | ---------------- | -------- | -------------------------------------- |
| `event`  | string           | Yes      | Event type identifier (e.g. `write-1`) |
| `value`  | number \| string | Yes      | Payload value                          |
| `source` | string           | Yes      | Source identifier (e.g. `my-app`)      |
| `meta`   | object           | No       | Optional metadata key-value pairs      |

**Response 200 — Accepted:**
```json
{
  "outcome": "accepted",
  "stigma": 2,
  "ndb_score": 0.038,
  "crdt_key": "event:write-1:1778444822715",
  "timestamp_ms": 1778444822715
}
```

**Response 429 — Rate Limited:**
```json
{
  "outcome": "rate_limited",
  "retry_after_ms": 1000
}
```

**Response 403 — STIGMA Blocked (L3 escalation):**
```json
{
  "outcome": "blocked",
  "stigma": 3,
  "reason": "anomalous_burst_pattern",
  "ndb_score": 0.78
}
```

**Response fields:**

| Field          | Type    | Description                           |
| -------------- | ------- | ------------------------------------- |
| `outcome`      | string  | `accepted`, `blocked`, `rate_limited` |
| `stigma`       | integer | STIGMA level assigned: 1, 2, or 3     |
| `ndb_score`    | float   | NDB score at time of request          |
| `crdt_key`     | string  | CRDT key where state was committed    |
| `timestamp_ms` | integer | Unix timestamp in milliseconds        |

---

### `GET /events`

Retrieve the operations event log.

**Authentication:** Required.

**Request:**
```http
GET /events?limit=25&stigma=2&endpoint=/submit&outcome=accepted
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
```

**Query parameters:**

| Parameter  | Type    | Default | Description                                |
| ---------- | ------- | ------- | ------------------------------------------ |
| `limit`    | integer | 25      | Max events to return (max: 1000)           |
| `offset`   | integer | 0       | Pagination offset                          |
| `stigma`   | integer | –       | Filter by STIGMA level (1, 2, or 3)        |
| `endpoint` | string  | –       | Filter by endpoint (e.g. `/submit`)        |
| `outcome`  | string  | –       | Filter by outcome (`accepted`, `ok`, etc.) |
| `since_ms` | integer | –       | Only events after this timestamp           |
| `until_ms` | integer | –       | Only events before this timestamp          |

**Response 200:**
```json
{
  "total": 6,
  "showing": 6,
  "events": [
    {
      "timestamp_ms": 1778444822715,
      "endpoint": "/submit",
      "action": "submit-op",
      "stigma": 2,
      "ndb_score": 0.038,
      "outcome": "accepted"
    },
    {
      "timestamp_ms": 1778444830108,
      "endpoint": "/status",
      "action": "read-status",
      "stigma": 2,
      "ndb_score": 0.038,
      "outcome": "ok"
    }
  ]
}
```

---

### `GET /events/export`

Export event log as CSV or JSON file.

**Authentication:** Required.

**Request:**
```http
GET /events/export?format=csv&since_ms=1778444000000
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
```

**Query parameters:**

| Parameter  | Type    | Default | Description                  |
| ---------- | ------- | ------- | ---------------------------- |
| `format`   | string  | `json`  | `csv` or `json`              |
| `since_ms` | integer | –       | Export events from this time |

**Response:** A downloadable file with the requested format.

---

### `GET /crdt/state`

Retrieve the local CRDT state map.

**Authentication:** Required.

**Request:**
```http
GET /crdt/state
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
```

**Response 200:**
```json
{
  "cardinality": 2,
  "entries": [
    {
      "key": "event:write-2:1778444825243",
      "payload_b64": "eyJldmVudCI6ICJ3cml0ZS0yIiwgInZhbHVlIjogMjAyLCAic291cmNlIjogImtsb3VkLWNvbnRyb2wtcGxhbmUiLCAidGltZXN0YW1wX3V0YyI6ICIyMDI2LTA1LTEwVDIwOjI3OjA1LjE4MDgyOCswMDowMCJ9",
      "decoded": {
        "event": "write-2",
        "value": 202,
        "source": "kloud-control-plane",
        "timestamp_utc": "2026-05-10T20:27:05.180828+00:00"
      }
    },
    {
      "key": "event:write-1:1778444822715",
      "payload_b64": "eyJldmVudCI6ICJ3cml0ZS0xIiwgInZhbHVlIjogMTAxLCAic291cmNlIjogImtsb3VkLWNvbnRyb2wtcGxhbmUiLCAidGltZXN0YW1wX3V0YyI6ICIyMDI2LTA1LTEwVDIwOjI3OjAyLjY1NDkwNyswMDowMCJ9",
      "decoded": {
        "event": "write-1",
        "value": 101,
        "source": "kloud-control-plane",
        "timestamp_utc": "2026-05-10T20:27:02.654907+00:00"
      }
    }
  ]
}
```

---

### `GET /metrics`

Prometheus-compatible metrics endpoint for scraping.

**Authentication:** Required.

**Request:**
```http
GET /metrics
Authorization: Bearer kloud_sk_live_XXXXXXXXXXXXXXXXXXXX
```

**Response 200 (text/plain, Prometheus format):**
```
# HELP kloud_ndb_score Current NDB deviation score
# TYPE kloud_ndb_score gauge
kloud_ndb_score 0.041

# HELP kloud_latency_ms Current fabric latency in milliseconds
# TYPE kloud_latency_ms gauge
kloud_latency_ms 16

# HELP kloud_crdt_keys Total CRDT state key cardinality
# TYPE kloud_crdt_keys gauge
kloud_crdt_keys 2

# HELP kloud_stigma_events_total Total STIGMA events by level
# TYPE kloud_stigma_events_total counter
kloud_stigma_events_total{level="L1"} 0
kloud_stigma_events_total{level="L2"} 6
kloud_stigma_events_total{level="L3"} 0

# HELP kloud_node_load_ratio Node utilization ratio
# TYPE kloud_node_load_ratio gauge
kloud_node_load_ratio 0.00
```

---

## SDK USAGE

### Python SDK

```python
from kloud_sdk import KloudClient

client = KloudClient(
    node_url="https://your-node.kloud.io",
    api_key="kloud_sk_live_XXXXXXXXXXXXXXXXXXXX"
)

# Check health
health = client.health()
print(f"NDB: {health['ndb_score']} · Status: {health['status']}")

# Submit an operation
result = client.submit(
    event="user-action",
    value={"action": "login", "user_id": 42},
    source="web-app"
)
print(f"Outcome: {result['outcome']} · STIGMA: {result['stigma']}")

# Read events
events = client.events(limit=10, stigma=2)
for event in events['events']:
    print(f"{event['timestamp_ms']} | {event['endpoint']} → {event['outcome']}")

# Read CRDT state
state = client.crdt_state()
print(f"State keys: {state['cardinality']}")
```

---

### TypeScript / Node.js SDK

```typescript
import { KloudClient } from '@kloud/sdk';

const client = new KloudClient({
  nodeUrl: 'https://your-node.kloud.io',
  apiKey: 'kloud_sk_live_XXXXXXXXXXXXXXXXXXXX'
});

// Check health
const health = await client.health();
console.log(`NDB: ${health.ndb_score} · Status: ${health.status}`);

// Submit an operation
const result = await client.submit({
  event: 'user-action',
  value: { action: 'purchase', orderId: 'ORD-001' },
  source: 'checkout-service'
});
console.log(`Outcome: ${result.outcome} · STIGMA L${result.stigma}`);

// Read events
const events = await client.events({ limit: 10, outcome: 'accepted' });
events.events.forEach(e => {
  console.log(`${e.timestamp_ms} | ${e.endpoint} → ${e.outcome}`);
});
```

---

## ERROR CODES

| HTTP Status | Code                | Description                                         |
| ----------- | ------------------- | --------------------------------------------------- |
| 200         | –                   | Success                                             |
| 400         | `invalid_payload`   | Malformed request body                              |
| 401         | `unauthorized`      | Missing or invalid API key                          |
| 403         | `stigma_blocked`    | Operation blocked by STIGMA engine                  |
| 422         | `missing_fields`    | Required fields absent (`event`, `value`, `source`) |
| 429         | `rate_limited`      | Too many requests; respect `retry_after_ms`         |
| 500         | `fabric_error`      | Internal fabric error                               |
| 503         | `node_initializing` | Node not yet ready; retry in 30s                    |

---

## RATE LIMITS

| Tier       | Requests/second | Requests/month |
| ---------- | --------------- | -------------- |
| Starter    | 10 req/s        | 1,000,000      |
| Pro        | 50 req/s        | 5,000,000      |
| Enterprise | Custom          | Unlimited      |

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 1000000
X-RateLimit-Remaining: 999994
X-RateLimit-Reset: 1780000000000
```

---

## CHANGELOG

| Version | Date     | Changes                                                                     |
| ------- | -------- | --------------------------------------------------------------------------- |
| v1.0.0  | May 2026 | Initial release — /health, /status, /submit, /events, /crdt/state, /metrics |

---

*Document version: 1.0 · May 2026 · Kloud Sovereign Fabric*  
*API Reference — for SDK support: support@kloud.io*  
*© 2026 Kloud · All rights reserved*
