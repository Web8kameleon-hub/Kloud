# NodeDB Fluid Membership and Recovery Protocol

## Intent
Define a controllable, smooth protocol for hybrid-kameleon fabric operation across:
- wwwmmm
- ndb
- stigma
- tide
- nanogrid
- cxl
- cxl.i

## Membership Lifecycle
States:
- `joining`
- `active`
- `draining`
- `left`

### Join Flow
1. Node calls `POST /api/v1/control-plane/membership/join` with endpoint and transport tags.
2. Control plane records node as `active`.
3. Node is added to topology view.
4. Health sync cycles start updating its NodeDB state.

### Leave Flow
1. Operator or node calls `POST /api/v1/control-plane/membership/leave`.
2. Control plane marks node as `left` with reason.
3. Node remains in audit history but not in active topology.

## Recovery Lifecycle
States:
- `detected`
- `isolated-soft`
- `probing`
- `resyncing`
- `reintegrating`
- `active-restored`

### Trigger
- `POST /api/v1/control-plane/recovery/trigger`

### Steps
1. `isolate-node-soft`
2. `run-health-probe`
3. `resync-from-nanogrid-chain`
4. `restore-active-state-gradually`

## Sync Mapping Rules
Health status to stigma state:
- `healthy` -> `active`
- `degraded` -> `degraded`
- `error` -> `recovering`

Quality score to NDB quality:
- `>= 0.90` -> `excellent`
- `>= 0.75` -> `good`
- `>= 0.50` -> `fair`
- `>= 0.20` -> `poor`
- `< 0.20` -> `critical`

## Safety Rules
- Keep control loops short and deterministic.
- Persist every meaningful state transition.
- Allow gradual re-entry into active topology.
- Prefer soft isolation before hard eviction.
