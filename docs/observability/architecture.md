# Kloud Cloud — Observability Architecture

**Document Status:** Draft  
**Version:** 1.0.0  
**Last Updated:** December 11, 2025

---

## Overview

This document describes the end-to-end observability architecture for Kloud Cloud, covering metrics collection, storage, visualization, and alerting.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Kloud Services                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   API    │  │  ALBA    │  │  ALBI    │  │  JONA    │   │
│  │  :8000   │  │  :5555   │  │  :6666   │  │  :7777   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                          │                                  │
│                    /metrics endpoints                       │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │   Prometheus   │
                  │    :9090       │
                  │                │
                  │  - Scraping    │
                  │  - TSDB        │
                  │  - Alerting    │
                  └────────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │    Grafana     │
                  │    :3000       │
                  │                │
                  │  - Dashboards  │
                  │  - Queries     │
                  │  - Alerts      │
                  └────────────────┘
```

---

## Components

### 1. Metrics Exporters

Each Kloud service exposes metrics via `/metrics` endpoint:

- **FastAPI apps:** Built-in Prometheus middleware
- **Custom metrics:** Business logic counters/gauges
- **System metrics:** Node exporter integration

### 2. Prometheus TSDB

**Configuration:**
- Scrape interval: 15s
- Retention: 15d
- Storage: Local TSDB
- Target discovery: Static configs

**Key Features:**
- Time-series database optimized for metrics
- PromQL query language
- Built-in alerting rules
- Federation support (future)

### 3. Grafana

**Dashboards:**
- System overview
- API performance
- Neural engine metrics
- TSDB health
- Business KPIs

**Integrations:**
- Prometheus data source
- Alert channels (Slack, email)
- Custom panels

---

## Data Flow

1. **Collection:** Services expose `/metrics` (Prometheus format)
2. **Scraping:** Prometheus pulls metrics every 15s
3. **Storage:** Metrics stored in TSDB with compression
4. **Querying:** Grafana queries Prometheus via PromQL
5. **Visualization:** Dashboards render real-time charts
6. **Alerting:** Rules trigger notifications on thresholds

---

## Scalability Considerations

### Current Setup (Single Instance)
- ✅ Suitable for development/staging
- ✅ Handles 1000+ series efficiently
- ✅ Low operational overhead

### Future Scaling (Production)
- **Prometheus HA:** Multiple replicas with Thanos
- **Remote Storage:** Long-term metrics in S3
- **Distributed Tracing:** OpenTelemetry integration
- **Log Aggregation:** Loki for centralized logging

---

## Security

- **Authentication:** Grafana OAuth integration
- **Network:** Internal-only Prometheus endpoint
- **Encryption:** TLS for remote write (future)
- **RBAC:** Role-based dashboard access

---

## Monitoring the Monitors

Prometheus monitors itself:
- `/metrics` endpoint self-scraping
- TSDB health checks
- Query performance metrics
- Alert rule evaluation latency

---

**Next:** [Metrics Overview →](metrics-overview.md)

