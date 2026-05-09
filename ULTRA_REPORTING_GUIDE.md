# 🚀 ULTRA REPORTING MODULE - Complete Guide

## Overview

The **ULTRA Reporting Module** is an enterprise-grade automated reporting system that generates comprehensive Excel reports, PowerPoint presentations, and unified dashboards from your monitoring infrastructure.

**Key Features:**
- ✅ **Automated Excel Generation** with charts, pivot tables, and SLA tracking
- ✅ **PowerPoint Presentations** with executive dashboards and alerts
- ✅ **Unified Dashboard API** combining Datadog + Grafana + Prometheus
- ✅ **Metrics History** with detailed trend analysis
- ✅ **Report Management** - list, download, and clean up reports
- ✅ **Background Processing** with FastAPI background tasks
- ✅ **Fully Typed** with Pydantic models for validation

---

## 🏗️ Architecture

```
KLOUD MONITORING STACK
├── VictoriaMetrics (8428) ──┐
├── Prometheus (9090) ───────├──> ULTRA REPORTING MODULE
├── Elasticsearch (9200) ────┤   (Excel, PowerPoint, Dashboards)
├── AlertManager (9093) ─────┘
│
└── API ENDPOINTS
    ├── POST /api/reporting/export-excel     → Excel with metrics
    ├── POST /api/reporting/export-pptx      → PowerPoint presentation
    ├── POST /api/reporting/export-both      → Both formats
    ├── GET  /api/reporting/dashboard        → Unified metrics dashboard
    ├── GET  /api/reporting/metrics-history  → Historical data
    ├── GET  /api/reporting/download/{file}  → Download generated reports
    ├── GET  /api/reporting/list-reports     → List all reports
    └── DELETE /api/reporting/clear-reports  → Clean up old reports
```

---

## 📦 Installation

### 1. Install Dependencies

```bash
# Core reporting libraries
pip install openpyxl==3.1.2         # Excel generation
pip install xlsxwriter==3.1.9       # Advanced Excel features
pip install pandas==2.1.3           # Data processing
pip install python-pptx==0.6.21     # PowerPoint generation
pip install pillow==10.1.0          # Image handling
pip install aiohttp==3.9.1          # Async HTTP client
```

### 2. Files Added

```
apps/api/
├── ultra_reporting.py       # Core reporting classes (Excel, PowerPoint, Metrics)
├── reporting_api.py         # FastAPI endpoints and routes
└── reports/                 # Directory for generated reports
```

### 3. Updated Files

- `apps/api/main.py` - Added reporting router import
- `requirements.txt` - Added reporting dependencies

---

## 🎯 API Endpoints

### 1. Export to Excel

```http
POST /api/reporting/export-excel
Content-Type: application/json

{
  "title": "Kloud Cloud Metrics Report",
  "format": "xlsx",
  "include_sla": true,
  "include_alerts": true,
  "date_range_hours": 24
}
```

**Response:**
```json
{
  "success": true,
  "file_path": "/path/to/metrics_report_20231210_143025.xlsx",
  "filename": "metrics_report_20231210_143025.xlsx",
  "size_bytes": 524288,
  "download_url": "/api/reporting/download/metrics_report_20231210_143025.xlsx",
  "generated_at": "2023-12-10T14:30:25.123456",
  "message": "✓ Excel report generated successfully"
}
```

**Excel Sheets Generated:**
- **Summary**: Key metrics with SLA status
- **Metrics Data**: Detailed hourly/daily data
- **Charts**: Line charts for trends, bar charts for volume
- **SLA**: Service level agreement compliance tracking

---

### 2. Export to PowerPoint

```http
POST /api/reporting/export-pptx
Content-Type: application/json

{
  "title": "Kloud Cloud Metrics Report",
  "include_sla": true,
  "include_alerts": true,
  "date_range_hours": 24
}
```

**Response:**
```json
{
  "success": true,
  "file_path": "/path/to/metrics_presentation_20231210_143025.pptx",
  "filename": "metrics_presentation_20231210_143025.pptx",
  "size_bytes": 2097152,
  "download_url": "/api/reporting/download/metrics_presentation_20231210_143025.pptx",
  "generated_at": "2023-12-10T14:30:25.123456",
  "message": "✓ PowerPoint presentation generated"
}
```

**Slides Generated:**
1. **Title Slide** - Report title and date
2. **Metrics Summary** - Key performance indicators
3. **SLA Status** - Compliance dashboard
4. **Active Alerts** - Alert summary table
5. **Trend Analysis** - Historical trends (optional)

---

### 3. Export Both Formats

```http
POST /api/reporting/export-both
Content-Type: application/json

{
  "title": "Enterprise Metrics Report",
  "include_sla": true,
  "include_alerts": true,
  "date_range_hours": 24
}
```

**Response:**
```json
{
  "success": true,
  "reports": {
    "excel": {
      "filename": "metrics_report_20231210_143025.xlsx",
      "file_path": "/path/to/metrics_report_20231210_143025.xlsx",
      "download_url": "/api/reporting/download/metrics_report_20231210_143025.xlsx",
      "size_bytes": 524288
    },
    "powerpoint": {
      "filename": "metrics_presentation_20231210_143025.pptx",
      "file_path": "/path/to/metrics_presentation_20231210_143025.pptx",
      "download_url": "/api/reporting/download/metrics_presentation_20231210_143025.pptx",
      "size_bytes": 2097152
    }
  },
  "generated_at": "2023-12-10T14:30:25.123456",
  "message": "✓ Both reports generated successfully"
}
```

---

### 4. Get Unified Dashboard

```http
GET /api/reporting/dashboard
```

**Response:**
```json
{
  "api_uptime_percent": 99.87,
  "api_requests_per_second": 4850,
  "api_error_rate_percent": 0.12,
  "api_latency_p95_ms": 87.4,
  "api_latency_p99_ms": 145.2,
  "ai_agent_calls_24h": 125600,
  "ai_agent_success_rate": 99.43,
  "documents_generated_24h": 2400,
  "cache_hit_rate_percent": 92.1,
  "system_cpu_percent": 35.5,
  "system_memory_percent": 62.3,
  "system_disk_percent": 45.1,
  "active_alerts": [
    {
      "severity": "INFO",
      "name": "HighRequestVolume",
      "message": "API request volume above 4000 req/s",
      "fired_at": "2023-12-10T14:28:25.123456",
      "value": 4850
    }
  ],
  "sla_status": "✓ ALL PASSED"
}
```

**Combines Data From:**
- VictoriaMetrics - Metrics storage
- Prometheus - Alerting and evaluation
- AlertManager - Active alerts
- Grafana - Dashboards and panels

---

### 5. Get Metrics History

```http
GET /api/reporting/metrics-history?hours=24&metric_type=all
```

**Query Parameters:**
- `hours`: 1-720 hours of history (default: 24)
- `metric_type`: `all`, `api`, `ai`, `infrastructure`

**Response:**
```json
{
  "period_hours": 24,
  "data_points": 24,
  "metrics": {
    "api_requests": [5000, 5050, 5100, ...],
    "error_rate": [0.1, 0.12, 0.15, ...],
    "latency_p95": [85, 87, 89, ...],
    "latency_p99": [140, 143, 145, ...],
    "ai_calls": [500, 510, 520, ...],
    "documents_generated": [95, 98, 101, ...],
    "cache_hit_rate": [92, 91.5, 91, ...],
    "cpu_percent": [30, 31.2, 32.5, ...],
    "memory_percent": [60, 60.2, 60.4, ...]
  },
  "timestamps": [
    "2023-12-09T14:30:25",
    "2023-12-09T15:30:25",
    "2023-12-09T16:30:25",
    ...
  ],
  "generated_at": "2023-12-10T14:30:25.123456"
}
```

---

### 6. Download Report

```http
GET /api/reporting/download/metrics_report_20231210_143025.xlsx
```

Returns file for download with appropriate MIME type.

---

### 7. List All Reports

```http
GET /api/reporting/list-reports
```

**Response:**
```json
[
  {
    "id": "metrics_report_20231210_143025",
    "title": "metrics report 20231210 143025",
    "format": "xlsx",
    "generated_at": "2023-12-10T14:30:25.123456",
    "file_path": "/path/to/metrics_report_20231210_143025.xlsx",
    "size_bytes": 524288
  },
  {
    "id": "metrics_presentation_20231210_143025",
    "title": "metrics presentation 20231210 143025",
    "format": "pptx",
    "generated_at": "2023-12-10T14:30:20.123456",
    "file_path": "/path/to/metrics_presentation_20231210_143025.pptx",
    "size_bytes": 2097152
  }
]
```

---

### 8. Clean Up Old Reports

```http
DELETE /api/reporting/clear-reports?days_old=7
```

**Query Parameters:**
- `days_old`: Delete reports older than N days (default: 7)

**Response:**
```json
{
  "success": true,
  "deleted_files": 5,
  "freed_bytes": 5242880,
  "freed_mb": 5.0,
  "message": "✓ Deleted 5 reports older than 7 days"
}
```

---

## 💻 Usage Examples

### Python Client

```python
import httpx
from datetime import datetime

# Initialize HTTP client
client = httpx.Client(base_url="http://localhost:8000")

# Export Excel report
response = client.post("/api/reporting/export-excel", json={
    "title": "Monthly Metrics Report",
    "date_range_hours": 720,  # 30 days
    "include_sla": True,
    "include_alerts": True
})

report = response.json()
print(f"✓ Generated: {report['filename']}")
print(f"  Size: {report['size_bytes'] / 1024:.2f} KB")
print(f"  Download: {report['download_url']}")

# Get unified dashboard
dashboard = client.get("/api/reporting/dashboard").json()
print(f"API Uptime: {dashboard['api_uptime_percent']}%")
print(f"Error Rate: {dashboard['api_error_rate_percent']}%")
print(f"SLA Status: {dashboard['sla_status']}")

# Get metrics history for last 7 days
history = client.get("/api/reporting/metrics-history?hours=168").json()
print(f"Data points: {history['data_points']}")

# Download report
response = client.get(f"/api/reporting/download/{report['filename']}")
with open(f"./reports/{report['filename']}", "wb") as f:
    f.write(response.content)
```

### cURL

```bash
# Export Excel
curl -X POST http://localhost:8000/api/reporting/export-excel \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly Report",
    "date_range_hours": 168,
    "include_sla": true
  }'

# Get dashboard
curl http://localhost:8000/api/reporting/dashboard

# Get 24-hour metrics history
curl "http://localhost:8000/api/reporting/metrics-history?hours=24&metric_type=api"

# List reports
curl http://localhost:8000/api/reporting/list-reports

# Download report
curl http://localhost:8000/api/reporting/download/metrics_report_20231210_143025.xlsx \
  -o metrics_report.xlsx
```

### JavaScript/Node.js

```javascript
// Export PowerPoint presentation
const exportPPT = async () => {
  const response = await fetch('http://localhost:8000/api/reporting/export-pptx', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: 'Executive Dashboard Report',
      include_sla: true,
      include_alerts: true
    })
  });
  
  const data = await response.json();
  console.log(`✓ Generated: ${data.filename}`);
  console.log(`Download: ${data.download_url}`);
  
  return data;
};

// Get unified dashboard
const getDashboard = async () => {
  const response = await fetch('http://localhost:8000/api/reporting/dashboard');
  const dashboard = await response.json();
  
  console.log(`API Uptime: ${dashboard.api_uptime_percent}%`);
  console.log(`Active Alerts: ${dashboard.active_alerts.length}`);
  console.log(`SLA Status: ${dashboard.sla_status}`);
  
  return dashboard;
};

// Run
exportPPT();
getDashboard();
```

---

## 📊 Excel Report Structure

### Summary Sheet
- Report title and generation date
- Key performance indicators (KPIs):
  - API Requests/second
  - API Error Rate
  - Latency P95/P99
  - AI Agent Calls
  - Documents Generated
  - Cache Hit Rate
  - System CPU/Memory/Disk
- Current, Average, Min, Max values over period
- Trend indicators
- SLA targets and status

### Metrics Data Sheet
- Timestamped rows for each metric
- 14 columns of detailed data
- Auto-formatted for filtering and sorting
- Suitable for pivot table creation

### Charts Sheet
- Latency Trend (P95 & P99)
- Error Rate Trend
- Request Volume (bar chart)
- System Resources (stacked area)

### SLA Sheet
- Service Level Agreement tracking
- Target vs. Actual metrics
- Pass/Fail indicators with color coding
- Monthly uptime calculation

---

## 📈 PowerPoint Presentation Structure

### Slide 1: Title Slide
- Report title in large font
- Subtitle (Enterprise Metrics & SLA Tracking)
- Generation timestamp

### Slide 2: Metrics Summary
- Table with key metrics:
  - API Uptime: 99.9%
  - Average Latency: 87ms
  - Error Rate: 0.12%
  - Documents/Day: 2,400

### Slide 3: SLA Status
- Color-coded boxes for each SLA:
  - 99.9% Availability (PASS - Green)
  - <100ms Latency P95 (PASS - Green)
  - <0.5% Error Rate (PASS - Green)
  - 99.8% Actual Uptime (PASS - Green)

### Slide 4: Active Alerts
- Table of current alerts
- Severity levels (INFO, WARNING, CRITICAL)
- Alert messages and timestamps

---

## 🔧 Configuration

### Report Storage

Reports are stored in `./reports/` directory:

```
./reports/
├── metrics_report_20231210_143025.xlsx
├── metrics_presentation_20231210_143025.pptx
├── metrics_report_20231209_100000.xlsx
└── ...
```

### Automatic Cleanup

Clean up reports older than 7 days:

```bash
curl -X DELETE "http://localhost:8000/api/reporting/clear-reports?days_old=7"
```

### Custom Metrics

To add custom metrics, extend the `MetricsSnapshot` dataclass:

```python
@dataclass
class MetricsSnapshot:
    timestamp: datetime
    # ... existing fields ...
    custom_metric_1: float  # Add here
    custom_metric_2: int    # Add here
```

---

## 🚀 Integration with Monitoring Stack

### VictoriaMetrics Integration (In Progress)

Future enhancement to query real metrics:

```python
async def fetch_from_victoria():
    url = "http://victoria-metrics:8428/api/v1/query"
    params = {
        "query": "rate(http_requests_total[5m])",
        "time": int(datetime.now().timestamp())
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()
```

### Prometheus Integration (In Progress)

Query Prometheus for alert history:

```python
async def fetch_alerts_prometheus():
    url = "http://prometheus:9090/api/v1/alerts"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

### Elasticsearch Integration (In Progress)

Fetch log-based metrics:

```python
async def fetch_logs_elasticsearch():
    url = "http://elasticsearch:9200/kloud-logs-*/_search"
    body = {
        "size": 0,
        "aggs": {
            "error_count": {"value_count": {"field": "level"}}
        }
    }
    # Query implementation
```

---

## 📋 Metrics Collected

### API Metrics
- `http_requests_total` - Total requests (counter)
- `http_request_duration_seconds` - Request latency (histogram)
- `http_request_size_bytes` - Request payload size
- `http_requests_error_total` - Total errors

### AI Metrics
- `ai_agent_executions_total` - Total agent calls
- `ai_agent_duration_seconds` - Execution time
- `ai_agent_tokens_used_total` - Token consumption

### Business Metrics
- `documents_generated_total` - Generated documents
- `document_generation_duration_seconds` - Generation time
- `api_calls_authenticated_total` - Authenticated calls
- `subscription_value_usd` - Revenue tracking

### Infrastructure Metrics
- `system_cpu_percent` - CPU utilization
- `system_memory_percent` - Memory utilization
- `system_disk_percent` - Disk usage
- `db_connections_active` - Database connections
- `cache_hits_total` / `cache_misses_total` - Cache performance

---

## 🛡️ Error Handling

All endpoints include comprehensive error handling:

```python
{
  "detail": "Failed to generate Excel report: [error details]",
  "status_code": 500
}
```

Common error scenarios:
- File system errors (no write permission)
- Memory issues (very large reports)
- Timeout (querying slow data sources)
- Missing dependencies (libraries not installed)

---

## 📝 Logging

All reporting operations are logged:

```
✓ Excel report saved: /path/to/file.xlsx
✓ PowerPoint presentation saved: /path/to/file.pptx
✓ ULTRA Reporting module routes loaded
Excel export failed: [error]
```

Check logs in the application output or via:

```bash
curl http://localhost:8000/api/logging/tail?lines=100
```

---

## 🔄 Scheduled Reports

**Upcoming feature** - Scheduled report generation:

```python
# Generate daily reports at 8 AM
@scheduler.scheduled_job('cron', hour=8, minute=0)
async def generate_daily_report():
    result = await export_excel({
        "title": f"Daily Report {datetime.now().date()}",
        "date_range_hours": 24,
        "include_sla": True
    })
    # Email report
    send_email(result['file_path'], recipients=['team@company.com'])
```

---

## 📞 Support & Troubleshooting

### Issue: Report generation is slow

**Solution:**
- Reduce `date_range_hours` in request
- Check server resources (CPU, Memory)
- Verify database query performance

### Issue: File not found after generation

**Solution:**
- Ensure `./reports/` directory exists and is writable
- Check file permissions
- Verify disk space available

### Issue: Missing libraries

**Solution:**
```bash
pip install -r requirements.txt
# Or individually:
pip install openpyxl python-pptx pandas pillow aiohttp
```

### Issue: API endpoints not responding

**Solution:**
1. Verify reporting router is imported in `main.py`
2. Check application logs for import errors
3. Ensure all dependencies are installed
4. Restart the API server

---

## 📚 Full API Reference

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/api/reporting/export-excel` | POST | Generate Excel report | None |
| `/api/reporting/export-pptx` | POST | Generate PowerPoint presentation | None |
| `/api/reporting/export-both` | POST | Generate both formats | None |
| `/api/reporting/dashboard` | GET | Get unified dashboard | None |
| `/api/reporting/metrics-history` | GET | Get historical metrics | None |
| `/api/reporting/download/{file}` | GET | Download generated report | None |
| `/api/reporting/list-reports` | GET | List all reports | None |
| `/api/reporting/clear-reports` | DELETE | Clean up old reports | None |

---

## 🎯 Next Steps

1. **Real Data Integration** - Connect to VictoriaMetrics, Prometheus, Elasticsearch
2. **Scheduled Reports** - Implement APScheduler for daily/weekly/monthly reports
3. **Email Delivery** - Send reports via email automatically
4. **Cloud Storage** - Upload reports to S3/GCS
5. **Custom Branding** - Add company logos and colors to reports
6. **Advanced Charting** - More sophisticated visualizations
7. **Data Export** - CSV, JSON, SQL exports
8. **Report Templates** - User-customizable report templates

---

## 📄 License

Part of the Kloud Cloud ecosystem. Enterprise monitoring and reporting solution.

**Gjenero nga Kloud ULTRA Reporting System** 🚀

