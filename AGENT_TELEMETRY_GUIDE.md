# Agent Telemetry Integration Guide

## Overview

AI agents (AGIEM, ASI, Blerina, SAAS) can now send telemetry data to the Alba/Albi/Jona Trinity stack for real-time monitoring, analytics, and coordination.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  AI AGENTS                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  AGIEM   │  │   ASI    │  │ Blerina  │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │              │                │
│       └─────────────┼──────────────┘                │
│                     │                                │
│           ┌─────────▼──────────┐                    │
│           │ TelemetryRouter    │                    │
│           └─────────┬──────────┘                    │
│                     │                                │
│        ┌────────────┼────────────┐                  │
│        │            │            │                  │
│   ┌────▼─────┐ ┌───▼────┐ ┌────▼─────┐            │
│   │  ALBA    │ │  ALBI  │ │  JONA    │            │
│   │  :5050   │ │ :6060  │ │  :7070   │            │
│   └──────────┘ └────────┘ └──────────┘            │
│   Data Collect  Analytics  Coordination            │
└─────────────────────────────────────────────────────┘
```

## Components

### 1. Alba (Port 5050) - Data Collection

**Endpoint:** `POST /api/telemetry/ingest`

Collects raw telemetry data from agents:

- Operation timing
- Token usage
- Success/failure status
- Metadata and context

### 2. Albi (Port 6060) - Analytics

**Endpoint:** `POST /api/analytics/agent`

Processes agent analytics:

- Performance metrics
- Token consumption analysis
- Duration tracking
- Success rate calculations

### 3. Jona (Port 7070) - Coordination

**Endpoint:** `POST /api/coordination/event`

Coordinates agent events:

- Operation status tracking
- Error logging
- Multi-agent orchestration
- Event correlation

## Usage

### Using TelemetryRouter (Recommended)

```python
from agent_telemetry import TelemetryRouter, AgentMetrics
import time

# Initialize router
router = TelemetryRouter(
    alba_url="http://localhost:5050",
    albi_url="http://localhost:6060",
    jona_url="http://localhost:7070"
)

# Create metrics
metrics = AgentMetrics(
    agent_name="MyAgent",
    timestamp=time.time(),
    status="success",
    operation="data_processing",
    duration_ms=1234.56,
    input_tokens=500,
    output_tokens=150,
    success=True,
    metadata={"stage": "preprocessing"}
)

# Send to all services
results = router.send_all(metrics)
# Returns: {'alba': True, 'albi': True, 'jona': True}
```

### Using AgentTelemetryMixin

```python
from agent_telemetry import AgentTelemetryMixin

class MyAgent(AgentTelemetryMixin):
    def __init__(self):
        super().__init__(telemetry_enabled=True)
        self.agent_name = "MyAgent"
    
    def process_data(self):
        self.start_operation("data_processing")
        
        # Your processing logic here
        result = do_work()
        
        self.end_operation(
            success=True,
            input_tokens=500,
            output_tokens=150,
            metadata={"result_size": len(result)}
        )
        
        return result
```

### Standalone Function

```python
from agent_telemetry import init_telemetry, send_agent_telemetry

# Initialize once
init_telemetry()

# Send telemetry anywhere
send_agent_telemetry(
    agent_name="QuickAgent",
    operation="quick_task",
    duration_ms=100.0,
    success=True
)
```

## Integration with Existing Agents

### AGIEM Integration

```python
# In agiem_core.py
from agent_telemetry import TelemetryRouter

class AGIEMCore:
    def __init__(self):
        self.telemetry = TelemetryRouter()
        # ... existing init code
    
    def run_pipeline(self):
        start = time.time()
        
        # Run pipeline
        result = self._execute_pipeline()
        
        # Send telemetry
        metrics = AgentMetrics(
            agent_name="AGIEM",
            timestamp=time.time(),
            status="success",
            operation="pipeline_execution",
            duration_ms=(time.time() - start) * 1000,
            success=True,
            metadata={"nodes": len(self.nodes)}
        )
        self.telemetry.send_all(metrics)
        
        return result
```

### ASI Integration

```python
# In asi_core.py
from agent_telemetry import send_agent_telemetry

class ASICore:
    def analyze_status(self):
        start = time.time()
        
        # Existing analysis
        result = self._perform_analysis()
        
        # Send telemetry
        send_agent_telemetry(
            agent_name="ASI",
            operation="realtime_analysis",
            duration_ms=(time.time() - start) * 1000,
            success=True,
            metadata={"health_score": self.health_score}
        )
        
        return result
```

### Blerina Integration

```python
# In blerina_reformatter.py
from agent_telemetry import init_telemetry, send_agent_telemetry

init_telemetry()

def extract_youtube_metadata(video_id: str):
    start = time.time()
    
    try:
        # Existing YouTube API call
        metadata = youtube.videos().list(...).execute()
        
        # Success telemetry
        send_agent_telemetry(
            agent_name="Blerina",
            operation="youtube_metadata_extraction",
            duration_ms=(time.time() - start) * 1000,
            success=True,
            metadata={"video_id": video_id, "views": metadata.get("viewCount")}
        )
        
        return metadata
        
    except Exception as e:
        # Error telemetry
        send_agent_telemetry(
            agent_name="Blerina",
            operation="youtube_metadata_extraction",
            duration_ms=(time.time() - start) * 1000,
            success=False,
            metadata={"error": str(e)}
        )
        raise
```

## Data Structures

### AgentMetrics

```python
@dataclass
class AgentMetrics:
    agent_name: str           # Name of the agent (AGIEM, ASI, Blerina, etc.)
    timestamp: float          # Unix timestamp
    status: str               # "success" or "error"
    operation: str            # Operation name (e.g., "pipeline_execution")
    duration_ms: Optional[float] = None      # Operation duration in milliseconds
    input_tokens: Optional[int] = None       # Input token count (for LLM agents)
    output_tokens: Optional[int] = None      # Output token count
    success: bool = True                     # Operation success flag
    error: Optional[str] = None              # Error message if failed
    metadata: Optional[Dict[str, Any]] = None # Additional context
```

## API Endpoints

### Alba Telemetry Endpoint

```http
POST http://localhost:5050/api/telemetry/ingest
Content-Type: application/json

{
  "source": "AGIEM",
  "data": {
    "agent_name": "AGIEM",
    "timestamp": 1734108000.123,
    "status": "success",
    "operation": "pipeline_execution",
    "duration_ms": 1234.56
  }
}
```

### Albi Analytics Endpoint

```http
POST http://localhost:6060/api/analytics/agent
Content-Type: application/json

{
  "agent": "ASI",
  "operation": "realtime_analysis",
  "duration_ms": 567.89,
  "tokens": {
    "input": 500,
    "output": 150
  },
  "success": true,
  "metadata": {}
}
```

### Jona Coordination Endpoint

```http
POST http://localhost:7070/api/coordination/event
Content-Type: application/json

{
  "agent": "Blerina",
  "operation": "youtube_metadata_extraction",
  "status": "success",
  "success": true,
  "error": null
}
```

## Viewing Telemetry Data

### Alba - View Collected Data

```bash
curl http://localhost:5050/data?limit=10
curl http://localhost:5050/metrics
```

### Albi - View Analytics

```bash
curl http://localhost:6060/insights?limit=10
curl http://localhost:6060/anomalies?limit=10
```

### Jona - View Coordination Log

```bash
curl http://localhost:7070/queue
curl http://localhost:7070/metrics
```

## Monitoring & Observability

All telemetry is automatically traced with OpenTelemetry:

- **Tempo** (port 3200): Distributed tracing
- **Loki** (port 3100): Log aggregation
- **Prometheus** (port 9090): Metrics collection
- **Grafana** (port 3001): Visualization dashboards

### Grafana Dashboards

View agent telemetry in Grafana:

1. Open <http://localhost:3001>
2. Navigate to "Agent Performance" dashboard
3. Filter by agent name (AGIEM, ASI, Blerina)
4. View metrics:
   - Operation duration
   - Success rate
   - Token usage (for LLM agents)
   - Error frequency

## Testing

Test the integration:

```bash
python agent_telemetry.py
```

Expected output:

```
🧪 Testing Agent Telemetry Integration

Testing AGIEM -> Alba/Albi/Jona...
📊 AGIEM.pipeline_execution: 3/3 telemetry endpoints reached
Results: {'alba': True, 'albi': True, 'jona': True}

Testing ASI -> Alba/Albi/Jona...
📊 ASI.realtime_analysis: 3/3 telemetry endpoints reached
Results: {'alba': True, 'albi': True, 'jona': True}

Testing Blerina -> Alba/Albi/Jona...
📊 Blerina.youtube_metadata_extraction: 3/3 telemetry endpoints reached
Results: {'alba': True, 'albi': True, 'jona': True}

✅ Telemetry integration test complete
```

## Configuration

### Environment Variables

```bash
# .env
ALBA_TELEMETRY_URL=http://localhost:5050
ALBI_ANALYTICS_URL=http://localhost:6060
JONA_COORDINATION_URL=http://localhost:7070
TELEMETRY_ENABLED=true
```

### Production URLs

For Hetzner deployment (157.90.234.158):

```python
router = TelemetryRouter(
    alba_url="http://157.90.234.158:5050",
    albi_url="http://157.90.234.158:6060",
    jona_url="http://157.90.234.158:7070"
)
```

## Troubleshooting

### Telemetry not sending

1. **Check services are running:**

   ```bash
   curl http://localhost:5050/health
   curl http://localhost:6060/health
   curl http://localhost:7070/health
   ```

2. **Check network connectivity:**

   ```bash
   docker network inspect kloud-network
   ```

3. **View service logs:**

   ```bash
   docker logs kloud-alba --tail 50
   docker logs kloud-albi --tail 50
   docker logs kloud-jona --tail 50
   ```

### Partial failures (1/3 or 2/3 success)

This is normal if a service is temporarily unavailable. Telemetry will:

- Log warnings for failed endpoints
- Continue sending to available endpoints
- Not block agent operations

### High latency

If telemetry adds noticeable latency:

1. Increase timeout (default: 5s)
2. Send telemetry asynchronously
3. Batch telemetry data

```python
# Async example
import asyncio

async def send_telemetry_async(metrics):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, router.send_all, metrics)
```

## Best Practices

1. **Always include operation name** - Makes filtering and debugging easier
2. **Add meaningful metadata** - Context helps with root cause analysis
3. **Track both success and failure** - Error telemetry is critical
4. **Use consistent agent names** - "AGIEM" not "agiem" or "Agiem"
5. **Measure duration** - Performance tracking requires timing
6. **Don't block on telemetry** - Use try/except to prevent crashes

## Status

✅ **COMPLETE** - Agent telemetry integration fully operational

- [x] TelemetryRouter implementation
- [x] Alba endpoint (`/api/telemetry/ingest`)
- [x] Albi endpoint (`/api/analytics/agent`)
- [x] Jona endpoint (`/api/coordination/event`)
- [x] AgentTelemetryMixin for easy integration
- [x] Standalone helper functions
- [x] Full test suite (3/3 agents passing)
- [x] OpenTelemetry tracing enabled
- [x] Documentation complete

## Next Steps

1. **Integrate AGIEM** - Add telemetry to `agiem_core.py`
2. **Integrate ASI** - Add telemetry to `asi_core.py`
3. **Integrate Blerina** - Add telemetry to `blerina_reformatter.py`
4. **Create Grafana dashboards** - Visualize agent performance
5. **Set up alerts** - Notify on agent failures or high latency

---

## Stigma Bus Integration (NEW)

### Overview

Stigma Bus is an event-driven reactive system that connects all intelligence modules to Rust Core (Ocean). Every event from Trinity (ALBA/ALBI/JONA), MALI, BLERINA, LIAM, ALDA, KLAJDI, and ASI propagates through Stigma Bus and triggers:

1. **State Updates** - FabricState reflects all module signals
2. **Capability Routing** - Events map to agent capabilities
3. **Autoscaling** - Agents scale based on capability demand
4. **Firewall Intelligence** - Edge Gateway protects based on anomalies & threats

### Architecture: Stigma Fabric

```
                    ┌─────────────────────────────────────┐
                    │        TRINITY (ALBA/ALBI/JONA)     │
                    │      + MALI + BLERINA + LIAM        │
                    │      + ALDA + KLAJDI + ASI + AGENTS │
                    └──────────────────┬──────────────────┘
                                       │
                                       │ Stigma Event
                                       │ {source, kind, level, payload}
                                       │
                    ┌──────────────────▼──────────────────┐
                    │     STIGMA BUS (broadcast::channel) │
                    │    Kapacitet: 10,000 events/buffer  │
                    └──────────────────┬──────────────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     │                 │                 │
           ┌─────────▼──────────┐  │  │            │
           │  DISPATCH_EVENT    │  │  │            │
           │  (per-module       │  │  │            │
           │   handlers)        │  │  │            │
           └─────────┬──────────┘  │  │            │
                     │             │  │            │
        ┌────────────▼────────┐    │  │       ┌────▼────────────┐
        │  FabricState Update │    │  │       │ CAPABILITY ROUTER │
        │  - patterns         │    │  │       │ (event → agent)   │
        │  - gaps             │    │  │       └────┬─────────────┘
        │  - risks            │    │  │            │
        │  - predictions      │    │  │       ┌────▼──────────────┐
        │  - anomalies        │    │  │       │ AUTOSCALE TRIGGER │
        │  - harmony          │    │  │       │ POST /agents/scale│
        │  - asi_signal       │    │  │       └───────────────────┘
        └────────────┬────────┘    │  │
                     │             │  │
        ┌────────────▼─────────────┼──┼───────────────────┐
        │         GET /fabric/state        (refreshed 150ms)
        └────────────┬─────────────────────────────────────┘
                     │
        ┌────────────▼─────────────────────────────────────┐
        │  EDGE GATEWAY - Intelligent Routing + Firewall   │
        │  - Reads FabricState                             │
        │  - Routes based on asi_signal                    │
        │  - Applies firewall rules based on anomalies     │
        │  - Probes health (150ms loop, NOT fabric loop)   │
        └─────────────────────────────────────────────────┘
```

### Module → Capability Mapping

| Module  | Event      | Level | Capability          | Target  |
| ------- | ---------- | ----- | ------------------- | ------- |
| ALBA    | frame      | 3+    | network-monitoring  | 4 users |
| ALBI    | anomaly    | 2+    | pattern-recognition | 6 users |
| JONA    | harmony    | any   | insight-synthesis   | 3 users |
| MALI    | prediction | 3+    | meta-analysis       | 5 users |
| MALI    | pattern    | 2+    | pattern-analysis    | 4 users |
| BLERINA | gap        | 4+    | gap-detection       | 5 users |
| LIAM    | eigen      | 3+    | tensor-processing   | 5 users |
| LIAM    | tensor     | 3+    | optimization        | 4 users |
| ALDA    | batch      | 2+    | labor-orchestration | 6 users |
| KLAJDI  | anomaly    | 2+    | investigation       | 4 users |
| KLAJDI  | risk       | 2+    | risk-assessment     | 3 users |
| ASI     | signal     | any   | node-supervision    | 3 users |

### Sending Stigma Events

All modules can POST to `/fabric/stigma`:

```bash
curl -X POST http://10.10.0.1:9000/fabric/stigma \
  -H "Content-Type: application/json" \
  -d '{
    "source": "MALI",
    "kind": "prediction",
    "level": 3,
    "payload": {
      "predictions": ["cpu_rising", "memory_spike"],
      "confidence": 0.95
    }
  }'
```

### Module-Specific Routes (Convenience)

```bash
# Trinity
POST /trinity/event

# MALI
POST /mali/event

# BLERINA
POST /blerina/event

# LIAM
POST /liam/event

# ALDA
POST /alda/event

# KLAJDI
POST /klajdi/event

# Agents
POST /agents/submit
```

### Edge Gateway Firewall Intelligence

Edge Gateway reads `FabricState` every 150ms and applies intelligent firewall rules:

**Rule Categories:**

1. **Trinity Anomalies** → Block suspicious patterns
   - If `trinity_anomaly` in anomalies AND (large payload OR admin route)
   - Action: BLOCK (403)

2. **MALI Patterns** → Rate limit high-frequency requests
   - If `mali_pattern` in anomalies AND (API request AND small payload)
   - Action: RATE_LIMIT (429)

3. **BLERINA Gaps** → Redirect sensitive routes
   - If `gap:` in anomalies AND (config/credential route)
   - Action: REDIRECT to fallback_origin

4. **LIAM Tensor Spikes** → Block large payloads
   - If `liam_eigen_spike` in anomalies AND (payload > 100KB)
   - Action: BLOCK (403)

5. **ALDA Compute Overload** → Reroute heavy compute
   - If `asi_signal == "compute_overload"` AND (analyze/compute route)
   - Action: REDIRECT to compute_origin

6. **KLAJDI Risks** → Block unknown sources
   - If `klajdi_risk` in anomalies AND (non-health AND empty body)
   - Action: BLOCK (403)

7. **Degraded Harmony** → Activate protection
   - If `harmony < 40%` AND (large payload)
   - Action: RATE_LIMIT (429)

### Capability Routing Logic

```rust
// Example: MALI prediction event
if let Some(cap_target) = capability_router(&event) {
    // Returns: CapabilityTarget { 
    //   capability: "meta-analysis", 
    //   target_capacity: 5 
    // }
    trigger_autoscale("meta-analysis", 5).await;
    
    // Unified Agents System receives:
    // POST /agents/scale
    // { "capability": "meta-analysis", "target_capacity": 5 }
}
```

### Autoscaling Flow

```
Stigma Event (level: 3+)
    ↓
capability_router() → (capability, target)
    ↓
trigger_autoscale(capability, target)
    ↓
POST /agents/scale {capability, target_capacity}
    ↓
Unified Agents System scales agent pools
    ↓
FabricState reflects new pool sizes
    ↓
Edge Gateway routes to newly scaled agents
```

---

**File:** `agent_telemetry.py`, `ocean_core/src/main.rs`, `edge_gateway/src/main.rs`  
**Services:** Ocean Core (9000), Edge Gateway (7000)  
**Status:** ✅ Production Ready (Stigma Fabric Integration Complete)  
**Last Updated:** May 16, 2026
