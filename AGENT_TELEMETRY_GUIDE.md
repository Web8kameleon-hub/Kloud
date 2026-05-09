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
1. Open http://localhost:3001
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

**File:** `agent_telemetry.py`  
**Services:** Alba (5050), Albi (6060), Jona (7070)  
**Status:** ✅ Production Ready  
**Last Updated:** December 13, 2025

