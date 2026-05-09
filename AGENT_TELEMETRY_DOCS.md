# Agent Telemetry Integration - Dokumentacion i Plotë

## 📡 Çfarë është Agent Telemetry?

Sistemi që lidh **agjentët inteligjentë** (AGIEM, ASI, Blerina) me **pipeline-in e telemetrisë** Alba/Albi/Jona.

### Agjentët:
- **AGIEM** - Menaxheri i pipeline-ve (koordinon ALBA→ALBI→JONA→ASI)
- **ASI** - Orchestratori real-time (merr status, jep komanda)
- **Blerina** - Agjent domeni (përdor analizat për të krijuar dokumente)

### Trinity (Alba/Albi/Jona):
- **ALBA** - Data Collector (mbledh telemetri nga sensorë)
- **ALBI** - Neural Processor (analizon dhe identifikon anomali)
- **JONA** - Ethical Overseer (sintetizon dhe kontrollon vendime)

---

## 🏗️ Arkitektura

```
┌─────────────────────────────────────────────┐
│           AGJENTËT (AI Agents)              │
├─────────────────────────────────────────────┤
│  AGIEM  │   ASI   │  Blerina  │  Custom    │
└────┬────┴────┬────┴────┬──────┴────┬────────┘
     │         │         │           │
     └─────────┴─────────┴───────────┘
               │
     ┌─────────▼──────────────────┐
     │  Agent Telemetry Router    │
     │  (agent_telemetry.py)      │
     └────┬──────────┬──────┬─────┘
          │          │      │
     ┌────▼───┐ ┌───▼───┐ ┌▼────┐
     │  ALBA  │ │ ALBI  │ │JONA │  ← Trinity
     │  5050  │ │ 6060  │ │7070 │
     └────────┘ └───────┘ └─────┘
          │          │      │
          └──────────┴──────┘
                   │
          ┌────────▼──────────┐
          │   ASI Realtime    │  ← Orchestrator
          │   Engine (8000)   │
          └───────────────────┘
```

---

## 📦 Komponente

### 1. **AgentMetrics** (Dataclass)

Struktura standarde për metrikat e agjentëve:

```python
@dataclass
class AgentMetrics:
    agent_name: str             # "AGIEM", "ASI", "Blerina"
    timestamp: float            # Unix timestamp
    status: str                 # "success" | "error"
    operation: str              # "pipeline_execution", "analyze_system"
    duration_ms: Optional[float]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    success: bool
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]
```

### 2. **AgentPulse** (Dataclass)

Snapshot real-time i shëndetit të agjentëve:

```python
@dataclass
class AgentPulse:
    agent: str       # "alba", "albi", "jona"
    role: str        # "collector", "analyzer", "synthesizer"
    status: str      # "ok" | "error"
    metrics: Dict    # Metrikat aktuale
    ts: str          # ISO timestamp
```

### 3. **TelemetryRouter**

Klasa kryesore që ruan lidhjet me Trinity dhe ASI.

#### Inicializimi:

```python
router = TelemetryRouter(
    base_url="http://127.0.0.1",
    alba_port=5050,
    albi_port=6060,
    jona_port=7070,
    asi_port=8000,
    enabled=True
)
```

#### READ Operations:

| Metoda | Endpoint | Qëllimi |
|--------|----------|---------|
| `get_root()` | `/` | Service info (version, uptime) |
| `get_asi_status()` | `/asi/status` | Trinity orchestration status |
| `get_asi_health()` | `/asi/health` | Health check (ok/unhealthy) |
| `get_agent_metrics(agent)` | `/asi/{agent}/metrics` | Alba/Albi/Jona specifike |
| `get_prometheus_metrics()` | `/metrics` | Prometheus exposition format |
| `pulse(agent, role)` | - | Real-time snapshot |

#### WRITE Operations:

| Metoda | Endpoint | Qëllimi |
|--------|----------|---------|
| `send_to_alba(metrics)` | `/api/telemetry/ingest` | Dërgon raw telemetri në Alba |
| `send_to_albi(metrics)` | `/api/analytics/agent` | Dërgon analizë në Albi |
| `send_to_jona(metrics)` | `/api/coordination/event` | Dërgon event në Jona |
| `execute_trinity(cmd, payload)` | `/asi/execute` | Ekzekuton komanda Trinity |
| `send_all(metrics)` | - | Dërgon në të tre njëherësh |

---

## 🚀 Përdorimi

### A. Standalone Functions (për scripts)

#### 1. Send Simple Telemetry:

```python
from agent_telemetry import send_agent_telemetry

send_agent_telemetry(
    agent_name="AGIEM",
    operation="pipeline_execution",
    duration_ms=1234.56,
    success=True,
    metadata={"stage": "ALBA", "frames": 267}
)
```

#### 2. Initialize Router Globally:

```python
from agent_telemetry import init_telemetry

router = init_telemetry(
    base_url="http://production-server",
    alba_port=5050,
    enabled=True
)
```

#### 3. Execute Trinity Commands:

```python
result = router.execute_trinity(
    command="analyze_system",
    payload={"priority": "high", "center": "Zurich-Lab"}
)
print(result)
# {'status': 'success', 'task_id': 'abc123', ...}
```

#### 4. Get Real-Time Pulse:

```python
alba_pulse = router.pulse("alba", "collector")
print(f"Alba Status: {alba_pulse.status}")
print(f"Metrics: {alba_pulse.metrics}")
```

---

### B. Mixin for Agent Classes

Për klasat e agjentëve që duan telemetri automatike:

```python
from agent_telemetry import AgentTelemetryMixin

class MyAgent(AgentTelemetryMixin):
    def __init__(self):
        super().__init__(telemetry_enabled=True)
        self.agent_name = "AGIEM"
    
    def do_work(self):
        self.start_operation("data_processing")
        
        # ... do actual work ...
        
        self.end_operation(
            success=True,
            input_tokens=500,
            output_tokens=150,
            metadata={"frames": 267}
        )
```

Kjo automatikisht:
- Llogarit `duration_ms`
- Dërgon në Alba/Albi/Jona
- Logon rezultatet

---

### C. Continuous Monitoring Loop

Për monitorim të vazhdueshëm (p.sh. në service):

```python
from agent_telemetry import telemetry_loop

telemetry_loop(
    interval=15,           # Kontrollo çdo 15 sekonda
    max_iterations=None    # None = infinite
)
```

**Çfarë bën:**
1. Merr ASI status dhe health
2. Merr pulse nga Alba/Albi/Jona
3. **Nëse health OK dhe Jona alignment OK:**
   - Ekzekuton `analyze_system` command
4. **Nëse health dobët:**
   - Defer actions, log warning
5. Emit pulse logs për audit
6. Sleep `interval` sekonda

---

## 💻 CLI Usage

### Test Mode (dërgon sample metrics):

```bash
python agent_telemetry.py --test
```

Output:
```
🧪 Testing Agent Telemetry Integration

Testing AGIEM -> Alba/Albi/Jona...
📊 AGIEM.pipeline_execution: 3/3 telemetry endpoints reached
Results: {'alba': True, 'albi': True, 'jona': True}

Testing ASI -> Alba/Albi/Jona...
📊 ASI.realtime_analysis: 3/3 telemetry endpoints reached
Results: {'alba': True, 'albi': True, 'jona': True}

✅ Telemetry integration test complete
```

### Monitor Mode (continuous loop):

```bash
# Default: 15s interval, infinite
python agent_telemetry.py --monitor

# Custom interval (30s)
python agent_telemetry.py --monitor --interval 30

# Limited iterations (100 checks)
python agent_telemetry.py --monitor --max-iterations 100
```

---

## 🔐 Health-Gated Actions

Sistemi ka **siguri të integruar**:

```python
if (
    asi.get("health") == "ok"
    and health.get("status") == "healthy"
    and jona_pulse.metrics.get("alignment_ok", True)
):
    # SAFE to execute commands
    router.execute_trinity("analyze_system")
else:
    # DEFER actions, log warning
    logger.warning("Health/alignment not OK; deferring actions")
```

**Pse është kjo e rëndësishme?**
- **ASI health**: Kontrollon që orchestratori të jetë operacional
- **Jona alignment**: Siguron që vendimi të jetë etikisht i sigurt
- **Deferred execution**: Nëse dicka nuk është OK, veprimi nuk kryhet

---

## 📊 Prometheus Integration

Sistemi ekspozon metrikat në format Prometheus:

```python
prom_metrics = router.get_prometheus_metrics()
print(prom_metrics)
```

Output (sample):
```prometheus
# HELP agent_operations_total Total operations by agent
# TYPE agent_operations_total counter
agent_operations_total{agent="AGIEM",status="success"} 267
agent_operations_total{agent="ASI",status="success"} 42

# HELP agent_duration_seconds Operation duration
# TYPE agent_duration_seconds histogram
agent_duration_seconds_bucket{agent="AGIEM",le="0.5"} 100
agent_duration_seconds_bucket{agent="AGIEM",le="1.0"} 200
```

Mund të konsumohet nga:
- **Grafana** dashboards
- **Alertmanager** rules
- **SIEM** systems

---

## 🎯 Use Cases

### 1. AGIEM Pipeline Execution

```python
# AGIEM përfundon një cycle
from agent_telemetry import send_agent_telemetry

send_agent_telemetry(
    agent_name="AGIEM",
    operation="cycle_execution",
    duration_ms=6984.0,
    success=True,
    metadata={
        "center": "Zurich-Lab",
        "stages": ["ALBA", "ALBI", "JONA", "ASI"],
        "frames_processed": 267,
        "anomalies_detected": 6
    }
)
```

### 2. ASI Real-Time Analysis

```python
# ASI kompleton një analizë
send_agent_telemetry(
    agent_name="ASI",
    operation="realtime_analysis",
    duration_ms=108.0,
    success=True,
    metadata={
        "health_score": 93.35,
        "status": "operational",
        "success_rate": "99.34%"
    }
)
```

### 3. Blerina Document Generation

```python
# Blerina gjeneron raport
send_agent_telemetry(
    agent_name="Blerina",
    operation="report_generation",
    duration_ms=2340.0,
    success=True,
    metadata={
        "document_type": "PDF",
        "pages": 5,
        "sources": ["Alba", "Albi", "Jona"]
    }
)
```

### 4. Execute Trinity Command (health-gated)

```python
router = TelemetryRouter()

# Check health first
health = router.get_asi_health()
if health.get("status") == "healthy":
    result = router.execute_trinity(
        command="start_monitoring",
        payload={"center": "Zurich-Lab", "interval": 10}
    )
    print(f"Command executed: {result}")
else:
    print("Health check failed, command deferred")
```

---

## 🛡️ Error Handling

Sistemi ka **graceful degradation**:

```python
# Nëse Alba/Albi/Jona janë offline:
results = router.send_all(metrics)
# {'alba': False, 'albi': False, 'jona': True}
# ↑ Vazhdon edhe nëse disa endpoints dështojnë

# Nëse ASI është offline:
asi_status = router.get_asi_status()
# {'health': 'error', 'error': 'Connection refused'}
# ↑ Kthen error dict në vend të exception
```

**Best Practices:**
- Përdor `enabled=False` për testing local
- Monitoron logs për `ERROR:AgentTelemetry`
- Check success counts: `3/3` = perfekt, `0/3` = problem

---

## 🔧 Configuration

### Production Setup:

```python
from agent_telemetry import init_telemetry

router = init_telemetry(
    base_url="https://production.kloud.com",
    alba_port=5050,
    albi_port=6060,
    jona_port=7070,
    asi_port=8000,
    enabled=True
)
```

### Development (local):

```python
router = init_telemetry(
    base_url="http://127.0.0.1",
    enabled=False  # Disable actual sending
)
```

### Docker Compose:

```yaml
services:
  agent-telemetry:
    build: .
    command: python agent_telemetry.py --monitor --interval 15
    environment:
      - ALBA_URL=http://alba:5050
      - ALBI_URL=http://albi:6060
      - JONA_URL=http://jona:7070
      - ASI_URL=http://asi:8000
    depends_on:
      - alba
      - albi
      - jona
      - asi
```

---

## 📈 Metrics Flow

```
AGIEM executes pipeline
  ↓
send_agent_telemetry("AGIEM", "pipeline_execution")
  ↓
AgentMetrics created (agent_name, timestamp, duration, metadata)
  ↓
router.send_all(metrics)
  ├→ send_to_alba()  → POST /api/telemetry/ingest
  ├→ send_to_albi()  → POST /api/analytics/agent
  └→ send_to_jona()  → POST /api/coordination/event
  ↓
Results: {'alba': True, 'albi': True, 'jona': True}
  ↓
Logged: "📊 AGIEM.pipeline_execution: 3/3 telemetry endpoints reached"
```

---

## 🔍 Debugging

### Enable Debug Logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Output:
```
DEBUG:AgentTelemetry:✓ Alba: AGIEM telemetry sent
DEBUG:AgentTelemetry:✓ Albi: AGIEM analytics sent
DEBUG:AgentTelemetry:✓ Jona: AGIEM event sent
INFO:AgentTelemetry:📊 AGIEM.pipeline_execution: 3/3 telemetry endpoints reached
```

### Check Connection:

```python
router = TelemetryRouter()

# Test each endpoint
print("Alba:", router.send_to_alba(test_metrics))
print("Albi:", router.send_to_albi(test_metrics))
print("Jona:", router.send_to_jona(test_metrics))
```

---

## 🎓 Integration Examples

### AGIEM Pipeline Integration:

```python
# In agiem_core.py
from agent_telemetry import AgentTelemetryMixin

class AGIEMCore(AgentTelemetryMixin):
    def __init__(self):
        super().__init__(telemetry_enabled=True)
        self.agent_name = "AGIEM"
    
    def run_cycle(self, center, specialization):
        self.start_operation("cycle_execution")
        
        # Execute ALBA stage
        alba_frames = self.run_alba_stage()
        
        # Execute ALBI stage
        albi_insights = self.run_albi_stage(alba_frames)
        
        # Execute JONA stage
        jona_synthesis = self.run_jona_stage(albi_insights)
        
        # Execute ASI stage
        asi_realtime = self.run_asi_stage(jona_synthesis)
        
        self.end_operation(
            success=True,
            metadata={
                "center": center,
                "specialization": specialization,
                "frames": len(alba_frames),
                "anomalies": len(albi_insights["anomalies"])
            }
        )
```

### ASI Realtime Integration:

```python
# In asi_realtime_engine.py
from agent_telemetry import send_agent_telemetry
import time

def analyze_system():
    start = time.time()
    
    # ... perform analysis ...
    
    duration_ms = (time.time() - start) * 1000
    
    send_agent_telemetry(
        agent_name="ASI",
        operation="system_analysis",
        duration_ms=duration_ms,
        success=True,
        metadata={"health_score": 93.35}
    )
```

---

## 📚 References

- **Alba API**: `alba_api_server.py`
- **Albi Core**: `albi_core.py`
- **JONA Character**: `jona_character_v2.py`
- **ASI Realtime**: `asi_realtime_engine.py`
- **AGIEM Core**: `agiem_core.py`
- **Cycle Engine**: `cycle_engine.py`

---

## 🎯 Summary

**Agent Telemetry** është ura që:

1. ✅ **Lidh** agjentët (AGIEM/ASI/Blerina) me Trinity (Alba/Albi/Jona)
2. ✅ **Dërgon** metrikat në të tre shërbimet njëherësh
3. ✅ **Merr** status dhe health nga ASI orchestrator
4. ✅ **Ekzekuton** komanda Trinity në mënyrë health-gated
5. ✅ **Monitoron** vazhdimisht me `telemetry_loop()`
6. ✅ **Ekspozon** metrika për Prometheus/Grafana

**Filozofia:**
- **Pull model**: Agjentët lexojnë statusin nga ASI
- **Push model**: Agjentët dërgojnë metrikat në Trinity
- **Health-gated**: Asnjë veprim kritik nuk ekzekutohet pa kontroll shëndeti
- **Graceful degradation**: Sistemi vazhdon edhe nëse disa endpoints dështojnë

---

**Happy Telemetry! 📡✨**

