# Cardinality Engineering — Anti-Explosion Practices

**Document Status:** Draft  
**Version:** 1.0.0  
**Last Updated:** December 11, 2025

---

## What is Cardinality?

**Cardinality** = Number of unique label combinations in your metrics.

Example:
```
http_requests_total{method="GET", endpoint="/api", status="200"}
http_requests_total{method="POST", endpoint="/api", status="201"}
```

Cardinality = 2 (two unique label combinations)

---

## Why Cardinality Matters

### The Math

If you have:
- 10 methods × 100 endpoints × 10 status codes = **10,000 series**

Adding one high-cardinality label:
- 10 methods × 100 endpoints × 10 status codes × **1,000 user IDs** = **10,000,000 series**

### The Impact

**Low Cardinality (< 10K series):**
- ✅ Fast queries (< 100ms)
- ✅ Low memory usage (< 1GB)
- ✅ Easy to maintain

**High Cardinality (> 100K series):**
- ❌ Slow queries (> 10s)
- ❌ High memory usage (> 10GB)
- ❌ Frequent crashes
- ❌ Expensive infrastructure

---

## Kloud's Current State

| Metric | Value | Analysis |
|--------|-------|----------|
| **Total Series** | 1,053 | 🟢 Low |
| **Label Pairs** | 515 | 🟢 Very Low |
| **Top Label Cardinality** | 1,013 (`instance`) | 🟢 Expected |
| **Risk Level** | **Minimal** | 🟢 Safe |

**Interpretation:** Kloud is operating at ~1% of recommended limits.

---

## Anti-Explosion Rules

### ✅ DO: Use Low-Cardinality Labels

**Good labels:**
- `method` — GET, POST, PUT, DELETE (4 values)
- `status_code` — 200, 400, 500, etc. (~20 values)
- `service` — api, alba, albi, jona (4 values)
- `environment` — dev, staging, prod (3 values)

### ❌ DON'T: Use High-Cardinality Labels

**Bad labels:**
- `user_id` — unique per user (millions of values)
- `request_id` — unique per request (billions of values)
- `timestamp` — unique per second (infinite values)
- `email` — unique per user (millions of values)
- `session_id` — unique per session (millions of values)

---

## Case Study: The User ID Disaster

### Before (Bad)
```python
http_requests_total{user_id="12345", endpoint="/api"}
```

**Result:** 1 million users × 100 endpoints = **100 million series** 💥

### After (Good)
```python
http_requests_total{endpoint="/api"}
# User ID stored in logs, not metrics
```

**Result:** 100 endpoints = **100 series** ✅

**Alternative:** Use aggregated metrics
```python
users_active_total{tier="premium"}  # Group by subscription tier
```

---

## Histogram Bucket Optimization

### Current Setup
```
prometheus_http_request_duration_seconds_bucket{le="0.005"}
prometheus_http_request_duration_seconds_bucket{le="0.01"}
prometheus_http_request_duration_seconds_bucket{le="0.025"}
...
prometheus_http_request_duration_seconds_bucket{le="+Inf"}
```

**Buckets:** 11 per metric  
**Impact:** 1 histogram = 11 series

### Best Practices

1. **Use fewer buckets for low-traffic metrics:**
   ```yaml
   # Instead of 11 buckets, use 5
   buckets: [0.01, 0.1, 0.5, 1.0, 5.0]
   ```

2. **Aggregate before exporting:**
   ```python
   # Bad: Per-endpoint histograms
   request_duration{endpoint="/user/123"}
   
   # Good: Aggregated histograms
   request_duration{service="api"}
   ```

3. **Use recording rules:**
   ```yaml
   - record: api:request_duration:avg
     expr: rate(http_request_duration_sum[5m]) / rate(http_request_duration_count[5m])
   ```

---

## Label Normalization

### Problem: Unbounded Labels

```python
# Bad: endpoint="/user/12345"
# Creates series for every user ID
http_requests{endpoint="/user/12345"}
```

### Solution: Relabeling

```yaml
# prometheus.yml
metric_relabel_configs:
  - source_labels: [endpoint]
    regex: '/user/[0-9]+'
    target_label: endpoint
    replacement: '/user/:id'
```

**Result:** All user endpoints collapse into single series.

---

## Monitoring Cardinality

### PromQL Queries

**Check series count per label:**
```promql
count by (__name__) ({__name__=~".+"})
```

**Find high-cardinality labels:**
```promql
topk(10, count by (instance, job) ({__name__=~".+"}))
```

**Detect cardinality explosion:**
```promql
rate(prometheus_tsdb_head_series[1h]) > 100
```

### Alerts

```yaml
groups:
  - name: cardinality
    rules:
      - alert: HighCardinalityDetected
        expr: prometheus_tsdb_head_series > 10000
        for: 5m
        annotations:
          summary: "Series count exceeding 10K"
          description: "Current: {{ $value }} series"

      - alert: CardinalityGrowthRapid
        expr: rate(prometheus_tsdb_head_series[1h]) > 100
        for: 10m
        annotations:
          summary: "Series growing at {{ $value }}/hour"
```

---

## Cardinality Budget

### Allocation Strategy

| Service | Max Series | Labels | Notes |
|---------|-----------|--------|-------|
| **API Gateway** | 500 | `method`, `endpoint`, `status` | Core metrics |
| **ALBA** | 200 | `task_type`, `status` | Content generation |
| **ALBI** | 200 | `analysis_type`, `status` | Analytics |
| **JONA** | 200 | `stream_type`, `status` | Neural audio |
| **System** | 300 | `resource`, `node` | CPU, RAM, disk |
| **TSDB** | 300 | `instance`, `job` | Prometheus itself |
| **Reserve** | 2,300 | — | Future growth |
| **Total** | **4,000** | — | Target threshold |

---

## Tools & Techniques

### 1. Cardinality Explorer (Grafana Plugin)
```bash
grafana-cli plugins install grafana-cardinality-explorer
```

### 2. Prometheus Relabeling
```yaml
# Drop high-cardinality labels
metric_relabel_configs:
  - regex: 'user_id|session_id'
    action: labeldrop
```

### 3. Recording Rules
```yaml
# Pre-aggregate expensive queries
groups:
  - name: aggregations
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)
```

### 4. Metric Filtering
```yaml
# Only scrape specific metrics
metric_relabel_configs:
  - source_labels: [__name__]
    regex: '(http_.*|process_.*|go_.*)'
    action: keep
```

---

## Real-World Limits

### Industry Standards

| Scale | Series Count | Infrastructure |
|-------|-------------|----------------|
| **Small** | < 10K | Single Prometheus (2GB RAM) |
| **Medium** | 10K - 100K | Single Prometheus (8GB RAM) |
| **Large** | 100K - 1M | Prometheus HA + Remote Storage |
| **Massive** | > 1M | Thanos / Cortex / Mimir |

### Kloud Trajectory

**Current:** 1K series (Small)  
**6 months:** 5K series (Small → Medium transition)  
**12 months:** 20K series (Medium)  
**24 months:** 100K series (Medium → Large transition)

---

## Action Items

### Immediate (Week 1)
- [x] Audit current label usage ✅
- [ ] Set up cardinality alerts
- [ ] Document label standards

### Short-term (Month 1)
- [ ] Implement relabeling rules
- [ ] Create cardinality dashboard
- [ ] Train team on best practices

### Long-term (Quarter 1)
- [ ] Recording rules for common queries
- [ ] Remote storage evaluation
- [ ] Federation planning (multi-cluster)

---

**Next:** [Alerts →](alerts.md)

