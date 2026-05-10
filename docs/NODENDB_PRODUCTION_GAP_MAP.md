# NodeDB Hybrid Kameleon Production Gap Map

## Scope

This map defines the concrete production gaps and the required control-plane endpoints and data structures for a fluid, non-aggressive transition from pixel-bits-giga to wwwmmm-ndb-stigma-tide-nanogrid-cxl-cxl.i.

## Runtime Priority Policy (Mandatory)

- First mode must always be native technology mode:
  - wwwmmm
  - ndb
  - stigma
  - nodesndb
  - fluid resonance
  - metric-tide
- Hybrid old modus is fallback-only and must never be default.
- Fallback is allowed only when quality gates fail across repeated cycles.
- Return to native mode must be staged and evidence-based.

## Gap 1: Unified Control Plane

Current state:

- Runtime health checks and node registration exist.
- Nanogrid telemetry exists.
- No single API surface unifying both.

Required endpoints:

- `POST /api/v1/control-plane/bootstrap`
- `POST /api/v1/control-plane/sync`
- `GET /api/v1/control-plane/nodes`
- `GET /api/v1/control-plane/nodes/{node_id}`
- `GET /api/v1/control-plane/nanogrid/status`
- `GET /api/v1/control-plane/topology`

Required data structures:

- `ControlPlaneSnapshot`
- `NodeRuntimeView`
- `NanogridResonantView`

## Gap 2: Automatic State Sync

Current state:

- Health checks are available.
- NodeDB state transitions are manual unless explicitly called.

Required behavior:

- Map `health.status` to `StigmaState`.
- Map `quality_score` to `NDBQuality`.
- Persist updates continuously.

Required structures:

- `HealthSyncResult`
- `NodeStateTransitionLog`

## Gap 3: Lightweight Infinite Memory

Current state:

- Node state was in-memory only.

Required behavior:

- Persist NodeDB nodes and states to snapshot JSON.
- Restore snapshot on initialization.

Required artifacts:

- `output/nodedb/nodedb_snapshot.json`

## Gap 4: Membership Control

Current state:

- Peers are mostly config-driven.

Required endpoints:

- `GET /api/v1/control-plane/membership`
- `POST /api/v1/control-plane/membership/join`
- `POST /api/v1/control-plane/membership/leave`

Required structures:

- `MembershipRecord`
- `MembershipRegistry`

Persistence artifact:

- `output/nodedb/membership_registry.json`

## Gap 5: Recovery Orchestration

Current state:

- Recovery state exists, but orchestration needs explicit control-plane API.

Required endpoints:

- `POST /api/v1/control-plane/recovery/trigger`
- `GET /api/v1/control-plane/recovery/{node_id}`

Required structures:

- `RecoveryPlan`
- `RecoveryStepStatus`

## Gap 6: Fabric Governance

Current state:

- Telemetry and chain integrity exist.

Required behavior:

- Expose topology and fabric profile from one endpoint.
- Keep transition smooth with controlled, staged reintegration.

Required structures:

- `FabricTopology`
- `TransportTags`: lorawan, mesh, any-wave, cxl, cxl.i

## Transition Rules (Non-Aggressive)

- Never hard cut traffic from legacy state to fluid state.
- Run gradual sync cycles.
- Trigger recovery in soft isolate mode first.
- Reinstate node only after successful probe and chain resync.
