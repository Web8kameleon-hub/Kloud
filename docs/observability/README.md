# Kloud Cloud — Observability Suite
**Enterprise Monitoring · TSDB Analysis · Performance Telemetry**

Kloud Cloud përdor një arkitekturë moderne observability me:

- **Prometheus TSDB**
- **Grafana Dashboards**
- **Exporter-layer custom**
- **Kloud Internal Neuro-Monitor Engine**

Ky dokument shërben si hyrje për:

- SRE engineers
- DevOps teams
- Cloud architects
- Investors reviewing platform maturity
- Enterprise clients assessing reliability

---

## 🔭 Overview

Observability në Kloud është ndërtuar mbi 3 shtylla:

### 1. Metrics

Prometheus mbledh të gjitha metrikat e sistemeve:

- API latency
- Error rates
- TSDB internal metrics
- Network diagnostics
- Custom neurosonic pipeline metrics

### 2. Logs

Logs qëndrojnë të strukturuara si:

- Application logs
- System logs
- Audit logs
- Access logs
- Neurosonic processing logs

### 3. Traces

Në versionin 1.1 futet:

- OpenTelemetry tracing
- Distributed spans midis API → Brain Engine → ALBA Streams

---

## 📊 Metrics Included

Kloud mbledh 5 kategori metrikash:

| Category | Description |
|----------|-------------|
| **API Metrics** | Request duration, body size, response code |
| **System Metrics** | CPU, RAM, disks, threads |
| **TSDB Metrics** | Chunks, series, compaction, cardinality |
| **Network Metrics** | Conntrack, dialer failures |
| **Kloud Neural Metrics** | EEG ingestion, brain-sync workloads, harmonic engines |

---

## 📈 TSDB Status Snapshot (From Your Grafana)

| Metric | Value |
|--------|-------|
| **Series Count** | 1053 |
| **Chunks** | 1053 |
| **Label Pairs** | 515 |
| **Active Window** | 2025-12-10 15:09 → 16:23 |

Ky është një TSDB **ultra i shëndetshëm** — ideal për një startup në fazë rritjeje / pre-production.

---

## 🚦 Cardinality Risk Evaluation

Cardinality është metrika më kritike e Prometheus.

Në Kloud:

- `instance = localhost:9090` → **1013 series**
- `job = prometheus` → **1013 series**

**Top metric families:**

- `prometheus_http_request_duration_seconds_bucket` → **130 series**
- `prometheus_http_response_size_bytes_bucket` → **117 series**

**Rreziku aktual:**  
🟢 **Low (stable)** – s'ka eksplodime të cardinality.

---

## 📊 Grafana Dashboards

Visualizimet e mëposhtme janë të disponueshme në `grafana-dashboards/`:

### Chart 1: Memory Usage by Label Name
![Memory Usage](grafana-dashboards/chart1.png)

**Analysis:** `__name__` label dominon me ~52KB, followed by `instance` (~25KB). This indicates healthy label distribution without memory bloat.

### Chart 2: Top Label Value Pair Cardinality
![Label Cardinality](grafana-dashboards/chart2.png)

**Analysis:** `instance=localhost:9090` and `job=prometheus` each have ~1000 unique combinations. This is expected for a single-instance Prometheus setup.

### Chart 3: TSDB Time Window Timeline
![TSDB Timeline](grafana-dashboards/chart3.png)

**Analysis:** Linear growth from position 1.0 to 2.0 indicates steady data ingestion over the monitoring period (15:09 → 16:23).

### Chart 4: Top Metric Families by Series Count
![Metric Families](grafana-dashboards/chart4.png)

**Analysis:** 
- `http_req_dur_bucket` leads with 130 series
- `http_resp_size_bucket` follows with 117 series
- Total series distribution is well-balanced across metric families

### Chart 5: Label Cardinality
![Label Pairs](grafana-dashboards/chart5.png)

**Analysis:** 515 unique label pairs across the entire TSDB. This low cardinality ensures efficient query performance.

### Chart 6: Total Active Time Series
![Active Series](grafana-dashboards/chart6.png)

**Analysis:** 1053 active series represent a lightweight, production-ready monitoring setup.

---

## 📂 Next Sections

Dokumentacioni ndahet në kapituj:

- **[metrics-overview.md](metrics-overview.md)** → shpjegon të gjitha metrikat
- **[tsdb-analysis.md](tsdb-analysis.md)** → komenton grafikun 1, 2, 3, 4, 5
- **[cardinality-engineering.md](cardinality-engineering.md)** → praktikat anti-explosion
- **[alerts.md](alerts.md)** → alert rregullat enterprise
- **[anomalies-report.md](anomalies-report.md)** → analiza inteligjente e trafikut

---

## 🔧 For Developers

### Quick Start

```bash
# View Prometheus metrics
curl http://localhost:9090/metrics

# Access Grafana
open http://localhost:3000

# Query TSDB status
curl http://localhost:9090/api/v1/status/tsdb
```

### Key Endpoints

- **Prometheus:** `http://localhost:9090`
- **Grafana:** `http://localhost:3000`
- **API Metrics:** `http://localhost:8000/metrics`
- **Neural Metrics:** `http://localhost:5555/metrics`

---

## 📄 Export & Reporting

This documentation is available in:

- **Markdown** (GitHub-ready)
- **PDF** (for investors/partners)
- **HTML** (embedded in internal wiki)

---

**Maintained by:** Kloud Cloud SRE Team  
**Last Updated:** December 11, 2025  
**Version:** 1.0.0

