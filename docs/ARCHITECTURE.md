# 🏗️ Kloud Cloud Architecture

## Overview

Kloud Cloud is an AI-powered Industrial IoT platform with Neural Intelligence capabilities, developed by Ledjan Ahmati / ABA GmbH (Germany).

## System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          KLOUD CLOUD PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    PRESENTATION LAYER (Frontend)                       │  │
│  │  • Next.js Web App (Port 3000)                                         │  │
│  │  • Mobile Apps (React Native)                                          │  │
│  │  • Admin Dashboard                                                     │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    API GATEWAY LAYER (Layer 13)                        │  │
│  │  • Rate Limiting                                                       │  │
│  │  • Authentication (JWT)                                                │  │
│  │  • Request Validation                                                  │  │
│  │  • Security Headers (Helmet)                                           │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                    AI INTELLIGENCE LAYERS (1-12)                       │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │  │
│  │  │ Layer 1 │ │ Layer 2 │ │ Layer 3 │ │ Layer 4 │ │ Layer 5 │          │  │
│  │  │  Core   │ │  DDoS   │ │  Mesh   │ │  Alba   │ │  Albi   │          │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │  │
│  │  │ Layer 6 │ │ Layer 7 │ │ Layer 8 │ │ Layer 9 │ │Layer 10 │          │  │
│  │  │  Jona   │ │Curiosity│ │ Neuro   │ │ Memory  │ │ Quantum │          │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │  │
│  │  ┌─────────┐ ┌─────────┐                                              │  │
│  │  │Layer 11 │ │Layer 12 │  ASI Trinity: Alba + Albi + ASI              │  │
│  │  │   AGI   │ │   ASI   │                                              │  │
│  │  └─────────┘ └─────────┘                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                  ENTERPRISE LAYERS (13-18)                             │  │
│  │  • Layer 13: API Gateway (Helmet, Rate Limiting)                       │  │
│  │  • Layer 14: Logging (Winston, Pino)                                   │  │
│  │  • Layer 15: Circuit Breaker (Opossum)                                 │  │
│  │  • Layer 16: Validation (Zod)                                          │  │
│  │  • Layer 17: Auth (JWT, RBAC)                                          │  │
│  │  • Layer 18: Config (Convict, dotenv)                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      DATA LAYER                                        │  │
│  │  • PostgreSQL (Primary Database)                                       │  │
│  │  • Redis (Caching & Sessions)                                          │  │
│  │  • Neo4j (Graph Database)                                              │  │
│  │  • MinIO (Object Storage)                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Services

| Service    | Port  | Description                 |
| ---------- | ----- | ----------------------------|
| ocean-core | 8030  | Curiosity Ocean AI Engine   |
| alba       | 5555  | Analytical Intelligence     |
| albi       | 6680  | Creative Intelligence       |
| asi        | 9094  | Artificial Superintelligence|
| clx     | 11434 | LLM Model Server            |
| postgres   | 5432  | Primary Database            |
| redis      | 6379  | Cache & Sessions            |

## Resonant Core

The platform now treats NDB, Stigma, and Tide as shared cross-service primitives.

- NDB is the nano-decibel resonance score used for stability and drift detection.
- Stigma is the persistent noise-trace memory model used for audit and history.
- Tide is the operational pressure band used for gating and policy decisions.
- Stigma Cloud is the long-lived fluid memory layer for trace preservation.

The canonical contract lives in [docs/RESONANT_CORE.md](docs/RESONANT_CORE.md).
Existing REST and JSON APIs remain compatible during migration.

## Technology Stack

### Backend (Python)

- FastAPI 0.115+
- Uvicorn (ASGI Server)
- Pydantic (Data Validation)
- SQLAlchemy (ORM)
- OpenTelemetry (Observability)

### Backend (Node.js)

- Express 4.x
- TypeScript 5.x
- Zod (Validation)
- Winston (Logging)
- Opossum (Circuit Breaker)

### Frontend

- Next.js 14+
- React 18+
- TailwindCSS
- Svelte (Some components)

### Infrastructure

- Docker & Docker Compose
- Kubernetes (Production)
- Nginx (Reverse Proxy)
- GitHub Actions (CI/CD)

## Security Measures

1. **Authentication**: JWT-based with refresh tokens
2. **Authorization**: Role-based access control (RBAC)
3. **Rate Limiting**: 100 requests per 15 minutes per IP
4. **Headers**: Helmet.js for security headers
5. **Validation**: All inputs validated with Zod/Pydantic
6. **Circuit Breaker**: Fault tolerance for external calls
7. **Encryption**: TLS 1.3 for all communications

## Monitoring & Observability

- **Logging**: Winston + Daily Rotate Files
- **Metrics**: Prometheus + VictoriaMetrics
- **Tracing**: OpenTelemetry + Jaeger
- **Dashboards**: Grafana

---

Kloud Cloud Platform © 2026 ABA GmbH - All Rights Reserved

| Service          | Port | Purpose                                    |
| ---------------- | ---- | ------------------------------------------ |
| ALBI             | 8001 | EEG signal processing and feature extract  |
| ALBA             | 8002 | Audio analysis and speech recognition      |
| Ocean            | 8003 | Core data orchestration and routing        |
| ASI              | 8004 | Artificial Superintelligence engine        |
| Curiosity Ocean  | 8005 | Advanced learning and reasoning            |
| Payment Service  | 8006 | Stripe, SEPA, PayPal webhook handling      |

