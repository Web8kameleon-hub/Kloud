# Kloud Cloud - Labs, Engines & Agents Reference
> Complete architectural documentation of all laboratories, engines, and agents

## 🤖 AGENTS ARCHITECTURE

### Trinity Core Agents

| Agent | Port | Role | Responsibility |
|-------|------|------|----------------|
| **ALBA** | 5050 | Data Collection | Network infrastructure, data gathering from registered sources |
| **ALBI** | 6060 | Neural Processing | Intelligence enhancement, creativity, pattern recognition |
| **JONA** | 7070 | Safety & Ethics | System harmony, violation detection, ethical guardrails |

### Extended Intelligence Agents

| Agent | Port | Role | Description |
|-------|------|------|-------------|
| **BLERINA** | - | Document Intelligence | Bits-Labor-Enhanced-Intelligence-Recreator-Array |
| **ASI** | 9094 | Core Engine | Artificial Super Intelligence realtime engine |
| **AGIEM** | - | Agent Manager | Agent Intelligence Manager, orchestrates all agents |
| **SAAS** | 9999 | Services | Service orchestrator for cloud infrastructure |

---

## 🔬 NEURO ENGINES (`apps/api/neuro/`)

### 1. BrainSync Engine
**File:** `brainsync_engine.py`
**Purpose:** EEG → Audio synthesis for brainwave entrainment

```python
class BrainSyncEngine:
    modes = ["relax", "focus", "sleep", "motivation", "creativity", "recovery"]
    
    # Brainwave targets:
    # - relax: 8.0 Hz (alpha)
    # - focus: 14.0 Hz (high alpha/low beta)
    # - sleep: 2.0 Hz (delta)
    # - motivation: 12.0 Hz (strong alpha)
    # - creativity: 10.0 Hz (alpha-theta border)
    # - recovery: 7.83 Hz (Schumann resonance)
```

### 2. Energy Engine
**File:** `energy_engine.py`
**Purpose:** Voice/audio analysis for energy and emotion detection

- Pitch & dominant frequency analysis
- Vocal tension (jitter + shimmer)
- Spectral centroid → brightness/mood
- Energy Score (0-100)
- Emotion mapping: energized, calm, stressed

### 3. HPS Engine (Harmonic Profile Scanner)
**File:** `hps_engine.py`
**Purpose:** Audio harmonic fingerprinting

- Key detection (tonality)
- Tempo/BPM extraction
- Harmonic fingerprint
- Emotional tone (valence + arousal)
- Personality archetype mapping

### 4. Moodboard Engine
**File:** `moodboard_engine.py`
**Purpose:** Visual mood generation from audio profiles

### 5. YouTube Insight Engine
**File:** `youtube_insight_engine.py`
**Purpose:** Video analysis and insight extraction

### 6. Audio to MIDI
**File:** `audio_to_midi.py`
**Purpose:** Audio signal to MIDI conversion

---

## 🧪 RESEARCH LABS (`research/`)

### 1. Research Proposal Lab
**File:** `research_proposal_lab.py`
**Purpose:** Transforms telemetry and generated APIs into proposal-ready artifacts

```python
class ResearchProposalLab:
    """Transforms telemetry and generated APIs into proposal-ready artefacts."""
    
    def build_brief(context) -> ResearchBrief
    def persist_packet(proposal, attachments) -> ProposalPacket
```

### 2. Self-Generating API Lab
**File:** `self_generating_api.py`
**Purpose:** Self-generating API laboratory utilities

### 3. Sandbox Core
**File:** `sandbox_core.py`
**Purpose:** Security container and execution sandbox

### 4. Real AGI System
**File:** `real_agi_system.py`
**Purpose:** Artificial General Intelligence research module

### 5. YouTube Title Analysis
**File:** `youtube_title_analysis.py`
**Purpose:** NLP analysis of video titles for insights

---

## 📦 MODULES (`apps/api/modules/`)

### Python Modules

| Module | Purpose |
|--------|---------|
| `biometric_tracker.py` | Biometric data tracking and analysis |
| `coaching_engine.py` | AI coaching and guidance system |
| `world_learner.py` | Global knowledge acquisition module |

### TypeScript Neural Modules (`app/modules/`)

| Module | Purpose |
|--------|---------|
| `alpha_theta_beta.ts` | Brainwave frequency management |
| `auto_adapt_trainer.ts` | Self-adapting training system |
| `NeuralRebalanceModule.ts` | Neural state rebalancing |

---

## 🔧 SERVICES (`services/`)

### ASI System
**File:** `services/asi_system.py`
**Purpose:** Core ASI service orchestration

### Concept Gap Service
**Directory:** `services/concept_gap/`
**Purpose:** Gap detection in concept understanding

---

## 🎯 CORE ENGINES (Root Level)

| Engine | File | Purpose |
|--------|------|---------|
| Cycle Engine | `cycle_engine.py` | Main reproduction/cycle system |
| ASI Realtime | `asi_realtime_engine.py` | Real-time ASI processing |
| AGIEM Core | `agiem_core.py` | Agent intelligence management |
| ASI Core | `asi_core.py` | Core ASI functionality |
| ALBA Core | `alba_core.py` | Data collection core |
| ALBI Core | `albi_core.py` | Neural processing core |

---

## 📊 INFRASTRUCTURE

### Observability Stack
- **Prometheus** - Metrics collection
- **VictoriaMetrics** - Long-term storage
- **Loki** - Log aggregation
- **Grafana** - Visualization
- **Jaeger** - Distributed tracing

### Data Sources (External APIs)
- YouTube Data API
- arXiv API (research papers)
- GitHub API
- News APIs (Reuters, AP)
- Weather APIs
- Financial APIs
- Social Media APIs

---

## 🔌 PORT REGISTRY

| Service | Port |
|---------|------|
| ALBA Agent | 5050 |
| ALBI Agent | 6060 |
| JONA Agent | 7070 |
| Web Frontend | 3000 |
| Main API | 8000 |
| ASI Engine | 9094 |
| SAAS Orchestrator | 9999 |
| Grafana | 3001 |
| Prometheus | 9090 |
| Loki | 3100 |

---

## 📁 FILE STRUCTURE OVERVIEW

```
Kloud-cloud/
├── apps/
│   ├── api/
│   │   ├── modules/          # Python modules
│   │   └── neuro/            # Neuro engines
│   └── web/                  # Next.js frontend
├── research/                 # Research labs
├── services/                 # Microservices
├── *_core.py                 # Core agent files
├── *_engine.py               # Engine files
└── docker-compose*.yml       # Deployment configs
```

---

## ✅ ARCHITECTURE PRINCIPLES

1. **Single Responsibility** - Each agent/engine has one focused task
2. **Scalability** - All components are horizontally scalable
3. **Registered Sources** - All data sources are registered and approved
4. **Open Source First** - Priority on open/public data sources
5. **Real-time Processing** - Sub-second response times
6. **Ethical AI** - JONA ensures ethical guardrails

---

*Last Updated: December 2025*
*Kloud Cloud Platform v2.1.0*

