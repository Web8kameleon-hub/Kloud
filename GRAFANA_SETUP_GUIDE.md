# 📊 Grafana Dashboard Setup Guide - ASI Trinity Real-Time Monitoring

## Quick Start (3 Steps)

### Step 1: Access Grafana
```
URL: http://localhost:3001
Username: admin
Password: admin
```

### Step 2: Add Prometheus Datasource
1. Click **Configuration** (gear icon) → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL to: `http://localhost:9090`
5. Click **Save & Test**

### Step 3: Import Dashboard
1. Click **+** (Create) → **Import**
2. Copy-paste the JSON from `grafana-asi-trinity-dashboard.json`
3. Click **Load**
4. Select Prometheus datasource
5. Click **Import**

---

## 📈 Available Panels

### Real-Time Metrics

| Panel | Metric | Source | Refresh |
|-------|--------|--------|---------|
| **ALBA Network Health** | CPU % | `process_cpu_seconds_total` | 5s |
| **Memory Usage** | MB | `process_resident_memory_bytes` | 5s |
| **ALBI Neural Processing** | Goroutines | `go_goroutines` | 5s |
| **GC Operations** | Time (s) | `go_gc_duration_seconds` | 5s |
| **JONA Coordination** | Requests/5m | `promhttp_metric_handler_requests_total` | 5s |
| **HTTP Requests** | Rate | Calculated | 5s |
| **System Uptime** | Seconds | `process_start_time_seconds` | 5s |

---

## 🔗 Dashboard JSON

The dashboard definition is available in:
- **File**: `grafana-asi-trinity-dashboard.json`
- **API Import**: `POST /api/dashboards/db` (requires Grafana API key)

---

## 🎯 What Each Component Shows

### ALBA Network (Left Panel)
- **Real CPU Usage** from actual system processes
- **Memory Consumption** in MB from resident memory
- **Network Latency** calculated from metrics

### ALBI Neural (Middle Panel)
- **Active Goroutines** (concurrency)
- **Neural Patterns** detected
- **GC Pause Time** for efficiency

### JONA Coordination (Right Panel)
- **HTTP Requests** in 5-minute windows
- **Request Rate** per second
- **Overall Coordination Score**

---

## 📡 Prometheus Queries

### CPU Usage (%)
```
rate(process_cpu_seconds_total[1m]) * 100
```

### Memory (MB)
```
process_resident_memory_bytes / 1024 / 1024
```

### Active Goroutines
```
go_goroutines
```

### HTTP Requests (5m)
```
increase(promhttp_metric_handler_requests_total[5m])
```

### GC Time
```
go_gc_duration_seconds_sum
```

### Uptime (seconds)
```
time() - process_start_time_seconds
```

---

## 🚀 Automated Setup (Docker)

If using Docker containers, add to `docker-compose.yml`:

```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  volumes:
    - grafana-storage:/var/lib/grafana
    - ./grafana-dashboards.yaml:/etc/grafana/provisioning/dashboard-providers.yaml
    - ./grafana-asi-trinity-dashboard.json:/etc/grafana/provisioning/dashboards/asi-trinity.json
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_USERS_ALLOW_SIGN_UP=false
```

---

## 🔄 Refreshing Metrics

Dashboard refreshes every **5 seconds** automatically:
- Real-time CPU/Memory updates
- Live goroutine counts
- Current request rates
- Active health scores

---

## 📊 Expected Values

### ALBA Network
- CPU: 0.1 - 5% (typically low)
- Memory: 80 - 200 MB
- Latency: 10 - 50 ms
- Health: 0.8 - 0.99

### ALBI Neural
- Goroutines: 20 - 100
- Neural Patterns: 1000 - 2000
- GC Time: 0.001 - 0.01 seconds
- Health: 0.2 - 0.8

### JONA Coordination
- Requests (5m): 10 - 100
- Request Rate: 0.1 - 1 req/sec
- Coordination: 40 - 80%
- Health: 0.4 - 0.95

---

## 🆘 Troubleshooting

### Dashboard Not Loading
- Verify Prometheus is running: `http://localhost:9090`
- Check datasource connection
- Ensure metrics are being scraped

### No Data Points
- Check if Prometheus has collected metrics (wait 5-10 seconds)
- Verify metric names in Prometheus UI
- Check Prometheus scrape interval

### Connection Refused
- Ensure Grafana is running on port 3001
- Check `docker ps` for running containers
- Verify Prometheus URL: `http://localhost:9090`

---

## 🎓 Learning Resources

1. **Prometheus Metrics**: http://localhost:9090/metrics
2. **Grafana Docs**: https://grafana.com/docs/
3. **PromQL Guide**: https://prometheus.io/docs/prometheus/latest/querying/basics/

---

## API Endpoints That Power This Dashboard

```
GET /asi/status           → Full ASI Trinity status
GET /asi/health           → Overall health check
GET /asi/alba/metrics     → ALBA Network metrics
GET /asi/albi/metrics     → ALBI Neural metrics
GET /asi/jona/metrics     → JONA Coordination metrics
```

All endpoints source from **real Prometheus metrics** - zero synthetic data! ✅

---

**Last Updated**: December 9, 2025
**System**: Kloud Cloud - ASI Trinity
**Data Source**: Prometheus (Real-Time)

