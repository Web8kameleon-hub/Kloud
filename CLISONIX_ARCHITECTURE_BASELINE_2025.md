# 🏗️ KLOUD ARCHITECTURE BASELINE 2025
**Commercial SaaS Platform - Production Architecture Document**

---

## 📋 Executive Summary

**Document Purpose**: Authoritative architecture specification for the **Kloud SaaS commercial platform**, separating production-ready services from experimental research code.

**Platform Status**: Operational but requires stabilization through architectural cleanup and boundary enforcement.

**Prometheus TSDB Health** (as of Dec 2025):
- Series: 1,244 (healthy, no cardinality explosion)
- TSDB: Stable, compaction working
- Labels: Optimal distribution
- Monitoring stack: Production-grade ✅

**Critical Finding**: Architecture has grown **organically** with ~211 Python files, 13+ frontend modules, 7 core agents, and significant research/demo code intermingled with production services. This document establishes clear boundaries.

---

## 🎯 Kloud Platform Mission

**Kloud** is a commercial SaaS platform providing:
1. **Neural signal processing** (EEG, biofeedback, audio synthesis)
2. **AI-powered agent coordination** (Alba, Albi, Jona, ASI, AGIEM)
3. **Real-time monitoring & telemetry** (Prometheus, Grafana, distributed tracing)
4. **Multi-tenant SaaS delivery** with billing, authentication, and API access
5. **Industrial-grade data pipelines** (Airflow orchestration)

**NOT included in Kloud**: UltraWebThinking research platform, experimental AGI modules, prototype signal generators, demo launchers.

---

## 🏛️ Production Service Inventory

### Core Backend Services

#### 1. **Main API Service** (`apps/api/main.py`)
- **Port**: 8000
- **Role**: Central FastAPI gateway for all Kloud operations
- **Lines**: 3,219
- **Features**:
  - Health checks & system status
  - Authentication (JWT + API keys)
  - Billing integration (Stripe)
  - AI agent proxy endpoints
  - WebSocket support for real-time data
  - OpenAPI/Swagger documentation
- **Dependencies**: PostgreSQL, Redis, Alba/Albi/Jona agents
- **Status**: ✅ CORE PRODUCTION

#### 2. **AI Agent Trinity (Alba → Albi → Jona)**

##### ALBA - Adaptive Learning & Brain Analysis
- **Port**: 5555
- **Files**:
  - `alba_api_server.py` (FastAPI service)
  - `alba_core.py` (169 lines - data collection logic)
  - `alba_feeder_service.py` (data feeding pipeline)
  - `alba_frame_generator.py` (signal frame generation)
- **Role**: **Data Collector**
  - Ingests EEG signals, industrial sensor data
  - Real-time frame generation for neural processing
  - Feeds data to Albi for analysis
- **Database**: Shares PostgreSQL with main API
- **Status**: ✅ CORE PRODUCTION

##### ALBI - Advanced Learning & Brain Intelligence
- **Port**: 6666
- **Files**:
  - `albi_core.py` (154 lines - analytics engine)
  - FastAPI service integration
- **Role**: **Neural Processor**
  - Adaptive learning algorithms
  - Pattern recognition in neural signals
  - Sends processed insights to Jona
- **Database**: Shares PostgreSQL with main API
- **Status**: ✅ CORE PRODUCTION

##### JONA - Joint Oscillatory Neural Analysis
- **Port**: 7777
- **Files**:
  - `jona_service_7777.py` (267 lines - coordinator)
- **Role**: **Coordinator & Synthesizer**
  - Synthesizes Alba + Albi data
  - Generates neural audio (brain-to-sound conversion)
  - Orchestrates agent communication
  - Exports final results to API
- **Database**: Shares PostgreSQL with main API
- **Status**: ✅ CORE PRODUCTION

#### 3. **ASI - Artificial Superintelligence Core**
- **Port**: N/A (internal service)
- **Files**:
  - `asi_core.py` (258 lines)
  - `asi_realtime_engine.py` (realtime processing)
- **Role**: **System Intelligence Layer**
  - Mesh network coordination
  - Cross-agent optimization
  - Predictive scaling decisions
  - Telemetry aggregation
- **Status**: ✅ CORE PRODUCTION

#### 4. **AGIEM - AGI Evolution Module**
- **Port**: N/A (internal service)
- **Files**:
  - `agiem_core.py` (1,360 lines)
- **Role**: **Meta-Intelligence & Evolution**
  - Real-time AGI operations
  - System log analysis
  - Mesh reporting & health checks
  - Agent performance optimization
- **Status**: ✅ CORE PRODUCTION

#### 5. **Blerina - YouTube Integration**
- **Port**: N/A (utility service)
- **Files**:
  - `blerina_reformatter_ai.py` (253 lines)
- **Role**: **Content Analysis Utility**
  - YouTube API integration
  - Video metadata extraction
  - Neural insight generation from content
- **Status**: ✅ PRODUCTION UTILITY

### Orchestration & Coordination

#### Master Orchestrator
- **Port**: 9999
- **Files**:
  - `master.py` (orchestrator core)
  - `mesh_cluster_startup.py` (cluster initialization)
  - `mesh_hq_receiver.py` (event receiver)
- **Role**: **Service Coordinator**
  - Manages Alba/Albi/Jona lifecycle
  - Health checks & failover
  - Distributed pulse balancing
  - Mesh network event routing
- **Status**: ✅ CORE PRODUCTION

### Supporting Services

#### Backend Application (`backend/`)
- **Files**:
  - `backend/app.py` (Flask/FastAPI hybrid)
  - `backend/mesh/` (networking, security, telemetry)
  - `backend/neuro/` (neural engines: BrainSync, Energy, HPS, Moodboard, YouTubeInsight)
  - `backend/utils/` (scheduler, monitor, orchestrator)
- **Role**: Legacy backend services supporting main API
- **Status**: ✅ PRODUCTION BACKEND (requires consolidation with `apps/api/`)

#### Billing & Economy
- **Files**:
  - `billing_plans.py` (subscription tiers)
  - `stripe_integration.py` (payment processing)
  - `economy_api_server.py` (economy management)
- **Role**: **SaaS Monetization**
- **Status**: ✅ PRODUCTION BILLING

#### Authentication & Security
- **Files**:
  - `api_key_middleware.py` (API key validation)
  - `backend/middleware/security.py` (JWT, quotas)
- **Role**: **Security Layer**
- **Status**: ✅ PRODUCTION SECURITY

#### Slack Notifications
- **Port**: 8888
- **Files**: `slack_integration_service.py`
- **Role**: **Alert Notifications**
- **Status**: ✅ PRODUCTION UTILITY

#### Telemetry & Tracing
- **Files**:
  - `tracing.py` (OpenTelemetry integration)
  - `usage_tracker.py` (API usage metrics)
- **Role**: **Observability**
- **Status**: ✅ PRODUCTION MONITORING

---

## 🌐 Frontend Application (`apps/web/`)

### Framework
- **Technology**: Next.js 14+ (App Router)
- **Location**: `apps/web/`
- **Port**: 3000

### Production Modules (`apps/web/app/modules/`)

| Module | Path | Description | Status |
|--------|------|-------------|--------|
| **Curiosity Ocean** | `curiosity-ocean/` | API exploration interface | ✅ Production |
| **EEG Analysis** | `eeg-analysis/` | Neural signal visualization | ✅ Production |
| **Neural Synthesis** | `neural-synthesis/` | Audio synthesis from brain data | ✅ Production |
| **Neuroacoustic Converter** | `neuroacoustic-converter/` | Audio-to-neural conversion | ✅ Production |
| **Spectrum Analyzer** | `spectrum-analyzer/` | Frequency domain analysis | ✅ Production |
| **Neural Biofeedback** | `neural-biofeedback/` | Real-time biofeedback loops | ✅ Production |
| **Fitness Dashboard** | `fitness-dashboard/` | Health & training metrics | ✅ Production |
| **Reporting Dashboard** | `reporting-dashboard/` | Executive metrics (Excel-style) | ✅ Production |
| **Data Collection** | `data-collection/` | Data ingestion interface | ✅ Production |
| **Open WebUI** | `open-webui/` | Chat interface integration | ✅ Production |
| **Crypto Dashboard** | `crypto-dashboard/` | Cryptocurrency monitoring | ✅ Production |
| **Weather Dashboard** | `weather-dashboard/` | Weather data integration | ✅ Production |
| **Phone Monitor** | `phone-monitor/` | Mobile device monitoring | ✅ Production |
| **Industrial Dashboard** | `industrial-dashboard/` | System overview | ⚠️ Demo (needs review) |

**Total**: 14 modules (13 production + 1 demo)

---

## 🗄️ Infrastructure Services (Docker)

### Database Layer
- **PostgreSQL 16**: Primary RDBMS (shared by all agents + API)
- **Redis 7**: Caching & session storage
- **MinIO**: S3-compatible object storage

### Monitoring Stack (Production-Grade)
- **Prometheus**: Metrics collection (TSDB: 1,244 series, healthy)
- **VictoriaMetrics**: High-performance long-term metrics storage
- **Grafana**: Visualization dashboards
- **Loki**: Log aggregation
- **Tempo**: Distributed tracing
- **Alertmanager**: Alert routing & management

### Logging & Search
- **Elasticsearch**: Full-text log search
- **Kibana**: Log visualization
- **Filebeat**: Log shipping

**Docker Compose Files**:
- `docker-compose.yml` (primary)
- `docker-compose.python.yml` (Python services)
- `docker-compose.producer-manager.yml` (producer services)

**Status**: ✅ PRODUCTION INFRASTRUCTURE

---

## 📊 Data Pipeline (Airflow)

### DAG Inventory (`dags/`)
- `alba_eeg_pipeline.py` - EEG data processing
- `albi_analytics_pipeline.py` - Analytics orchestration
- `jona_synthesis_pipeline.py` - Audio synthesis pipeline
- `neural_mesh_coordinator.py` - Mesh coordination
- `system_health_monitor.py` - Health checks
- `telemetry_aggregator.py` - Metrics aggregation

**Status**: ✅ PRODUCTION PIPELINES

---

## 🔄 Service Dependencies & Data Flow

### Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                      KLOUD PLATFORM                          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               Frontend (Next.js - Port 3000)                    │
│   Modules: EEG, Neural Synthesis, Reporting, Fitness, etc.     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            Main API (FastAPI - Port 8000)                       │
│   Auth • Billing • Agent Proxy • WebSocket • Health            │
└──┬──────────────┬──────────────┬──────────────┬────────────────┘
   │              │              │              │
   │              ▼              ▼              ▼
   │    ┌───────────────┐ ┌────────────┐ ┌────────────┐
   │    │ ALBA (5555)   │ │ ALBI (6666)│ │ JONA (7777)│
   │    │ Data Collect  │ │ Analytics  │ │ Coordinator│
   │    └───────┬───────┘ └──────┬─────┘ └──────┬─────┘
   │            │                │              │
   │            └────────┬───────┴──────────────┘
   │                     ▼
   │            ┌─────────────────────┐
   │            │ Orchestrator (9999) │
   │            │  Mesh Coordinator   │
   │            └──────────┬──────────┘
   │                       │
   ▼                       ▼
┌─────────────────┐  ┌──────────────┐
│   PostgreSQL    │  │   ASI Core   │
│   (Shared DB)   │  │  + AGIEM     │
└─────────────────┘  └──────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Monitoring Stack                      │
│   Prometheus → VictoriaMetrics          │
│   Loki → Tempo → Grafana                │
└─────────────────────────────────────────┘
```

### Critical Dependencies

1. **Alba → Albi → Jona** (Sequential pipeline)
   - Alba collects raw data
   - Albi processes & analyzes
   - Jona synthesizes & coordinates
   - **Database**: Shared PostgreSQL (potential bottleneck)

2. **Main API → All Agents**
   - API acts as reverse proxy
   - Direct HTTP calls to agent ports
   - **Risk**: No circuit breaker pattern visible

3. **Frontend → API**
   - REST API calls (port 8000)
   - WebSocket for real-time updates
   - Environment variables for agent URLs (hardcoded)

4. **Orchestrator → Agents**
   - Health checks every 30s
   - Failover coordination
   - Mesh event routing

---

## 🔒 Security Boundaries

### Authentication Flow
```
User → Frontend → API (JWT validation) → Service
                        ↓
                  API Key Middleware
                        ↓
                  Rate Limiting
```

### Authorization Levels
1. **Public**: Health checks, OpenAPI docs
2. **Authenticated**: Standard API access
3. **Premium**: High-rate-limit endpoints
4. **Admin**: Service management, billing access

### Current Issues ⚠️
- API keys in `.env` files (not secret-managed)
- Test Stripe keys in codebase
- No encryption at rest for DB
- Missing audit logging

---

## 📁 Repository Structure (Production Only)

### Recommended Clean Structure
```
kloud-cloud/
├── apps/
│   ├── api/              # Main FastAPI service (port 8000)
│   └── web/              # Next.js frontend (port 3000)
├── backend/              # Supporting backend services
│   ├── mesh/             # Networking & coordination
│   ├── neuro/            # Neural engines
│   └── utils/            # Shared utilities
├── agents/               # AI Agent services
│   ├── alba/             # Port 5555 - Data collector
│   ├── albi/             # Port 6666 - Analytics
│   ├── jona/             # Port 7777 - Coordinator
│   ├── asi/              # ASI core
│   └── agiem/            # AGIEM evolution module
├── orchestrator/         # Service orchestration (port 9999)
├── dags/                 # Airflow data pipelines
├── ops/                  # Infrastructure configs
│   ├── prometheus.yml
│   ├── grafana-dashboards/
│   ├── loki/
│   └── alertmanager.yml
├── infra/                # Deployment manifests
│   ├── docker-compose.yml
│   └── k8s/              # Kubernetes (future)
├── tests/                # Test suite (consolidated)
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                 # Architecture & API docs
├── .env.production       # Production secrets (gitignored)
└── README.md
```

### Files to Archive/Remove
See **Appendix A: Cleanup Recommendations**

---

## 🚀 Deployment Model

### Current: Docker Compose (Development + Production)
- **Primary**: `docker-compose.yml`
- **Scaling**: Limited to single-node
- **Orchestration**: Manual via PowerShell scripts

### Recommended: Hybrid Approach
1. **Development**: Docker Compose (current)
2. **Staging**: Docker Swarm or Kubernetes
3. **Production**: Kubernetes (AWS EKS / GCP GKE / Azure AKS)

### Service Ports (Production)
| Service | Port | Exposure |
|---------|------|----------|
| Frontend | 3000 | Public |
| Main API | 8000 | Public |
| Alba | 5555 | Internal |
| Albi | 6666 | Internal |
| Jona | 7777 | Internal |
| Slack Service | 8888 | Internal |
| Orchestrator | 9999 | Internal |
| PostgreSQL | 5432 | Internal |
| Redis | 6379 | Internal |
| Prometheus | 9090 | Internal (admin) |
| Grafana | 3001 | Internal (admin) |

---

## 🔧 CI/CD Pipeline (Future State)

### Build Pipeline
```
GitHub → CI (GitHub Actions / GitLab CI)
  ├── Lint & Type Check
  ├── Unit Tests
  ├── Integration Tests
  ├── Build Docker Images
  ├── Security Scan (Trivy)
  └── Push to Registry
```

### Deployment Pipeline
```
Registry → Staging (Auto Deploy)
  ├── Smoke Tests
  ├── Load Tests
  └── Manual Approval
       ↓
Production (Blue/Green Deploy)
  ├── Health Checks
  ├── Gradual Rollout
  └── Rollback on Failure
```

**Current Status**: Manual deployment ⚠️

---

## 🎯 Agent Roles & Boundaries

### ALBA - Data Collection Agent
**Owner**: Data Engineering Team  
**Responsibility**: Raw signal ingestion  
**SLA**: 99.5% uptime, < 100ms latency  
**API Surface**:
- `POST /collect` - Ingest EEG frames
- `GET /status` - Health check
- `GET /metrics` - Prometheus metrics

**Do NOT**: Perform analysis, synthesis, or coordination

---

### ALBI - Analytics Agent
**Owner**: Data Science Team  
**Responsibility**: Pattern recognition & learning  
**SLA**: 99.5% uptime, < 500ms processing time  
**API Surface**:
- `POST /analyze` - Process neural data
- `GET /model/status` - ML model health
- `GET /metrics` - Prometheus metrics

**Do NOT**: Collect data, generate audio, or manage mesh

---

### JONA - Coordination Agent
**Owner**: Platform Team  
**Responsibility**: Multi-agent synthesis & orchestration  
**SLA**: 99.9% uptime, < 200ms response  
**API Surface**:
- `POST /synthesize` - Generate neural audio
- `GET /coordination/status` - Mesh health
- `GET /metrics` - Prometheus metrics

**Do NOT**: Perform low-level data collection or analytics

---

### ASI - System Intelligence
**Owner**: Platform Team  
**Responsibility**: Cross-system optimization  
**SLA**: Best effort (experimental-to-production transition)  
**API Surface**: Internal only (no external exposure)

**Do NOT**: Replace agent logic - augment only

---

### AGIEM - Evolution Module
**Owner**: Research Team  
**Responsibility**: Meta-intelligence & system evolution  
**SLA**: Best effort (production monitoring, experimental optimization)  
**API Surface**: Internal only

**Do NOT**: Control agent lifecycle directly

---

## 📈 Monitoring & Alerting

### Key Metrics (Prometheus)

#### System Health
- `kloud_api_requests_total` - API request count
- `kloud_api_latency_seconds` - API response time
- `kloud_agent_health` - Agent status (0=down, 1=up)

#### Business Metrics
- `kloud_active_users` - Current user sessions
- `kloud_subscriptions_active` - Paid subscriptions
- `kloud_revenue_mrr` - Monthly recurring revenue

#### Agent Metrics
- `alba_frames_processed_total` - Data ingestion rate
- `albi_predictions_total` - Analytics throughput
- `jona_synthesis_duration_seconds` - Audio generation time

### Alerting Rules (`ops/alert-rules.yml`)
- **Critical**: API down > 1min, DB unreachable
- **Warning**: High latency (p95 > 1s), error rate > 1%
- **Info**: High load (CPU > 80%), disk > 85%

### Grafana Dashboards
1. **Executive Dashboard** - Business KPIs
2. **System Overview** - Infrastructure health
3. **Agent Trinity** - Alba/Albi/Jona metrics
4. **ASI Insights** - Meta-intelligence metrics

---

## 🧪 Testing Strategy

### Test Pyramid
```
        /\
       /E2E\        (10% - Selenium, Playwright)
      /──────\
     /Integ.  \     (30% - API integration tests)
    /──────────\
   /   Unit     \   (60% - Pytest, Jest)
  /______________\
```

### Current Test Coverage
- **Unit Tests**: Scattered (`test_*.py` in root)
- **Integration Tests**: 3 files in `tests/`
- **E2E Tests**: Missing ❌

**Recommendation**: Consolidate to `tests/` directory, add CI pipeline

---

## 📜 Licensing & Ownership

### Kloud SaaS Platform
- **Type**: Commercial Proprietary
- **Owner**: [Company Name]
- **License**: Closed Source (for SaaS customers)
- **Scope**: All services in this document

### Third-Party Dependencies
- **Open Source**: FastAPI, Next.js, PostgreSQL, Prometheus (see `requirements.txt`, `package.json`)
- **Commercial**: Stripe (payment gateway), OpenAI (optional AI features)

**Separation from UltraWebThinking**: Required ⚠️

---

## 🔮 2026 Roadmap (Stability Focus)

### Q1 2026: Cleanup & Consolidation
- [ ] Archive experimental code to `/research`
- [ ] Remove duplicate frontends & launchers
- [ ] Consolidate backend services (`backend/` → `apps/api/`)
- [ ] Implement secrets management (AWS Secrets Manager / Vault)
- [ ] Add circuit breakers & retry logic

### Q2 2026: Testing & CI/CD
- [ ] 80% unit test coverage
- [ ] Integration test suite for all agents
- [ ] Automated CI/CD pipeline (GitHub Actions)
- [ ] Blue/green deployment strategy

### Q3 2026: Kubernetes Migration
- [ ] Kubernetes manifests for all services
- [ ] Horizontal pod autoscaling
- [ ] Production deployment to managed K8s
- [ ] Multi-region replication

### Q4 2026: Enterprise Features
- [ ] SSO integration (OAuth, SAML)
- [ ] Advanced RBAC & audit logs
- [ ] Multi-tenancy improvements
- [ ] SLA dashboard for customers

---

## 📞 Service Ownership

| Service | Team | On-Call | Slack Channel |
|---------|------|---------|---------------|
| Main API | Platform | @platform-oncall | #kloud-api |
| Alba | Data Eng | @dataeng-oncall | #kloud-alba |
| Albi | Data Science | @ds-oncall | #kloud-albi |
| Jona | Platform | @platform-oncall | #kloud-jona |
| Frontend | Frontend | @frontend-oncall | #kloud-web |
| Infra | DevOps | @devops-oncall | #kloud-infra |

---

## 🆘 Incident Response

### Severity Levels
- **SEV-1**: Complete platform outage → Page all teams
- **SEV-2**: Major feature broken → Page owning team
- **SEV-3**: Degraded performance → Slack alert
- **SEV-4**: Minor bug → Ticket only

### Runbooks
- **API Down**: Check Orchestrator (9999), restart agents
- **DB Slow**: Check connection pool, restart PostgreSQL
- **High Latency**: Check Prometheus for bottleneck, scale services

---

## 📚 Appendix A: Cleanup Recommendations

### Move to `/research/`
```
- generated_apis/
- generated_proposals/
- research_proposal_lab.py
- real_agi_system.py
- self_generating_api.py
- peer_node.py
- sandbox_core.py
```

### Move to `/archive/`
```
- frontend/ (old Next.js)
- frontend-new/ (another old Next.js)
- kloud-supernova/ (Vite app)
- launch_kloud_cloud.py
- start_server.py
- run_*.py (5 files)
- simple_server.py
- react_backend.py
- kloud_*.py (6 files in root)
- packages/signal-gen/ (TypeScript prototypes)
```

### Consolidate to `/tests/`
```
- All test_*.py from root (13 files)
- Keep tests/ directory structure
```

### Delete Entirely
```
- *.db files (SQLite dev databases)
- dump.rdb (Redis dev dump)
- node.key (generate per environment)
- *.bak files (28 backup files)
```

---

## 📚 Appendix B: Environment Variables

### Production `.env` Template
```bash
# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/kloud
REDIS_URL=redis://redis:6379/0

# Services
API_BASE_URL=https://api.kloud.com
ALBA_URL=http://alba:5555
ALBI_URL=http://albi:6666
JONA_URL=http://jona:7777
ORCHESTRATOR_URL=http://orchestrator:9999

# Auth
JWT_SECRET=<GENERATE_STRONG_SECRET>
API_KEY_SALT=<GENERATE_STRONG_SALT>

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# External APIs
OPENAI_API_KEY=sk-...
YOUTUBE_API_KEY=AIza...

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3001
LOKI_URL=http://loki:3100
```

**Security**: Use secret manager, never commit to Git

---

## 📚 Appendix C: API Contract Examples

### Alba API Contract
```yaml
openapi: 3.0.0
info:
  title: Alba Data Collection API
  version: 1.0.0
paths:
  /collect:
    post:
      summary: Ingest EEG data frame
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                timestamp: { type: string, format: date-time }
                channels: { type: array, items: { type: number } }
                sample_rate: { type: integer }
      responses:
        '200':
          description: Frame accepted
          content:
            application/json:
              schema:
                type: object
                properties:
                  status: { type: string }
                  frame_id: { type: string }
```

*Full contracts to be documented in separate OpenAPI files*

---

## ✅ Document Approval

**Version**: 1.0.0  
**Date**: December 2025  
**Author**: AI Engineering Team  
**Review Status**: ⚠️ DRAFT - Awaiting stakeholder approval  

**Approved By**:
- [ ] CTO
- [ ] Head of Engineering
- [ ] Lead DevOps Engineer
- [ ] Product Manager

**Next Review**: March 2026

---

**END OF DOCUMENT**

