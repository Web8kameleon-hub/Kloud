# Sovereign Edge Topology Mapped to Current Kloud Configuration

## Purpose

This document maps the 3-PoP sovereign architecture directly to the current Kloud deployment shape, ports, and runtime endpoints.

## Current Runtime Signals

Observed from active environment and existing docs:

- public domain path via https ingress
- control-plane endpoints under `/api/v1/control-plane/*`
- resonant endpoints under `/api/v1/resonant/*`
- runtime/bridge/gossip split already used in operations

## Logical Topology

### Control Plane

- domain: `kloud.aiagi.io`
- role: orchestration, bootstrap, sync-loop, scan-print
- key endpoints:
  - `GET /api/v1/control-plane/sync-loop/status`
  - `POST /api/v1/control-plane/bootstrap`
  - `GET /api/v1/control-plane/scan-print`

### Edge PoP Nodes

- PoP 1: primary edge
- PoP 2: standby edge
- PoP 3: recovery edge

Runtime conventions seen in current platform:

- bridge: `:8889`
- runtime: `:9080`
- gossip: `:9001` or node-specific gossip port
- public TLS ingress: `:443`

## Docker Service Mapping (Current Compose)

From current compose topology:

- `api` on `8000`
- `web` on `3000`
- `ai-global-9999` on `9999`
- `ocean-core` on `8030`
- `clx` on `11434`
- `clx-i` on `4444`
- `alba` on `5555`
- `albi` on `6680`
- `jona` on `7777`
- observability stack on `3001`, `8428`, `9090`, `3102`, `16686`

## Recommended Concrete Placement

### PoP 1 (Primary)

- ingress: nginx/envoy on 443
- runtime target: localhost:9080
- bridge target: localhost:8889
- control-plane proxy path to localhost:8091 where applicable
- default DNS target weight: high

### PoP 2 (Standby)

- same ingress contract as PoP 1
- same runtime and bridge ports
- DNS target weight: medium
- write routes enabled only when healthy

### PoP 3 (Recovery)

- same ingress contract
- DNS target weight: low
- receives traffic on failover or regional outage

## Route Contract

Public routes that must remain stable:

- `/health`
- `/status`
- `/api/v1/control-plane/*`
- `/api/v1/resonant/status`
- `/api/v1/resonant/events`
- `/api/v1/resonant/events/adaptive`

## Health and Promotion Signals

Use these as promotion signals per PoP:

- control-plane sync loop running
- resonant status returns healthy response
- metrics show stable `tide` and bounded `ndb_delta`
- state key growth possible via accepted writes

## Suggested DNS Model

For the sovereign path:

1. Move to independent authoritative DNS.
2. Create A/AAAA for PoP 1, PoP 2, PoP 3.
3. Use weighted or latency-based answer policy.
4. Keep low TTL during rollout phase.

Template:

- `docs/templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json`

## Failover Order

Default order:

1. PoP 1 primary
2. PoP 2 standby
3. PoP 3 recovery

If PoP 1 is degraded:

- remove from active answer set
- route reads and writes to PoP 2

If PoP 2 also degrades:

- route to PoP 3 and keep write controls strict

## Validation Commands (PowerShell)

```powershell
Invoke-RestMethod -Method GET -Uri "https://kloud.aiagi.io/health"
Invoke-RestMethod -Method GET -Uri "https://kloud.aiagi.io/status"
Invoke-RestMethod -Method GET -Uri "https://kloud.aiagi.io/api/v1/control-plane/sync-loop/status"
Invoke-RestMethod -Method GET -Uri "https://kloud.aiagi.io/api/v1/resonant/status"
Invoke-RestMethod -Method GET -Uri "https://kloud.aiagi.io/api/v1/resonant/metrics"
```

## Operations Note

This topology is intentionally compatible with existing Kloud endpoint contracts.

No client-facing schema break is required to move from single-edge to sovereign 3-PoP routing.
