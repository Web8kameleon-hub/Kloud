# 🔁 Research Data Ecosystem - Cycle Engine Integration

## Overview

The Research Data Ecosystem is now fully integrated with the **kloud Cycle Engine** for intelligent, automated document generation and knowledge management.

## What is the Cycle Engine?

The Cycle Engine creates, manages, and executes intelligent work cycles (kontrata pune inteligjente) that automatically:
- Collect research data from multiple sources
- Generate documents and reports on schedules
- Detect knowledge gaps and auto-create cycles to fill them
- Monitor data streams in real-time
- Ensure ethical alignment through JONA oversight

## Cycle Types

### 1. INTERVAL Cycles (Periodic)
Execute at regular intervals (hourly, daily, weekly, monthly)

**Examples:**
- PubMed literature monitoring (daily)
- ArXiv preprint scanning (daily)
- Weather data collection (hourly)
- European Open Data harvesting (weekly)
- Comprehensive research reports (monthly)

### 2. EVENT Cycles (Triggered)
Execute when specific events occur

**Examples:**
- New breakthrough paper published
- Anomaly detected in research data
- Knowledge gap identified
- Critical alert threshold reached

### 3. STREAM Cycles (Continuous)
Run continuously without stopping

**Examples:**
- Real-time news monitoring (NewsAPI + Guardian)
- Live weather data streaming
- Continuous social media analysis

### 4. BATCH Cycles (One-Time)
Execute once and complete

**Examples:**
- Quarterly research summary
- Annual report generation
- One-time data migration

### 5. GAP-TRIGGERED Cycles (Born-Concepts)
Automatically created when knowledge gaps detected

**Examples:**
- Missing research area identified by ALBI
- Low confidence in knowledge base (<70%)
- Concept not found in knowledge graph

## Predefined Research Cycles

| Cycle Name | Domain | Source | Agent | Frequency | Purpose |
|------------|--------|--------|-------|-----------|---------|
| `pubmed_daily` | Biomedical Research | PubMed | ALBA | Every 24h | Literature ingestion |
| `arxiv_daily` | Scientific Research | ArXiv | ALBA | Every 24h | Preprint monitoring |
| `weather_hourly` | Environmental Data | OpenWeatherMap | ALBA | Every 1h | Weather tracking |
| `news_realtime` | Current Events | NewsAPI + Guardian | ALBA | Continuous | News stream |
| `european_data_weekly` | Open Data | European Portals | ALBA | Every 7 days | Data harvesting |
| `research_report_monthly` | Documentation | All Sources | ALBI | Every 30 days | Report generation |
| `knowledge_gap_detection` | Meta Research | ALBI Insights | ALBI | Every 2 days | Gap analysis |

## Storage Targets

Each cycle can store data to multiple targets:

- **PostgreSQL**: Structured research data (papers, citations)
- **MongoDB**: Documents and generated reports
- **Elasticsearch**: Full-text searchable content
- **Weaviate**: Vector embeddings for semantic search
- **Neo4j**: Knowledge graphs and relationships
- **Local Filesystem**: Generated documents and reports

## Alignment Policies

Cycles respect ethical and quality alignment policies:

| Policy | Description | Use Case |
|--------|-------------|----------|
| `STRICT` | Any error stops the cycle | Medical research, critical data |
| `MODERATE` | Warnings logged, cycle continues | General research, news |
| `PERMISSIVE` | Only logs events | Environmental monitoring |
| `ETHICAL_GUARD` | JONA reviews and approves | Sensitive topics, human subjects |

## Usage Guide

### 1. Initialize Cycle Engine

```python
from cycle_engine import CycleEngine
from pathlib import Path

cycle_engine = CycleEngine(data_root=Path.cwd() / "data" / "cycles")
```

### 2. Create Predefined Research Cycles

```python
# Create all 7 predefined research cycles
created_ids = create_research_cycles()
print(f"✓ Created {len(created_ids)} cycles")
```

### 3. Create Custom Document Generation Cycle

```python
doc_cycle_id = create_document_generation_cycle(
    title="Weekly Biomedical Research Summary",
    sources=["pubmed", "arxiv", "european_data"],
    output_format="markdown",
    frequency="weekly"
)
```

### 4. Create Event-Triggered Cycle

```python
event_cycle_id = create_event_cycle(
    event_trigger="new_breakthrough_paper",
    task="immediate_analysis",
    domain="biomedical_research"
)
```

### 5. Auto-Detect Knowledge Gaps

```python
# System automatically creates cycles to fill gaps
auto_cycles = auto_detect_and_create_cycles(
    trigger="low_confidence",
    max_cycles=5
)
```

### 6. Monitor Cycles

```python
# Display dashboard
display_cycles_dashboard()

# Get specific cycle status
status = get_cycle_status(cycle_id)

# Get overall metrics
metrics = get_engine_metrics()
```

### 7. Start a Cycle (Async)

```python
import asyncio

# Start a cycle
execution = await cycle_engine.start_cycle(cycle_id)

# Stop a cycle
cycle_engine.stop_cycle(cycle_id)
```

## Agent Responsibilities

### ALBA (Data Collection)
- Monitors PubMed, ArXiv, Weather, News APIs
- Collects European Open Data
- Streams real-time data
- Stores data to multiple databases

### ALBI (Analysis & Documents)
- Generates monthly reports
- Analyzes knowledge gaps
- Creates document summaries
- Manages knowledge graph

### JONA (Oversight)
- Reviews ethical alignment
- Approves sensitive research
- Blocks problematic cycles
- Ensures human values

## Telemetry Integration

All cycle operations are tracked via the Trinity telemetry system:

```python
# Every cycle event sends telemetry
telemetry_router.send_all({
    "event": "cycle_created",
    "cycle_id": cycle.cycle_id,
    "domain": "biomedical_research",
    "timestamp": datetime.now().isoformat()
})
```

**Monitored Events:**
- Cycle creation
- Cycle execution start/stop
- Document generation
- Knowledge gap detection
- Alignment violations
- Storage operations

## File Structure

```
data/
└── cycles/
    ├── pubmed_daily/
    │   ├── executions/
    │   └── outputs/
    ├── arxiv_daily/
    │   ├── executions/
    │   └── outputs/
    ├── research_report_monthly/
    │   ├── executions/
    │   └── outputs/
    │       ├── 2025-01-report.md
    │       ├── 2025-02-report.md
    │       └── 2025-03-report.md
    └── knowledge_gap_detection/
        ├── executions/
        └── detected_gaps.json
```

## Dashboard Example

```
================================================================================
📊 RESEARCH DATA CYCLES DASHBOARD
================================================================================

🔹 BIOMEDICAL RESEARCH
--------------------------------------------------------------------------------
  ▶️ cycle_a3f5b891
     Task: literature_ingest (every 1 days)
     Source: pubmed → Agent: ALBA

  ⏸️ cycle_b8e2c4d7
     Task: gap_analysis (every 2 days)
     Source: albi_insights → Agent: ALBI

🔹 SCIENTIFIC RESEARCH
--------------------------------------------------------------------------------
  ▶️ cycle_c1d9f3a2
     Task: preprint_monitor (every 1 days)
     Source: arxiv → Agent: ALBA

================================================================================
📈 OVERALL METRICS
--------------------------------------------------------------------------------
  Total Cycles: 7
  Active: 3
  Pending: 2
  Completed: 2
================================================================================
```

## Integration with Research Ecosystem

The cycle integration connects to all existing research components:

1. **PubMed Integration** → `pubmed_daily` cycle
2. **ArXiv Integration** → `arxiv_daily` cycle
3. **Weather API** → `weather_hourly` cycle
4. **News APIs** → `news_realtime` cycle
5. **European Open Data** → `european_data_weekly` cycle
6. **Database Storage** → All cycles use multi-storage
7. **Telemetry System** → All events tracked
8. **Prometheus Metrics** → Cycle execution metrics
9. **Grafana Dashboards** → Visual monitoring

## Benefits

✅ **Automation**: No manual data collection needed  
✅ **Intelligence**: Auto-detects gaps and creates cycles  
✅ **Alignment**: JONA ensures ethical research  
✅ **Multi-Storage**: Data replicated to multiple systems  
✅ **Real-Time**: Stream cycles for live monitoring  
✅ **Scheduled**: Interval cycles for periodic tasks  
✅ **Event-Driven**: Responds to research breakthroughs  
✅ **Telemetry**: Full visibility into operations  
✅ **Scalable**: Can create thousands of cycles  
✅ **Flexible**: Custom cycles for any use case  

## Example Workflows

### Weekly Research Digest

```python
# 1. Create digest cycle
digest_cycle = create_document_generation_cycle(
    title="AI Research Weekly Digest",
    sources=["pubmed", "arxiv"],
    frequency="weekly"
)

# 2. Start cycle
await cycle_engine.start_cycle(digest_cycle)

# 3. Check generated document
# File saved to: data/cycles/document_generation/outputs/AI-Research-Weekly-Digest.md
```

### Real-Time Breakthrough Detection

```python
# 1. Create event cycle
breakthrough_cycle = create_event_cycle(
    event_trigger="arxiv_score>9.5",
    task="immediate_deep_analysis"
)

# 2. Cycle automatically runs when high-score paper appears
# 3. JONA reviews for ethical implications
# 4. Document generated and stored
```

### Knowledge Gap Filling

```python
# 1. ALBI detects gap in knowledge graph
# "Missing concept: quantum_consciousness_interface"

# 2. System auto-creates gap cycle
auto_cycles = auto_detect_and_create_cycles(trigger="concept_gap")

# 3. Cycle searches PubMed, ArXiv for relevant papers
# 4. Papers analyzed and added to knowledge graph
# 5. Gap filled, concept born
```

## Next Steps

1. **Run the Notebook**: Execute `Research_Data_Ecosystem_Integration.ipynb`
2. **Create Cycles**: Run `create_research_cycles()`
3. **Monitor Dashboard**: Run `display_cycles_dashboard()`
4. **Start Cycles**: Use `await cycle_engine.start_cycle(cycle_id)`
5. **Check Outputs**: View generated documents in `data/cycles/`
6. **Review Telemetry**: Check Alba/Albi/Jona dashboards

## Support

- **Documentation**: See `cycle_engine.py` for full API
- **Examples**: See `CYCLE_ENGINE_DEMO.py` for demos
- **Notebook**: See cells 28-33 for integration code
- **Telemetry**: Check `agent_telemetry.py` for tracking

---

**Integration Status**: ✅ **COMPLETE**  
**Version**: 1.0.0  
**Last Updated**: December 15, 2025  
**Author**: kloud Team

