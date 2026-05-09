# Kloud Production Services Inventory

**Last Updated:** December 11, 2025  
**Platform Version:** 1.0.0  
**Status:** Production-Ready SaaS Platform

---

## 🎯 Service Architecture Overview

Kloud operates as a **microservices-based AI platform** with the following layers:

1. **Agent Services** - 7 specialized AI agents running on dedicated ports
2. **API Gateway** - Unified FastAPI backend exposing all functionality
3. **Frontend** - Next.js web application
4. **Orchestration Layer** - System monitoring, scheduling, and reporting
5. **Infrastructure** - Monitoring stack (Prometheus, Grafana, Loki, Tempo, VictoriaMetrics)

---

## 🤖 Agent Services (Microservices)

### 1. Alba (Port 5555)
**File:** `alba_api_server.py`, `alba_core.py`, `alba_feeder_service.py`, `alba_frame_generator.py`, `alba_service_5555.py`  
**Purpose:** Content generation, creative workflows, frame-by-frame animation  
**Dependencies:** FastAPI, async task queue  
**Health Check:** `GET http://localhost:5555/health`

### 2. Albi (Port 6666)
**File:** `albi_core.py`, `albi_service_6666.py`  
**Purpose:** Data processing, analytics, business intelligence  
**Dependencies:** FastAPI, pandas, numpy  
**Health Check:** `GET http://localhost:6666/health`

### 3. Jona (Port 7777)
**File:** `jona_service_7777.py`  
**Purpose:** User interaction, conversational AI, natural language understanding  
**Dependencies:** FastAPI, NLP models  
**Health Check:** `GET http://localhost:7777/health`

### 4. ASI (Artificial Superintelligence)
**File:** `asi_core.py`, `asi_realtime_engine.py`  
**Purpose:** Real-time cognitive processing, pattern recognition, decision-making  
**Dependencies:** FastAPI, real-time event loop, signal processing  
**Logs:** `asi_logs.json`

### 5. AGIEM (Advanced General Intelligence Engine Module)
**File:** `agiem_core.py`  
**Purpose:** General-purpose AI reasoning, multi-modal learning  
**Dependencies:** FastAPI, machine learning models

### 6. Blerina (Content Reformatter)
**File:** `blerina_reformatter.py`  
**Purpose:** Text transformation, content restructuring, format conversion  
**Dependencies:** FastAPI, text processing libraries

### 7. Master Orchestrator (Port 9999)
**File:** `master.py`  
**Purpose:** Central coordination of all agents, workflow management  
**Dependencies:** FastAPI, inter-service communication  
**Health Check:** `GET http://localhost:9999/health`

---

## 🌐 API Gateway (Primary Production Service)

### Main API Service
**Location:** `apps/api/main.py` (3,219 lines)  
**Port:** 8000 (default)  
**Framework:** FastAPI  
**Description:** Unified API gateway exposing all Kloud functionality

**Key Modules:**
- **Brain Router** (`/brain/*`)
  - YouTube insight generation
  - Energy state analysis
  - Moodboard generation
  - Harmonic Personality Scanning (HPS)
  - BrainSync music generation
  - Audio-to-MIDI conversion
  
- **ASI Trinity Metrics** (`/asi/*`)
  - Real-time cognitive metrics
  - Trinity analysis (thought, emotion, intuition)
  
- **Alba/Albi Routes**
  - Content generation endpoints
  - Analytics endpoints
  
- **Mesh Networking** (`/mesh/*`)
  - Distributed signal monitoring
  - Telemetry collection
  - Alert management
  - Security services

**Internal Modules:**
- `apps/api/neuro/` - Neural processing engines (5 engines)
- `apps/api/integrations/` - External API integrations (YouTube, etc.)
- `apps/api/mesh/` - Mesh networking services (8 modules)
- `apps/api/billing/` - Stripe payment integration

---

## 🎨 Frontend Application

### Next.js Web App
**Location:** `apps/web/`  
**Port:** 3000 (default)  
**Framework:** Next.js 15.5.4, React 18  
**Modules:** 14 total (13 production, 1 demo)

**Production Modules:**
1. Agent Control Panel
2. Analytics Dashboard
3. API Playground
4. Audit & Compliance
5. BrainSync Studio
6. Content Generator
7. Economy Dashboard
8. Metrics Dashboard
9. Neural Control
10. Real-time Monitor
11. Reporting Dashboard (Excel-style)
12. Signal Generator
13. System Status

---

## 🔧 Orchestration Layer

### System Orchestrator (Port 5555)
**Location:** `backend/system/smart_orchestrator.py` (381 lines)  
**Purpose:** Real-time system monitoring, auto-healing, admin dashboard  
**Features:**
- Live event timeline
- Module health scanning
- PDF report generation
- Email alerting
- NeuroTrigger integration
- NeuroReset API (`/neuro/*`)

**Dependencies:**
- `backend/system/neuro_trigger.py` - Event-driven automation
- `backend/system/exporter.py` - PDF report generation
- `backend/system/email_reporter.py` - SMTP email delivery

### Daily Scheduler
**Location:** `backend/system/daily_scheduler.py`  
**Purpose:** Automated daily reports at 08:00 Europe/Berlin  
**Deployment:** Systemd service (`kloud_daily.service`)

### Additional System Tools
- `backend/system/auto_monitor.py` - Autonomous monitoring agent
- `backend/system/smart_scanner.py` - Service health scanner
- `backend/system/neuro_reset.py` - System reset/recovery API
- `backend/system/web_controller.py` - Web-based control interface

---

## 🛠️ Supporting Utilities

### Production Utilities (Root Directory)
- **`usage_tracker.py`** - API usage metering and quota management
- **`tracing.py`** - OpenTelemetry distributed tracing
- **`billing_plans.py`** - Subscription tier definitions
- **`localization.py`** - Multi-language support (EN, AL, TR, IT, ES, DE, FR)
- **`api_key_middleware.py`** - API authentication middleware
- **`API_CONFIG.py`** - Global API configuration

### Additional Services
- **`economy_api_server.py`** - Virtual economy management
- **`economy_layer.py`** - Economic simulation layer
- **`distributed_pulse_balancer.py`** - Load balancing for distributed nodes
- **`mesh_cluster_startup.py`** - Mesh network initialization
- **`mesh_hq_receiver.py`** - Central mesh telemetry receiver
- **`metrics_realtime.py`** - Real-time metrics collection
- **`slack_integration_service.py`** - Slack notifications
- **`kloud_sdk.py`** - Python SDK for Kloud API
- **`convert_openapi.py`** - OpenAPI schema converter
- **`favicon_fixer.py`** - Static asset management

---

## 📊 Monitoring & Observability Stack

### Prometheus
- **Purpose:** Metrics collection and storage
- **Port:** 9090
- **Metrics:** 1,244 time series (healthy TSDB)
- **Config:** `ops/prometheus.yml`

### VictoriaMetrics
- **Purpose:** Long-term metrics storage (Prometheus-compatible)
- **Port:** 8428
- **Retention:** Configurable long-term storage

### Grafana
- **Purpose:** Metrics visualization and dashboards
- **Port:** 3001
- **Datasources:** Prometheus, VictoriaMetrics, Loki, Tempo
- **Config:** `ops/grafana/provisioning/`

### Loki
- **Purpose:** Log aggregation and querying
- **Port:** 3100
- **Config:** `ops/loki-config.yml`

### Tempo
- **Purpose:** Distributed tracing backend
- **Port:** 3200
- **Config:** `ops/tempo-config.yml`

### Deployment
- **Method:** Docker Compose
- **Config:** `docker-compose.yml`, `ops/docker-compose.monitoring.yml`

---

## 🗄️ Database & Cache

### PostgreSQL 16
- **Purpose:** Primary relational database
- **Port:** 5432
- **Schema:** User accounts, subscriptions, agent data, audit logs

### Redis 7
- **Purpose:** Caching, session storage, task queue (Celery)
- **Port:** 6379
- **Persistence:** RDB snapshots

---

## 🔐 Security & Authentication

- **API Keys:** Middleware-based validation (`api_key_middleware.py`)
- **JWT Tokens:** python-jose with cryptography
- **Password Hashing:** bcrypt via passlib
- **CORS:** Configurable FastAPI middleware
- **Rate Limiting:** Redis-backed rate limiter

---

## 💳 Billing & Payments

- **Provider:** Stripe 7.8.0+
- **Module:** `apps/api/billing/stripe_integration.py`
- **Features:**
  - Customer creation
  - Subscription management
  - Usage-based billing
  - Payment intent handling
- **Plans:** Defined in `billing_plans.py`

---

## 📦 Deployment

### Docker Containers
- **API Service:** `Dockerfile.api`
- **Worker Service:** `Dockerfile.worker`
- **Orchestration:** `docker-compose.yml`, `docker-compose.python.yml`, `docker-compose.producer-manager.yml`

### Scripts
- `docker-run.ps1` - Windows PowerShell deployment script
- `init_industrial.ps1` - Industrial demo initialization (archived)

---

## 🧪 Testing

### Test Suite Location: `tests/`
- **Unit Tests:** `tests/unit/` (13 files)
  - `test_alba_albi_jona.py`
  - `test_backend.py`
  - `test_blerina_reformatter.py`
  - `test_config_sync.py`
  - `test_fastapi_integration.py`
  - `test_import_export.py`
  - `test_integration.py`
  - `test_minimal.py`
  - `test_multiple_topics.py`
  - `test_news_api.py`
  - `test_traces.py`
  - `test_audit_tracing_alerting.py`

- **Integration Tests:**
  - `test_comprehensive_integration.py`
  - `test_manager_sync.py`
  - `test_manager_sync_token.py`

---

## 🚫 Archived/Deprecated Services

**Location:** `/archive/`

### Old Services
- `kloud_*.py` (8 files) - Legacy kloud modules
- `saas_api.py` - Old Flask-based SaaS API
- `saas_services_orchestrator.py` - Deprecated orchestrator
- `industrial_dashboard_demo.py` - Demo application
- `industrial_data.py` - Demo data generator
- `main_minimal.py` - Lightweight API variant

### Old Frontends
- `archive/frontends/kloud-web-nextjs/` - Previous Next.js app
- `archive/frontends/kloud-frontend-nextjs/` - Earlier version

### Launchers
- 6 archived launcher scripts in `archive/launchers/`

---

## 🔬 Research & Experimental Code

**Location:** `/research/`

- **Generated APIs:** `generated_apis/` (29 auto-generated service prototypes)
- **Research Proposals:** Various experimental modules
- **Prototypes:** Signal generation, peer nodes, sandbox environments

**Note:** This code is **NOT** in production and is used for R&D purposes only.

---

## 📋 Runtime Requirements

### Python Environment
- **Version:** Python 3.13+
- **Package Manager:** pip (pyproject.toml)
- **Key Dependencies:**
  - FastAPI 0.104.1+
  - Uvicorn 0.24.0+ (with standard extras)
  - SQLAlchemy 2.0.23+ (async support)
  - Pydantic 2.5.0+ (with pydantic-settings)
  - Stripe 7.8.0+
  - NumPy, SciPy, Librosa, MNE (scientific computing)
  - OpenTelemetry (observability)
  - Celery 5.3.4+ (task queue)

### Node.js Environment
- **Version:** Node.js 18.0.0+
- **Package Manager:** npm (workspaces)
- **Key Dependencies:**
  - Next.js 15.5.4
  - React 18.2.0
  - TypeScript 5.0.0+
  - Tailwind CSS 3.4.0+

### Infrastructure
- **PostgreSQL:** 16+
- **Redis:** 7+
- **Docker:** 20.10+ with Docker Compose
- **Operating System:** Linux (production), Windows (development via WSL/native)

---

## 📞 Service Communication

### Inter-Service Communication
- **Protocol:** HTTP/REST (internal services), WebSocket (real-time features)
- **Service Discovery:** Hardcoded ports (development), Docker DNS (production)
- **Message Format:** JSON, CBOR (lightweight telemetry), MessagePack

### External APIs
- **YouTube API:** OAuth2 + API key
- **Stripe API:** Secret key authentication
- **Slack API:** Webhook URLs

---

## 🎯 Production Checklist

### Pre-Deployment
- [ ] Lock dependency versions (requirements.txt, package.json)
- [ ] Define OpenAPI contracts for all 7 agents
- [ ] Configure environment variables (.env.production)
- [ ] Set up PostgreSQL with proper schema migrations
- [ ] Configure Redis for persistence
- [ ] Set up SMTP for email reporting
- [ ] Configure Stripe webhook endpoints

### Monitoring Setup
- [ ] Deploy Prometheus scrape targets
- [ ] Import Grafana dashboards
- [ ] Configure Loki log sources
- [ ] Set up Tempo trace collectors
- [ ] Configure alerting rules

### Security Hardening
- [ ] Rotate API keys
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up rate limiting
- [ ] Enable audit logging

### Performance Optimization
- [ ] Enable Redis caching
- [ ] Configure connection pooling (PostgreSQL)
- [ ] Set up CDN for static assets
- [ ] Optimize Docker images
- [ ] Configure horizontal scaling (Kubernetes/Docker Swarm)

---

## 📈 Service Health Endpoints

| Service | Port | Health Check |
|---------|------|--------------|
| Alba | 5555 | `GET /health` |
| Albi | 6666 | `GET /health` |
| Jona | 7777 | `GET /health` |
| Master Orchestrator | 9999 | `GET /health` |
| Main API | 8000 | `GET /health` |
| Smart Orchestrator | 5555 | `GET /` (dashboard) |
| Prometheus | 9090 | `GET /-/healthy` |
| Grafana | 3001 | `GET /api/health` |
| Loki | 3100 | `GET /ready` |
| Tempo | 3200 | `GET /ready` |

---

## 📝 Documentation

- **API Documentation:** `API_DOCS.md` (comprehensive API guide)
- **Architecture Baseline:** `KLOUD_ARCHITECTURE_BASELINE_2025.md`
- **Metrics Monitoring:** `metrics_monitoring.md`
- **Integration Report:** `INTEGRATION_COMPLETE_REPORT.md`
- **Optimization Summary:** `OPTIMIZATION_SUMMARY.md`

---

## 🚀 Quick Start Commands

### Development
```bash
# Backend
cd apps/api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd apps/web
npm run dev

# All services (Docker)
docker-compose up -d
```

### Production
```bash
# Deploy monitoring stack
docker-compose -f ops/docker-compose.monitoring.yml up -d

# Deploy application services
docker-compose -f docker-compose.yml up -d

# Start orchestrator
python backend/system/smart_orchestrator.py
```

---

**Document Version:** 1.0.0  
**Maintained By:** Kloud Engineering Team  
**Contact:** Ledjan Ahmati (LedjanAhmati/Kloud-cloud)

