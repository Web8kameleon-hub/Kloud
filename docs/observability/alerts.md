# Alert Rules — Enterprise Monitoring

**Document Status:** Draft  
**Version:** 1.0.0  
**Last Updated:** December 11, 2025

---

## Overview

This document defines alert rules for Kloud Cloud's production monitoring.

---

## Alert Severity Levels

| Severity | SLA Response | Notification | Escalation |
|----------|--------------|--------------|------------|
| **🔴 Critical** | < 5 min | PagerDuty + SMS | Immediate |
| **🟠 Warning** | < 30 min | Slack + Email | 1 hour |
| **🟡 Info** | < 4 hours | Email only | None |

---

## Service-Level Alerts

### API Availability

```yaml
groups:
  - name: api_sla
    interval: 30s
    rules:
      - alert: APIDown
        expr: up{job="api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API is down"
          description: "{{ $labels.instance }} has been unreachable for 1 minute"

      - alert: APIHighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
          /
          sum(rate(http_requests_total[5m])) by (service)
          > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High 5xx error rate on {{ $labels.service }}"
          description: "Error rate: {{ $value | humanizePercentage }}"

      - alert: APIHighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
          ) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API p95 latency > 2s on {{ $labels.service }}"
          description: "Current p95: {{ $value }}s"
```

---

## Infrastructure Alerts

### Resource Exhaustion

```yaml
groups:
  - name: infrastructure
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (rate(process_cpu_seconds_total[5m])) * 100) < 20
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU usage above 80% on {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: |
          (process_resident_memory_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Memory usage above 90% on {{ $labels.instance }}"

      - alert: DiskSpaceLow
        expr: |
          (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space below 10% on {{ $labels.instance }}"
          description: "Available: {{ $value }}%"
```

---

## TSDB Health Alerts

### Prometheus Monitoring

```yaml
groups:
  - name: tsdb_health
    rules:
      - alert: PrometheusHighCardinality
        expr: prometheus_tsdb_head_series > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "TSDB series count exceeding 10K"
          description: "Current: {{ $value }} series"

      - alert: PrometheusCompactionSlow
        expr: prometheus_tsdb_compaction_duration_seconds > 300
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "TSDB compaction taking > 5 minutes"

      - alert: PrometheusScrapeFailing
        expr: up{job="prometheus"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Prometheus cannot scrape {{ $labels.instance }}"

      - alert: PrometheusHighRejectionRate
        expr: |
          rate(prometheus_target_scrapes_sample_out_of_order_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High sample rejection rate"
          description: "{{ $value }} samples/sec rejected"
```

---

## Business Logic Alerts

### Kloud-Specific Metrics

```yaml
groups:
  - name: kloud_business
    rules:
      - alert: ALBAFrameGenerationStalled
        expr: |
          rate(alba_frames_generated_total[5m]) == 0
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "ALBA stopped generating frames"

      - alert: ALBIInsightsDelayed
        expr: |
          rate(albi_insights_computed_total[5m]) < 0.1
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "ALBI insight generation slowed"

      - alert: JONAAudioStreamsDown
        expr: jona_audio_streams_active == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "JONA has no active audio streams"

      - alert: NeuroEEGIngestionStopped
        expr: |
          rate(neuro_eeg_packets_received_total[5m]) == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "No EEG data being ingested"
```

---

## Dependency Alerts

### External Services

```yaml
groups:
  - name: dependencies
    rules:
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is unreachable"

      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is unreachable"

      - alert: S3HighErrorRate
        expr: |
          sum(rate(aws_s3_errors_total[5m])) by (bucket) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High S3 error rate on {{ $labels.bucket }}"
```

---

## Alert Routing

### Alertmanager Configuration

```yaml
route:
  receiver: 'default'
  group_by: ['alertname', 'service']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 4h
  
  routes:
    - match:
        severity: critical
      receiver: pagerduty
      continue: true
    
    - match:
        severity: warning
      receiver: slack
      continue: true
    
    - match:
        severity: info
      receiver: email

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@kloud.com'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_KEY>'

  - name: 'slack'
    slack_configs:
      - api_url: '<SLACK_WEBHOOK>'
        channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'

  - name: 'email'
    email_configs:
      - to: 'monitoring@kloud.com'
```

---

## Runbooks

### APIDown Runbook

**Alert:** `APIDown`  
**Severity:** Critical

**Diagnosis:**
1. Check service status: `systemctl status kloud-api`
2. Review logs: `journalctl -u kloud-api -n 100`
3. Test connectivity: `curl http://localhost:8000/health`

**Resolution:**
1. Restart service: `systemctl restart kloud-api`
2. If still down, check dependencies (PostgreSQL, Redis)
3. Escalate to on-call engineer if not resolved in 5 minutes

---

### HighMemoryUsage Runbook

**Alert:** `HighMemoryUsage`  
**Severity:** Critical

**Diagnosis:**
1. Check memory usage: `free -h`
2. Identify top processes: `ps aux --sort=-%mem | head -20`
3. Review Prometheus memory: `curl localhost:9090/metrics | grep process_resident`

**Resolution:**
1. Identify memory leak (check recent deployments)
2. Restart affected service
3. Increase memory limits if sustained growth
4. Plan vertical scaling if recurring

---

## Testing Alerts

### Manual Alert Trigger

```bash
# Trigger high error rate alert
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/trigger-error
done

# Trigger high latency alert
curl http://localhost:8000/api/slow-endpoint?delay=5000
```

### Alert Testing Best Practices

1. **Test during business hours** (ensure team is available)
2. **Document test results** (verify all channels fire)
3. **Verify escalation** (confirm PagerDuty pages on-call)
4. **Check alert fatigue** (ensure alerts aren't too noisy)

---

## Alert Metrics

Track alert effectiveness:

```promql
# Alert firing rate
sum(ALERTS{alertstate="firing"}) by (alertname)

# Time to resolution
histogram_quantile(0.95, sum(rate(alert_resolution_duration_seconds_bucket[24h])) by (le))

# False positive rate
sum(rate(alerts_silenced_total[7d])) by (alertname) / sum(rate(alerts_fired_total[7d])) by (alertname)
```

---

**Next:** [Anomalies Report →](anomalies-report.md)

