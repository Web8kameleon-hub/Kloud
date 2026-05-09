# Hybrid Protocol Sovereign System

> **"Listen First, Enforce After Maturity"**

A multi-protocol intake system with maturity-gated ML overlay and protocol sovereignty enforcement.

## 🏗️ Architecture

```
INPUT → RAW → NORMALIZED → TEST → READY/FAIL → MATURE → ML OVERLAY → ENFORCEMENT
              ↓                      ↓
           FAILED                 IMMATURE
```

## 📁 Structure

```
hybrid_saas_platform/
├── core/
│   ├── canonical_table.py    # Append-only infinite Excel engine
│   ├── parser.py             # Multi-protocol input parser
│   └── validator.py          # Security & schema validation
├── labs/
│   └── lab_executor.py       # Test execution engine
├── agents/
│   └── agent_registry.py     # Intelligent task orchestration
├── ml_overlay/
│   └── ml_manager.py         # ML models (only for MATURE rows)
├── enforcement/
│   └── enforcement_manager.py # Protocol sovereignty layer
├── ui/
│   └── excel_template.py     # Excel visualization
├── tests/
│   └── test_pipeline.py      # Unit & integration tests
├── config.py                 # System configuration
├── run_pipeline.py           # Main orchestrator
└── requirements.txt          # Dependencies
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline demo
python run_pipeline.py

# Run tests
python -m pytest tests/ -v
```

## 📊 Key Concepts

### Maturity States
| State | Description | ML Eligible |
|-------|-------------|-------------|
| IMMATURE | Initial state, validation pending | ❌ |
| MATURING | Security & validation passed | ❌ |
| MATURE | All conditions met, ready for ML | ✅ |

### Maturity Gate Rule
```
MATURE = Security=PASS AND Validation=PASS AND Artifacts!=NULL AND Status=READY
```

### Pipeline Steps

1. **Intake** - Parse input from any protocol (REST, GraphQL, gRPC, Webhook, File)
2. **Validation** - Security & schema checks
3. **Labs/Agents** - Execute tests, generate artifacts
4. **ML Overlay** - Apply ML only on MATURE rows
5. **Enforcement** - Protocol sovereignty for MATURE rows

## 📥 Example Usage

```python
from run_pipeline import run_pipeline, PipelineConfig

# Input data
input_payload = {
    "cycle": 1,
    "layer": "L1",
    "variant": "A",
    "input_type": "grain",
    "data": {"weight_kg": 100}
}

# Run pipeline
config = PipelineConfig(verbose=True)
result = run_pipeline(input_payload, "REST", config)

print(f"Success: {result['success']}")
print(f"Status: {result['final_status']}")
print(f"Maturity: {result['final_maturity']}")
print(f"ML Applied: {result['ml_applied']}")
```

## 🔧 Configuration

Environment variables:
- `HYBRID_ENV` - Environment (development/staging/production)
- `SECURITY_METHOD` - Default security method (NONE/JWT/API_KEY/OAuth)
- `ML_ENABLED` - Enable ML overlay (true/false)
- `ENFORCEMENT_MODE` - Enforcement mode (PASSIVE/ADVISORY/STRICT)

## 📈 ML Models

| Model | Output | Description |
|-------|--------|-------------|
| Classifier | `ml_score` | Row quality/priority score |
| Agent Recommender | `ml_suggested_agent` | Best agent for similar rows |
| Lab Recommender | `ml_suggested_lab` | Best lab for processing |
| Anomaly Detector | `ml_anomaly_prob` | Anomaly probability |

## 🛡️ Enforcement Modes

| Mode | Behavior |
|------|----------|
| PASSIVE | Observe and log only |
| ADVISORY | Warn but accept |
| STRICT | Reject non-compliant |

## 📝 License

Proprietary - Kloud Cloud

