# NODENDB STIGMA PATTERN - Integration Guide

## Overview

**NodeDB Stigma Pattern** replaces rigid, hardcoded node definitions with a fluid, adaptive system that:

- **Auto-discovers** service structure through introspection
- **Adapts dynamically** to any package without code changes
- **Integrates NDB resonance quality** for node health signaling
- **Tracks Tide pressure** for system-wide resource management
- **Detects health patterns** automatically from code structure

Instead of separate node types (Flask nodes, FastAPI nodes, Worker nodes), NodeDB creates a single adaptive pattern that works with any service.

---

## Why NodeDB is a Stigma, Not a Script

### Traditional Script Approach (❌ Rigid)
```python
# Separate, hardcoded node types
class FlaskNodeHandler:
    def __init__(self, app):
        self.app = app
        self.port = 5000
        # Flask-specific logic

class FastAPINodeHandler:
    def __init__(self, app):
        self.app = app
        self.port = 8000
        # FastAPI-specific logic
```

**Problem:** Every new service type needs new Node class. Maintenance nightmare.

### Stigma Pattern Approach (✅ Adaptive)
```python
# Single pattern adapts to ANY service
stigma = StigmaPattern(service_module, "Backend API")
# Automatically discovers:
# - Service type (FastAPI, Flask, Django, etc.)
# - Capabilities (endpoints, methods)
# - Health checks
# - Requirements
```

**Benefit:** Same code handles all services. Stigma pattern learns, adapts, recovers.

---

## Key Concepts

### 1. **Stigma Pattern**
Dynamic introspection engine that examines any Python module and extracts:
- Service framework (FastAPI, Flask, Django, gRPC, etc.)
- Public methods and their signatures
- Class definitions and relationships
- Configuration requirements
- Environment variables
- Health check patterns

### 2. **NodeMetadata**
Extracted structural information about a service:
```python
NodeMetadata(
    node_id="node-a1b2c3d4e5",
    service_name="FastAPI Backend",
    service_type="FastAPI",
    package_name="api",
    capabilities=["endpoint:/health", "endpoint:/status", "function:generate_token"],
    health_checks=["health", "status", "ready"],
)
```

### 3. **NodeState**
Runtime state of a registered node:
```python
NodeState(
    stigma_state=StigmaState.ACTIVE,
    ndb_quality=NDBQuality.GOOD,        # Resonance quality signal
    ndb_delta=0.05,                      # Change in quality
    tide_pressure=0.6,                   # System-wide pressure
    last_heartbeat=datetime.utcnow(),
    metrics={"latency_ms": 15, "throughput_rps": 500}
)
```

### 4. **NodeDB Core**
Central repository with async-safe locking:
- Registers services dynamically
- Tracks all node states
- Simulates Tide pressure
- Triggers recovery workflows
- Queries node information

---

## Integration Steps

### Step 1: Initialize NodeDB

```python
# In your main application startup
from nodendb_stigma import initialize_nodendb, register_service_with_nodedb

async def setup():
    nodedb = await initialize_nodendb()
    print(f"✅ NodeDB initialized: {nodedb}")
```

### Step 2: Register Services

#### Option A: Generic Service Discovery
```python
from nodendb_stigma import register_service_with_nodedb

# Register any imported service module
import my_fastapi_app
import my_worker_service
import my_analytics_engine

node_api = await register_service_with_nodedb(
    my_fastapi_app,
    "FastAPI Backend"
)

node_worker = await register_service_with_nodedb(
    my_worker_service,
    "Celery Worker"
)

node_analytics = await register_service_with_nodedb(
    my_analytics_engine,
    "Analytics Engine"
)
```

#### Option B: With Custom Health Check
```python
async def check_api_health():
    """Custom health check for API"""
    try:
        response = await httpx.get("http://localhost:8000/health", timeout=2)
        return {
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

node_api = await register_service_with_nodedb(
    my_fastapi_app,
    "FastAPI Backend",
    health_check_fn=check_api_health
)
```

### Step 3: Report State Changes

```python
from nodendb_stigma import get_nodedb, StigmaState, NDBQuality

nodedb = get_nodedb()

# When service is ready
await nodedb.update_node_state(
    node_id="node-a1b2c3d4e5",
    state=StigmaState.READY,
    metrics={"startup_ms": 250, "config_loaded": True},
    ndb_quality=NDBQuality.GOOD
)

# Service is fully active
await nodedb.update_node_state(
    node_id="node-a1b2c3d4e5",
    state=StigmaState.ACTIVE,
    metrics={"latency_p99_ms": 45, "throughput_rps": 850},
    ndb_quality=NDBQuality.EXCELLENT
)

# Service degradation detected
await nodedb.update_node_state(
    node_id="node-a1b2c3d4e5",
    state=StigmaState.DEGRADED,
    metrics={"error_rate": 0.15, "latency_p99_ms": 2500},
    ndb_quality=NDBQuality.POOR
)
```

### Step 4: Monitor with NodeDB Client

```python
from nodendb_stigma import NodeDBClient, get_nodedb, StigmaState, NDBQuality

# Service reports its own state
class MyWorker:
    def __init__(self, node_id: str):
        nodedb = get_nodedb()
        self.client = NodeDBClient(nodedb, node_id)
    
    async def process_task(self, task):
        try:
            start = time.time()
            result = await self._do_work(task)
            latency = (time.time() - start) * 1000
            
            # Report success metrics
            await self.client.set_state(
                StigmaState.ACTIVE,
                metrics={"last_task_ms": latency, "tasks_completed": 1},
                ndb_quality=NDBQuality.GOOD
            )
            
            return result
        except Exception as e:
            logger.error(f"Task failed: {e}")
            
            # Request recovery
            await self.client.request_recovery()
```

### Step 5: Query Node Information

```python
# List all nodes
all_nodes = await nodedb.list_nodes()
for node in all_nodes:
    print(f"Node: {node['metadata']['node_id']}")
    print(f"  Service: {node['metadata']['service_name']}")
    print(f"  State: {node['state']['stigma_state']}")
    print(f"  NDB Quality: {node['state']['ndb_quality']}")

# Get specific node info
node_info = await nodedb.get_node_info("node-a1b2c3d4e5")
print(f"Capabilities: {node_info['metadata']['capabilities']}")
print(f"Health Checks: {node_info['metadata']['health_checks']}")

# Execute health check
health = await nodedb.health_check("node-a1b2c3d4e5")
print(f"Health Status: {health}")
```

---

## Real-World Example: ASI Trinity Integration

### Before (Rigid Node Scripts)
```python
# Old: Separate handler per service
alba_handler = ALBANodeHandler(alba_service)
albi_handler = ALBINodeHandler(albi_service)
jona_handler = JONANodeHandler(jona_service)
asi_handler = ASINodeHandler(asi_service)

# Each needs custom code
alba_handler.start()
albi_handler.start()
jona_handler.start()
asi_handler.start()
```

### After (NodeDB Stigma)
```python
# New: Single registration for all
from nodendb_stigma import initialize_nodendb, register_service_with_nodedb
from asi_trinity import alba, albi, jona, asi

async def setup_trinity():
    nodedb = await initialize_nodendb()
    
    # Register all services with same pattern
    for service, name in [
        (alba, "ALBA"),
        (albi, "ALBI"),
        (jona, "JONA"),
        (asi, "ASI"),
    ]:
        await register_service_with_nodedb(service, name)
    
    # All services now tracked by single adaptive system
    nodes = await nodedb.list_nodes()
    print(f"✅ Initialized {len(nodes)} Trinity nodes via Stigma Pattern")
```

---

## NDB Resonance Quality Integration

NodeDB tracks **NDB quality signal** which reflects system resonance:

```python
# Quality levels (mapped to 0.0-1.0 float)
NDBQuality.EXCELLENT    # 1.0  - Perfect resonance
NDBQuality.GOOD         # 0.8  - Normal operation
NDBQuality.FAIR         # 0.6  - Slight degradation
NDBQuality.POOR         # 0.3  - Significant issues
NDBQuality.CRITICAL     # 0.0  - Complete breakdown

# NDB delta tracks changes
state.ndb_delta = 0.05  # Quality improved by 5%
state.ndb_delta = -0.15 # Quality degraded by 15%

# Use delta to trigger recovery/alerts
if state.ndb_delta < -0.2:
    await nodedb.trigger_recovery(node_id)
```

---

## Tide Pressure Simulation

Simulate system-wide resource constraints:

```python
# Normal operation
await nodedb.simulate_tide_pressure(0.3)  # Low pressure

# Elevated stress
await nodedb.simulate_tide_pressure(0.7)  # High pressure

# Critical
await nodedb.simulate_tide_pressure(0.95) # Critical pressure

# All nodes' tide_pressure field updates automatically
# Services can check pressure to adjust behavior:
# - Under high tide: reduce non-critical work
# - Under critical: prioritize recovery paths
```

---

## Why Stigma Pattern Beats Rigid Scripts

| Aspect | Rigid Script | Stigma Pattern |
|--------|-------------|-----------------|
| **New Service Type** | Write new Node class | Auto-discovered |
| **Capability Discovery** | Hardcoded | Dynamic introspection |
| **Health Checks** | Manual endpoint list | Pattern detection |
| **Configuration** | Parse config files | Inspect module attrs |
| **Adaptation** | Code change required | Automatic |
| **Maintenance** | O(n) per service | O(1) per system |
| **Extensibility** | Limited | Unlimited |

---

## API Reference

### NodeDBCore Methods

```python
# Register service
metadata = await nodedb.register_service(
    service_module: Any,
    service_name: str,
    health_check_fn: Optional[Callable] = None
) -> NodeMetadata

# Update node state
state = await nodedb.update_node_state(
    node_id: str,
    state: StigmaState,
    metrics: Optional[Dict] = None,
    ndb_quality: Optional[NDBQuality] = None
) -> NodeState

# Trigger recovery
state = await nodedb.trigger_recovery(node_id: str) -> NodeState

# Query nodes
info = await nodedb.get_node_info(node_id: str) -> Dict
nodes = await nodedb.list_nodes() -> List[Dict]

# Health operations
health = await nodedb.health_check(node_id: str) -> Dict

# System pressure
await nodedb.simulate_tide_pressure(pressure: float) -> None
```

### StigmaState Enum
```python
INITIALIZING  # Service starting up
READY         # Ready to accept requests
ACTIVE        # Actively processing
DEGRADED      # Performance issues detected
RECOVERING    # In recovery workflow
OFFLINE       # Not responding
```

### NDBQuality Enum
```python
EXCELLENT  # Perfect resonance
GOOD       # Normal operation
FAIR       # Slight issues
POOR       # Significant degradation
CRITICAL   # Complete breakdown
```

---

## Next Steps

1. **Replace existing node handlers** with NodeDB registration
2. **Migrate health checks** to custom `health_check_fn` callbacks
3. **Update monitoring** to pull from NodeDB instead of per-service dashboards
4. **Integrate Tide pressure** into resource scheduling
5. **Test with ASI Trinity** (ALBA, ALBI, JONA, ASI) as primary use case

---

## Debugging NodeDB

```python
# Enable debug logging
import logging
logger = logging.getLogger('nodendb_stigma')
logger.setLevel(logging.DEBUG)

# Dump full node structure
import json
node_info = await nodedb.get_node_info("node-a1b2c3d4e5")
print(json.dumps(node_info, indent=2, default=str))

# Monitor state changes
for node in await nodedb.list_nodes():
    print(f"{node['metadata']['service_name']}: {node['state']['stigma_state']}")
```

---

**Author's Note:** The Stigma Pattern treats all nodes as adaptive entities governed by a universal pattern, not individual rules. This mirrors the Kloud philosophy: fluid, resonant, recoverable.
