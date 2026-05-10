# NodeDB-Fluid Reference Examples

This document gives a practical, ordered reference for how NodeDB-fluid adapts to packages and services without creating conflicts.

## 1. What NodeDB-Fluid Is

NodeDB-fluid is the adaptive runtime layer that:

- Introspects Python packages dynamically
- Learns service shape from live modules and health endpoints
- Stores node metadata and node state in snapshots
- Restores state automatically on startup
- Syncs live service health into NodeDB continuously

It is designed to fit mixed environments such as Windows, Ubuntu, Python, npm, and Rust-backed services, as long as a service can be described or observed through a module or endpoint.

## 2. Where The Core Logic Lives

The main runtime surfaces are:

- [nodendb_stigma.py](../nodendb_stigma.py)
- [nodendb_kloud_integration.py](../nodendb_kloud_integration.py)
- [nodedb_control_plane_api.py](../nodedb_control_plane_api.py)

The fluid adaptation itself is centered in:

- `StigmaPattern` for package introspection
- `NodeDBCore` for node registry and state management
- `load_snapshot()` for restore
- `register_service_with_nodedb()` for safe service registration

## 3. Reference Example Order

Use the following order when bringing a package or service into NodeDB-fluid.

### Step 1: Load the snapshot

NodeDB starts by restoring its previous state.

Example flow:

```python
from nodendb_stigma import initialize_nodendb

nodedb = await initialize_nodendb()
```

Expected outcome:

- Previously registered nodes are restored
- Node metadata is preserved
- Runtime state is resumed from snapshot JSON

### Step 2: Register the package or service

The service module is inspected dynamically.

Example flow:

```python
from nodendb_stigma import register_service_with_nodedb
import my_service_module

node_id = await register_service_with_nodedb(
    my_service_module,
    "My Service"
)
```

Expected outcome:

- Service type is detected automatically
- Public functions/classes are captured
- Health check patterns are discovered

### Step 3: Attach a live health check

If the package has a real endpoint, NodeDB should use that.

Example flow:

```python
async def check_my_service_health():
    response = await client.get("http://localhost:9000/health")
    return {
        "status": "healthy" if response.status_code == 200 else "error",
        "quality_score": 0.92,
    }

node_id = await register_service_with_nodedb(
    my_service_module,
    "My Service",
    health_check_fn=check_my_service_health,
)
```

Expected outcome:

- Real service health is attached to NodeDB
- NodeDB can map `healthy`, `degraded`, and `error` to node state
- The service remains platform-neutral

### Step 4: Update runtime state

NodeDB updates the node based on live signals.

Example flow:

```python
from nodendb_stigma import get_nodedb, StigmaState, NDBQuality

nodedb = get_nodedb()

await nodedb.update_node_state(
    node_id=node_id,
    state=StigmaState.ACTIVE,
    metrics={"latency_ms": 42, "quality_score": 0.95},
    ndb_quality=NDBQuality.EXCELLENT,
)
```

Expected outcome:

- State transitions are stored
- Quality deltas are tracked
- Recovery history stays intact

### Step 5: Synchronize real service health

The integration layer maps live health into NodeDB.

Example flow:

```python
from nodendb_kloud_integration import initialize_kloud_nodedb_real, monitor_real_services

context = await initialize_kloud_nodedb_real()
await monitor_real_services(context)
```

Expected outcome:

- API, Ocean, Trinity, and JONA health are captured
- NodeDB reflects real runtime behavior
- Conflicts are avoided because updates are centralized

## 4. How Conflicts Are Avoided

NodeDB-fluid avoids conflicts by following these rules:

- One global NodeDB instance per runtime
- Snapshot restore before live registration
- Async lock around registry mutations
- Dynamic introspection instead of rigid package-specific handlers
- Health sync is additive, not destructive
- Recovery is gradual, not hard-cut

## 5. Platform Examples

### Windows

- Use the same Python runtime and module introspection path
- Point health checks to `localhost`
- Keep MSVC/Rust build tools only for native Rust crates

### Ubuntu

- Use the same NodeDB snapshot and integration modules
- Use `localhost` or container DNS names for service checks

### Python packages

- Register imported modules directly
- Use health functions when real endpoints exist

### npm / TypeScript services

- Register through a Python wrapper module or a health adapter
- Let NodeDB introspect the wrapper and track the live endpoint

## 6. JONA Sandbox And Governance Path

For self-learning and self-writing, the runtime path is:

1. Proposal enters control plane
2. JONA sandbox health is read
3. Governance decision is computed
4. NodeDB stores the result in state/snapshot history

Relevant files:

- [nodendb_kloud_integration.py](../nodendb_kloud_integration.py)
- [nodedb_control_plane_api.py](../nodedb_control_plane_api.py)
- [protocol/src/governance_contracts.rs](../protocol/src/governance_contracts.rs)
- [protocol/src/self_writing_protocol.rs](../protocol/src/self_writing_protocol.rs)

## 7. Minimal Reference Example

```python
import my_service_module
from nodendb_stigma import initialize_nodendb, register_service_with_nodedb, get_nodedb, StigmaState, NDBQuality

async def bootstrap():
    nodedb = await initialize_nodendb()
    node_id = await register_service_with_nodedb(my_service_module, "My Service")
    await nodedb.update_node_state(
        node_id=node_id,
        state=StigmaState.ACTIVE,
        metrics={"quality_score": 0.93},
        ndb_quality=NDBQuality.EXCELLENT,
    )
```

## 8. Rule Of Thumb

If a service can be imported, inspected, or observed through a health endpoint, NodeDB-fluid can usually adapt to it. If it cannot, add a thin adapter or wrapper instead of hardcoding a new node type.

## 9. Examples By Package Type

### Python Package

Use direct module introspection plus a custom health callback.

```python
import my_python_package

node_id = await register_service_with_nodedb(
    my_python_package,
    "Python Package"
)
```

Best for:

- FastAPI apps
- Worker modules
- ML service packages
- Internal libraries with public functions or classes

### npm / TypeScript Service

Use a thin Python adapter that points NodeDB to the live HTTP endpoint.

```python
class TypeScriptServiceAdapter:
    __name__ = "typescript_service"
    __version__ = "1.0.0"

node_id = await register_service_with_nodedb(
    TypeScriptServiceAdapter(),
    "TypeScript Service",
    health_check_fn=check_ts_service_health,
)
```

Best for:

- Next.js apps
- Node APIs
- Frontend-backed control panels
- Services that are easiest to observe through `/health`

### Rust Service

Use the Rust service’s HTTP API or a Python-facing wrapper around it.

```python
class RustServiceAdapter:
    __name__ = "rust_service"
    __version__ = "0.1.0"

node_id = await register_service_with_nodedb(
    RustServiceAdapter(),
    "Rust Service",
    health_check_fn=check_rust_service_health,
)
```

Best for:

- Native fabric cores
- Gossip or protocol engines
- Low-level runtime services

### Dockerized Service

Use the container’s exposed endpoint and keep NodeDB on the host side.

```python
async def check_container_health():
    response = await client.get("http://localhost:8088/health")
    return {"status": "healthy" if response.status_code == 200 else "error"}
```

Best for:

- Mixed host/container deployments
- Local dev stacks
- Services with fixed ports

## 10. No-Conflict Checklist

Before adding a package or service, verify:

1. The package can be imported or wrapped cleanly.
2. The service has one stable health endpoint.
3. `initialize_nodendb()` runs before registration.
4. `register_service_with_nodedb()` is used instead of a custom node type.
5. State updates go through one NodeDB instance only.
6. Snapshot restore is preserved on startup.
7. JONA sandbox is used for self-learning or self-writing proposals.

## 11. Real Kloud Services Appendix

These are the current real services that fit the NodeDB-fluid pattern in this workspace.

### ALBA

- Current endpoint: `http://localhost:5555`
- Use it as a real service target with a health callback or wrapper module.
- Keep registration adapter-first so the service can remain unchanged.

### ALBI

- Current endpoint: `http://localhost:6680`
- Register it the same way as ALBA: importable wrapper if available, otherwise a thin HTTP adapter.
- Use NodeDB health sync to keep its state aligned with the live process.

### JONA

- Current endpoint: `http://localhost:7777`
- Treat JONA as the governance and sandbox observation target.
- Use it for self-learning and self-writing decisions, not as a hardcoded node subtype.

### Ocean

- Current endpoint: `http://localhost:8030`
- Attach its health and runtime metrics through the integration layer.
- Prefer the live `/health` or equivalent service endpoint if present.

### Practical Rule

If the service already exists in the runtime config, do not invent a new NodeDB shape for it. Wrap it, observe it, and let NodeDB-fluid absorb its state through snapshot restore and live sync.
