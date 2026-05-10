# KAMELEON LIFE - COMPLETE SYSTEM DOCUMENTATION

## 📋 Table of Contents
- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Integration Guide](#integration-guide)
- [Deployment](#deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

Kameleon Life is a **fully integrated neural audio synthesis system** with distributed microservices:

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Port 3000)                      │
│              Next.js Dashboard & Web Interface               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   API GATEWAY (Port 8000)                    │
│              FastAPI - Main Application Server               │
├──────────────────────┬──────────────────────────────────────┤
│                      │                                       │
│    ┌─────────────────┼─────────────────┐                   │
│    │                 │                 │                    │
▼    ▼                 ▼                 ▼                    ▼
┌────────┐         ┌────────┐       ┌────────┐         ┌─────────┐
│ ALBA   │         │ ALBI   │       │ JONA   │         │ORCHESTR │
│5555    │         │6666    │       │7777    │         │9999     │
│        │         │        │       │        │         │         │
│Telemetry         │Neural  │       │Data    │         │Service  │
│Collector         │Analytics      │Synthesis         │Registry │
└────────┘         └────────┘       └────────┘         └─────────┘
    │                  │                │                   │
    │                  │                │                   │
    └──────────────────┼────────────────┴───────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌────────┐
    │PostgreSQL    │ Redis  │    │MinIO   │
    │5432          │6379    │    │9000    │
    └────────┘     └────────┘    └────────┘
```

---

## Services

### 1. **Frontend (Port 3000)**
- Next.js 15 web application
- Real-time dashboard for system monitoring
- User interface for audio synthesis
- Environment: `NEXT_PUBLIC_API_BASE=http://localhost:8000`

### 2. **API Gateway (Port 8000)**
- FastAPI main application
- REST API endpoints
- WebSocket support
- Authentication & authorization
- Database connection pool

### 3. **ALBA Collector (Port 5555)**
- **Purpose**: Network telemetry collection
- **Endpoints**:
  - `POST /ingest` - Ingest sensor data
  - `GET /data` - Retrieve collected telemetry
  - `GET /metrics` - Service metrics
  - `GET /health` - Health check

### 4. **ALBI Processor (Port 6666)**
- **Purpose**: Neural data analysis and pattern detection
- **Endpoints**:
  - `POST /analyze` - Analyze data for patterns
  - `GET /insights` - Get analysis insights
  - `GET /anomalies` - Get detected anomalies
  - `GET /metrics` - Service metrics
  - `GET /health` - Health check

### 5. **JONA Coordinator (Port 7777)**
- **Purpose**: Audio synthesis and data coordination
- **Endpoints**:
  - `POST /synthesize` - Generate neural audio
  - `GET /synthesize/{id}` - Retrieve synthesis result
  - `GET /synthesize/{id}/audio` - Stream audio file
  - `POST /coordinate` - Coordinate multi-service tasks
  - `GET /queue` - Synthesis queue status
  - `GET /health` - Health check

### 6. **SAAS Orchestrator (Port 9999)**
- **Purpose**: Service discovery and orchestration
- **Key Endpoints**:
  - `GET /registry` - Service registry with health status
  - `GET /status/dashboard` - System dashboard
  - `GET /health` - Orchestrator health
  - `POST /communicate` - Inter-service messaging
  - `GET /metrics/aggregated` - Aggregated system metrics

---

## Getting Started

### Prerequisites
- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for services)
- **Docker** (optional, for containerized deployment)
- **Git** (for version control)

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/LedjanAhmati/Kloud-cloud.git
cd Kloud-cloud
```

2. **Install Dependencies**
```bash
# Frontend
cd apps/web
npm install

# Python services
cd ../..
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
# NEXT_PUBLIC_API_BASE=http://localhost:8000
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://localhost:6379
```

### Quick Start

#### Mode 1: Full System (Recommended)
```powershell
.\scripts\launch-all.ps1
```

#### Mode 2: SaaS Services Only
```powershell
.\scripts\launch-all.ps1 -Mode saas-only
```

#### Mode 3: Application Only
```powershell
.\scripts\launch-all.ps1 -Mode app-only
```

#### Mode 4: Docker Compose
```bash
docker-compose up -d
```

---

## API Documentation

### ALBA - Telemetry Collector

#### Ingest Data
```bash
POST /ingest
Content-Type: application/json

{
  "source": "sensor_001",
  "type": "eeg",
  "payload": {
    "frequency": 10.5,
    "amplitude": 0.8,
    "phase": 0.2
  }
}
```

**Response:**
```json
{
  "status": "ingested",
  "id": "abc123",
  "timestamp": "2025-01-01T00:00:00"
}
```

### ALBI - Neural Processor

#### Analyze Data
```bash
POST /analyze
Content-Type: application/json

{
  "channels": {
    "channel_1": [1.0, 1.2, 1.5, 1.3, 1.1],
    "channel_2": [2.0, 2.1, 2.05, 2.15, 2.08]
  }
}
```

**Response:**
```json
{
  "analysis_id": "xyz789",
  "statistics": {
    "channel_1": {
      "mean": 1.22,
      "std_dev": 0.17,
      "outliers": 0
    }
  },
  "anomalies": [],
  "confidence": 0.92
}
```

### JONA - Data Synthesis

#### Generate Audio
```bash
POST /synthesize
Content-Type: application/json

{
  "mode": "relax",
  "frequency": 10.0,
  "duration": 60,
  "amplitude": 0.7
}
```

**Response:**
```json
{
  "synthesis_id": "syn_001",
  "mode": "relax",
  "frequency": 10.0,
  "duration": 60,
  "status": "generated"
}
```

#### Stream Audio
```bash
GET /synthesize/{synthesis_id}/audio

# Returns WAV file stream
```

### Orchestrator - Service Management

#### Get Service Registry
```bash
GET /registry
```

**Response:**
```json
{
  "timestamp": "2025-01-01T00:00:00",
  "services": {
    "alba": {
      "name": "alba",
      "port": 5555,
      "status": "online",
      "health": 1.0
    },
    "albi": { ... },
    "jona": { ... }
  }
}
```

---

## Integration Guide

### Inter-Service Communication

Services communicate via the orchestrator using structured packets:

```python
# Example: Send telemetry from ALBA to ALBI
packet = {
    "source": "alba",
    "destination": "albi",
    "packet_type": "telemetry",
    "payload": {
        "channels": {...},
        "timestamp": "2025-01-01T00:00:00"
    }
}

response = requests.post(
    "http://localhost:9999/communicate",
    json=packet
)
```

### Data Flow Example

1. **Telemetry Ingestion** → ALBA (5555)
2. **Pattern Analysis** → ALBI (6666)
3. **Audio Synthesis** → JONA (7777)
4. **Result Delivery** → API (8000)

---

## Deployment

### Docker Compose (Production-Ready)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Included Services:**
- Frontend (3000)
- API (8000)
- ALBA (5555)
- ALBI (6666)
- JONA (7777)
- Orchestrator (9999)
- PostgreSQL (5432)
- Redis (6379)
- MinIO (9000)
- Prometheus (9090)
- Grafana (3001)

### Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n kloud
```

---

## Testing

### Comprehensive Test Suite

```bash
# Run all tests
pytest tests/test_comprehensive_integration.py -v

# Run specific test class
pytest tests/test_comprehensive_integration.py::TestAlbaService -v

# With coverage
pytest tests/test_comprehensive_integration.py --cov=. --cov-report=html
```

### CI/CD Pipeline

GitHub Actions workflow runs on every push:
- Code quality checks (flake8, black)
- Unit tests
- Integration tests
- Docker build verification
- Security scanning (Trivy)

**Status:** Check `.github/workflows/test-and-deploy.yml`

---

## Troubleshooting

### Port Already in Use

```powershell
# Find process using port
Get-NetTCPConnection -LocalPort 8000

# Kill process
Stop-Process -Id <PID> -Force

# Or free all SaaS ports
.\scripts\launch-all.ps1 -Mode full  # Auto-cleans ports
```

### Services Not Connecting

1. **Check health endpoints:**
```bash
curl http://localhost:5555/health
curl http://localhost:4444/health
curl http://localhost:7777/health
curl http://localhost:9999/health
```

2. **Check service registry:**
```bash
curl http://localhost:9999/registry
```

3. **Verify networking:**
```bash
docker network ls
docker network inspect kloud
```

### Database Connection Issues

```bash
# PostgreSQL
psql -h localhost -U postgres -d kloud

# Redis
redis-cli -h localhost -p 6379 ping

# MinIO
mc ls minio
```

### Memory/Resource Issues

```bash
# Monitor Docker
docker stats

# Monitor processes
Get-Process | Where-Object {$_.Name -like "*python*" -or $_.Name -like "*node*"}
```

---

## Monitoring & Observability

### Prometheus (Port 9090)
- System metrics collection
- Service health tracking
- Alert configuration

### Grafana (Port 3001)
- Dashboard visualization
- Real-time monitoring
- Alert notifications
- Default login: admin/admin

### Logs
```bash
# API logs
tail -f logs/Kloud_real.log

# Service logs (Docker)
docker-compose logs -f alba
docker-compose logs -f albi
docker-compose logs -f jona
```

---

## API Examples

### Complete Workflow

```python
import requests
import time

# 1. Ingest data into ALBA
alba_url = "http://localhost:5555"
data = {
    "source": "eeg_device_001",
    "type": "brainwave",
    "payload": {"frequency": 10.5, "amplitude": 0.8}
}
r1 = requests.post(f"{alba_url}/ingest", json=data)
print(f"Ingested: {r1.json()['id']}")

# 2. Analyze with ALBI
albi_url = "http://localhost:4444"
analysis_data = {
    "channels": {
        "ch1": [1.0, 1.1, 1.0, 0.9, 1.1],
        "ch2": [2.0, 2.1, 2.0, 1.9, 2.1]
    }
}
r2 = requests.post(f"{albi_url}/analyze", json=analysis_data)
analysis = r2.json()
print(f"Analysis ID: {analysis['analysis_id']}")

# 3. Synthesize audio with JONA
jona_url = "http://localhost:7777"
synthesis_config = {
    "mode": "relax",
    "frequency": 10.0,
    "duration": 30
}
r3 = requests.post(f"{jona_url}/synthesize", json=synthesis_config)
synthesis = r3.json()
print(f"Synthesis ID: {synthesis['synthesis_id']}")

# 4. Get audio stream
audio_response = requests.get(f"{jona_url}/synthesize/{synthesis['synthesis_id']}/audio")
with open("output.wav", "wb") as f:
    f.write(audio_response.content)
print("Audio saved to output.wav")
```

---

## Support & Documentation

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: `/docs/` directory
- **API Docs**: http://localhost:8000/docs (interactive Swagger UI)

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Maintainer**: Ledjan Ahmati

