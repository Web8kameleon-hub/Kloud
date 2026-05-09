# ASI-API Quick Reference

## Fast Access Endpoints

| Endpoint | Method | Purpose | Port |
|----------|--------|---------|------|
| `/health` | GET | API health check | 8000 |
| `/api/system-status` | GET | Full system diagnostics | 8000 |
| `/api/brain/youtube-insight` | POST | YouTube content analysis | 8000 |
| `/api/brain/energy-check` | POST | Energy consumption analysis | 8000 |
| `/api/brain/cortex-map` | POST | Neural network topology | 8000 |
| `/api/signals/neural-synthesis` | POST | Generate synthetic signals | 8000 |
| `/api/signals/process-audio` | POST | Audio processing & analysis | 8000 |
| `/api/status/services` | GET | Individual service status | 8000 |
| `/api/metrics` | GET | System metrics | 8000 |
| `/docs` | GET | Interactive API documentation | 8000 |
| `/redoc` | GET | ReDoc API documentation | 8000 |
| `/openapi.json` | GET | OpenAPI schema | 8000 |

---

## Common Tasks

### Check if System is Running

```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/health' | Select-Object StatusCode
```

### Get Full System Status

```powershell
$status = Invoke-WebRequest -Uri 'http://localhost:8000/api/system-status' -UseBasicParsing
$status.Content | ConvertFrom-Json | Format-Table
```

### Test YouTube Analysis API

```powershell
$body = @{
    video_id = "dQw4w9WgXcQ"
    analysis_type = "full"
    include_sentiment = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8000/api/brain/youtube-insight' `
    -Method POST `
    -Body $body `
    -ContentType 'application/json'
```

### Check Energy Usage

```powershell
$body = @{
    component = "api"
    analysis_depth = "detailed"
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8000/api/brain/energy-check' `
    -Method POST `
    -Body $body `
    -ContentType 'application/json'
```

### Get All Services Status

```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/api/status/services' | ConvertFrom-Json | ConvertTo-Json
```

### Run Full Test Suite

```powershell
cd c:\kloud-cloud
.\scripts\test-cycle.ps1
```

---

## Port Reference

| Service | Port | Protocol |
|---------|------|----------|
| API Backend | 8000 | HTTP/REST |
| MESH Network | 7777 | TCP |
| ORCH Manager | 5555 | TCP |
| Frontend | 3000 | HTTP/Next.js |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| Neo4j | 7687 | Bolt |

---

## Service Management

### View Running Services

```powershell
Get-Job
```

### View Service Logs (Last 20 lines)

```powershell
Get-Content logs/api-*.log -Tail 20
```

### Restart a Service

```powershell
Stop-Job -Name <job-name>
.\scripts\start-all.ps1
```

### Stop All Services

```powershell
Get-Job | Stop-Job
```

---

## Response Status Codes

| Code | Status | Meaning |
|------|--------|---------|
| 200 | OK | Successful request |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Permission denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many | Rate limit exceeded |
| 500 | Server Error | Internal error |
| 503 | Unavailable | Service down |

---

## Rate Limits

- **General API:** 100 req/min per IP
- **Brain Intelligence:** 10 req/min per endpoint
- **Signal Processing:** 20 req/min per endpoint

Check headers: `X-RateLimit-Remaining`

---

## Documentation Access

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json
- **Full Guide:** `ASI-API-GUIDE.md`

---

## Troubleshooting

### Service Not Responding

```powershell
Test-NetConnection -ComputerName localhost -Port 8000
```

### View System Diagnostics

```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/health/detailed' | ConvertFrom-Json
```

### Check Database Connections

```powershell
$status = Invoke-WebRequest -Uri 'http://localhost:8000/api/system-status' -UseBasicParsing
($status.Content | ConvertFrom-Json).database
```

### View Service Metrics

```powershell
Invoke-WebRequest -Uri 'http://localhost:8000/api/metrics?interval=24h' -UseBasicParsing | ConvertFrom-Json
```

---

**Created:** November 30, 2025
**System Version:** 1.0.0

