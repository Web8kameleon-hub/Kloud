# 📱 KLOUD CLOUD - SLACK INTEGRATION GUIDE

## Overview

The Slack Integration Service provides real-time monitoring, automated alerts, and notifications for your Kloud Cloud system. All components (ALBA, ALBI, JONA, Orchestrator, API) are monitored and can send notifications directly to your Slack workspace.

---

## 🚀 Quick Start

### 1. Get Slack Webhook URL

1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create New App" → "From scratch"
3. Name your app: "Kloud Cloud"
4. Select your workspace
5. Enable Incoming Webhooks
6. Create New Webhook to Workspace
7. Select your channel (or create #kloud-monitoring)
8. Copy the Webhook URL

### 2. Start Slack Integration

```powershell
# Basic startup
.\start-slack.ps1 -WebhookUrl "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# With custom channel
.\start-slack.ps1 -WebhookUrl "..." -Channel "#alerts"

# Test mode (verify webhook works)
.\start-slack.ps1 -WebhookUrl "..." -Mode test

# Monitor mode (health checks only)
.\start-slack.ps1 -Mode monitor
```

### 3. Verify Integration

```powershell
# Check service health
curl http://localhost:8888/health

# Get status report
curl http://localhost:8888/service-health

# Send to Slack
curl http://localhost:8888/status-report
```

---

## 📊 Features

### 1. Real-time Service Monitoring

Automatically monitors all services every 60 seconds:
- **ALBA** (Port 5555) - Network Telemetry Collector
- **ALBI** (Port 6666) - Neural Analytics Processor
- **JONA** (Port 7777) - Data Synthesis Coordinator
- **Orchestrator** (Port 9999) - Service Registry
- **API** (Port 8000) - Main API Server

### 2. Automated Health Alerts

Alerts when services go:
- ⛔ **Offline** (Critical severity)
- ⚠️ **Degraded** (Warning severity)
- ✅ **Online** (Recovery notification)

### 3. Status Reports

Send comprehensive status reports to Slack:
```bash
curl -X GET http://localhost:8888/status-report
```

Reports include:
- Service status (online/offline/degraded)
- Health percentage
- Response times
- Error counts

### 4. Custom Alerts

Send custom alerts from your application:

```bash
curl -X POST http://localhost:8888/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "service": "alba",
    "severity": "warning",
    "title": "High Memory Usage",
    "message": "ALBA service memory usage at 85%",
    "details": {
      "memory_used": "1.7GB",
      "memory_total": "2GB",
      "threshold": "80%"
    }
  }'
```

### 5. Deployment Notifications

Notify team when deployments happen:

```bash
curl -X POST http://localhost:8888/notify-deployment \
  -H "Content-Type: application/json" \
  -d '{
    "service": "alba",
    "version": "v1.2.3",
    "environment": "production",
    "status": "success",
    "details": "Deployed new telemetry ingestion service"
  }'
```

### 6. Metric Threshold Alerts

Alert when metrics exceed thresholds:

```bash
curl -X POST http://localhost:8888/metric-alert \
  -H "Content-Type: application/json" \
  -d '{
    "service": "albi",
    "metric_name": "response_time_ms",
    "value": 1250,
    "threshold": 1000,
    "status": "warning"
  }'
```

---

## 🔧 Configuration

### Environment Variables

```powershell
# Set in PowerShell before starting
$env:SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
$env:SLACK_BOT_TOKEN = "xoxb-your-bot-token"
$env:SLACK_CHANNEL = "#kloud-monitoring"
$env:SLACK_PORT = 8888

# Or set in system environment
[Environment]::SetEnvironmentVariable("SLACK_WEBHOOK_URL", "...", "User")
```

### Service Monitoring Interval

Default: 60 seconds

To change, edit `slack_integration_service.py`:
```python
await asyncio.sleep(60)  # Change to desired interval
```

### Threshold Settings

Customize alert thresholds by modifying service URLs in config:

```python
SERVICE_URLS = {
    "alba": "http://localhost:5555",
    "albi": "http://localhost:6666",
    "jona": "http://localhost:7777",
    "orchestrator": "http://localhost:9999",
    "api": "http://localhost:8000",
}
```

---

## 📡 API Reference

### Endpoints

#### GET `/health`
Check Slack integration health
```bash
curl http://localhost:8888/health
```

Response:
```json
{
  "service": "slack-integration",
  "status": "operational",
  "webhook_configured": true,
  "timestamp": "2025-01-15T10:30:00"
}
```

#### GET `/service-health`
Get all services health status
```bash
curl http://localhost:8888/service-health
```

Response:
```json
{
  "timestamp": "2025-01-15T10:30:00",
  "services": {
    "alba": {
      "status": "online",
      "health": 1.0,
      "url": "http://localhost:5555"
    },
    "albi": {
      "status": "online",
      "health": 1.0,
      "url": "http://localhost:6666"
    }
  },
  "summary": {
    "total": 5,
    "online": 5,
    "offline": 0
  }
}
```

#### GET `/status-report`
Generate and send status report to Slack
```bash
curl -X GET http://localhost:8888/status-report
```

Response:
```json
{
  "status": "report_sent",
  "services": { ... },
  "timestamp": "2025-01-15T10:30:00"
}
```

#### POST `/send-alert`
Send custom alert to Slack
```bash
curl -X POST http://localhost:8888/send-alert \
  -H "Content-Type: application/json" \
  -d '{
    "service": "alba",
    "severity": "critical",
    "title": "Alert Title",
    "message": "Alert message",
    "details": { "key": "value" }
  }'
```

#### POST `/send-message`
Send custom message to Slack
```bash
curl -X POST http://localhost:8888/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#kloud-monitoring",
    "text": "Custom message",
    "blocks": [ ... ]
  }'
```

#### POST `/metric-alert`
Alert when metric exceeds threshold
```bash
curl -X POST http://localhost:8888/metric-alert \
  -H "Content-Type: application/json" \
  -d '{
    "service": "albi",
    "metric_name": "response_time_ms",
    "value": 1250,
    "threshold": 1000,
    "status": "warning"
  }'
```

#### POST `/notify-deployment`
Send deployment notification
```bash
curl -X POST http://localhost:8888/notify-deployment \
  -H "Content-Type: application/json" \
  -d '{
    "service": "alba",
    "version": "v1.2.3",
    "environment": "production",
    "status": "success",
    "details": "Description"
  }'
```

---

## 🔄 Integration Examples

### Python Integration

```python
import requests
import json

SLACK_SERVICE_URL = "http://localhost:8888"

def send_alert(service, severity, title, message):
    """Send alert to Slack"""
    payload = {
        "service": service,
        "severity": severity,
        "title": title,
        "message": message
    }
    
    response = requests.post(
        f"{SLACK_SERVICE_URL}/send-alert",
        json=payload
    )
    
    return response.json()

def send_status_report():
    """Send status report to Slack"""
    response = requests.get(f"{SLACK_SERVICE_URL}/status-report")
    return response.json()

# Usage
send_alert("alba", "critical", "High CPU", "ALBA using 95% CPU")
send_status_report()
```

### Node.js Integration

```javascript
const axios = require('axios');

const SLACK_SERVICE_URL = 'http://localhost:8888';

async function sendAlert(service, severity, title, message) {
  try {
    const response = await axios.post(`${SLACK_SERVICE_URL}/send-alert`, {
      service,
      severity,
      title,
      message
    });
    return response.data;
  } catch (error) {
    console.error('Failed to send alert:', error);
  }
}

async function sendStatusReport() {
  try {
    const response = await axios.get(`${SLACK_SERVICE_URL}/status-report`);
    return response.data;
  } catch (error) {
    console.error('Failed to get status report:', error);
  }
}

// Usage
sendAlert('albi', 'warning', 'High Latency', 'Response time exceeded 2s');
sendStatusReport();
```

### Bash Integration

```bash
#!/bin/bash

SLACK_URL="http://localhost:8888"

send_alert() {
  local service=$1
  local severity=$2
  local title=$3
  local message=$4
  
  curl -X POST "$SLACK_URL/send-alert" \
    -H "Content-Type: application/json" \
    -d "{
      \"service\": \"$service\",
      \"severity\": \"$severity\",
      \"title\": \"$title\",
      \"message\": \"$message\"
    }"
}

send_status_report() {
  curl -X GET "$SLACK_URL/status-report"
}

# Usage
send_alert "jona" "critical" "Service Down" "JONA synthesis service offline"
send_status_report
```

---

## 🔒 Security

### Webhook URL Security

- **NEVER** commit webhook URLs to version control
- Store in environment variables or secure vaults
- Rotate webhooks periodically
- Use app-level tokens with minimal permissions

### Bot Token Security

If using bot tokens:
- Use token scoping (minimal required permissions)
- Store securely (AWS Secrets Manager, Azure Key Vault, etc.)
- Implement rate limiting
- Log all Slack API calls

---

## 🚨 Troubleshooting

### Webhook Not Working

```powershell
# Test webhook directly
$webhook = "YOUR_WEBHOOK_URL"
$payload = @{
    text = "Test message"
} | ConvertTo-Json

Invoke-WebRequest -Uri $webhook -Method Post -Body $payload
```

### Services Not Detecting as Online

1. Check service is running:
```bash
curl http://localhost:5555/health
curl http://localhost:6666/health
curl http://localhost:7777/health
```

2. Check port accessibility
3. Review Slack service logs

### Alerts Not Appearing in Slack

1. Verify webhook URL is correct
2. Check channel permissions
3. Review FastAPI logs
4. Test webhook connectivity

### High Alert Volume

To reduce alerts:
1. Increase monitoring interval (default: 60s)
2. Add alert deduplication
3. Implement alert aggregation
4. Use severity filtering

---

## 📈 Monitoring Dashboard

Access Slack integration monitoring at:
```
http://localhost:8888/status-report
```

This sends a comprehensive dashboard to your Slack channel with:
- All service status
- Health percentages
- Last update times
- Any active alerts

---

## 🔄 Integration with CI/CD

### GitHub Actions

```yaml
- name: Send Deployment Notification
  run: |
    curl -X POST http://localhost:8888/notify-deployment \
      -H "Content-Type: application/json" \
      -d '{
        "service": "api",
        "version": "${{ github.ref }}",
        "environment": "production",
        "status": "success",
        "details": "Deployed from commit ${{ github.sha }}"
      }'
```

### GitLab CI

```yaml
notify_slack:
  script:
    - curl -X POST http://localhost:8888/notify-deployment
      -H "Content-Type: application/json"
      -d '{"service":"api","version":"'$CI_COMMIT_SHA'","status":"success"}'
```

---

## 📞 Support

For issues or questions:
1. Check logs in `slack_integration_service.py`
2. Verify webhook URL and channel permissions
3. Test individual endpoints
4. Review API examples

---

## 🎯 Next Steps

1. ✅ Set up Slack webhook
2. ✅ Start Slack integration service
3. ✅ Verify webhook test message
4. ✅ Integrate with your services
5. ✅ Configure alert thresholds
6. ✅ Set up custom alerts
7. ✅ Monitor via Slack dashboard

---

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** 2025-01-15

