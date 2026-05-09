# Kloud Cloud - Complete API Reference (v1.0.0)

## Overview

**Base URL:** `http://localhost:8000`  
**Version:** 1.0.0  
**Format:** RESTful API with JSON responses  
**Documentation:** [Interactive Docs](http://localhost:8000/docs)

---

## 🎯 Core System Endpoints

### Health & Status

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Quick health check | Optional |
| `/status` | GET | Full system status with metrics | Optional |
| `/api/system-status` | GET | Frontend API proxy for `/status` | Optional |
| `/health/detailed` | GET | Detailed health with response times | Optional |

### Service Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status/services` | GET | Individual service status |
| `/api/metrics` | GET | System metrics (1h, 24h, 7d) |
| `/brain/cortex-map` | GET | Neural network topology |
| `/brain/temperature` | GET | Per-module thermal stress |
| `/brain/queue` | GET | Queue metrics |
| `/brain/threads` | GET | Thread info & CPU usage |
| `/brain/neural-load` | GET | Industrial neural load |
| `/brain/errors` | GET | Real-time cognitive errors |
| `/brain/live` | GET | SSE stream (real-time metrics) |

### Database & Cache

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/db/ping` | GET | PostgreSQL connection test |
| `/redis/ping` | GET | Redis connection test |

---

## 🧠 Brain Intelligence Endpoints

### YouTube Analysis

**Endpoint:** `GET /brain/youtube/insight`

```json
{
  "video_id": "dQw4w9WgXcQ",
  "response": {
    "metadata": "...",
    "emotional_tone": "...",
    "core_insights": ["..."],
    "trend_potential": 0.85,
    "target_audience": "...",
    "recommended_brain_sync": "..."
  }
}
```

### Audio Analysis & Synthesis

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/brain/energy/check` | POST | Daily energy analysis from audio |
| `/brain/harmony` | POST | Harmonic structure analysis |
| `/brain/scan/harmonic` | POST | Harmonic personality scan (HPS) |
| `/brain/music/brainsync` | POST | Generate brain-sync music (6 modes) |
| `/brain/moodboard/generate` | POST | Neural moodboard from mood+content |
| `/brain/sync` | POST | Full neural-harmonic synchronization |

### Signal Generation

**Endpoint:** `POST /neural-symphony`

Generates WAV audio stream from synthetic EEG alpha wave

```bash
curl -X POST http://localhost:8000/neural-symphony \
  -H "Content-Type: application/json" \
  -d '{"frequency": 10, "duration": 5}' \
  --output eeg-signal.wav
```

### Brain Control

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/brain/restart` | POST | Safely restart cognitive modules |

---

## 💬 Conversational API

### Ask/Query Endpoint

**Endpoint:** `POST /api/ask`

Request:

```json
{
  "question": "What is the system status?",
  "context": "optional context string",
  "include_details": true
}
```

Response:

```json
{
  "answer": "The system is operational with...",
  "timestamp": "2025-11-30T14:44:00Z",
  "modules_used": ["brain", "cortex"],
  "processing_time_ms": 234,
  "details": { }
}
```

---

## 📤 Data Upload & Processing

### EEG Data Processing

**Endpoint:** `POST /api/uploads/eeg/process`

```bash
curl -X POST http://localhost:8000/api/uploads/eeg/process \
  -F "file=@eeg_recording.csv"
```

### Audio File Processing

**Endpoint:** `POST /api/uploads/audio/process`

```bash
curl -X POST http://localhost:8000/api/uploads/audio/process \
  -F "file=@audio_sample.wav"
```

---

## 💳 Billing & Payment Integration

### PayPal Integration

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/billing/paypal/order` | POST | Create PayPal order |
| `/billing/paypal/capture/{order_id}` | POST | Capture PayPal payment |

**Create Order:**

```json
{
  "intent": "CAPTURE",
  "purchase_units": [{
    "amount": {
      "currency_code": "EUR",
      "value": "10.00"
    }
  }]
}
```

### Stripe Integration

**Endpoint:** `POST /billing/stripe/payment-intent`

```json
{
  "amount": 1000,
  "currency": "eur",
  "payment_method_types": ["sepa_debit"],
  "description": "Payment description",
  "customer": "optional_customer_id",
  "metadata": { }
}
```

### SEPA Transfer (Bank API)

**Endpoint:** `POST /billing/sepa/initiate`

```json
{
  "debtor_iban": "DE89370400440532013000",
  "creditor_iban": "FR1420041010050500013M02606",
  "amount": "100.00",
  "currency": "EUR",
  "remittance_information": "Payment description"
}
```

**Status:** 501 (Not Implemented - awaiting bank API configuration)

---

## 📊 ALBA Data Collection Module

### Stream Management

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/alba/status` | GET | ALBA module status |
| `/api/alba/streams/start` | POST | Start data collection stream |
| `/api/alba/streams/{stream_id}/stop` | POST | Stop data stream |
| `/api/alba/streams` | GET | Get all active streams |
| `/api/alba/streams/{stream_id}/data` | GET | Get stream data (with limit) |

### Configuration & Metrics

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/alba/config` | POST | Update collection config |
| `/api/alba/metrics` | GET | Collection metrics |
| `/api/alba/health` | GET | ALBA health check |

**Start Stream Request:**

```json
{
  "stream_id": "eeg_session_001",
  "description": "Morning EEG recording",
  "sampling_rate_hz": 256,
  "channels": ["fp1", "fp2", "cz", "pz"],
  "metadata": { "user_id": "123" }
}
```

---

## 🤖 ASI Trinity System

### System Status

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/asi/status` | GET | ASI Trinity status |
| `/asi/health` | GET | ASI system health |

### Command Execution

**Endpoint:** `POST /asi/execute`

```json
{
  "command": "analyze",
  "agent": "trinity",
  "parameters": {
    "input": "data",
    "mode": "full"
  }
}
```

---

## 🏠 Root Endpoints

| Endpoint | Method | Response |
|----------|--------|----------|
| `/` | GET | API root info |
| `/docs` | GET | Interactive Swagger UI |
| `/redoc` | GET | ReDoc documentation |
| `/openapi.json` | GET | OpenAPI 3.0 schema |

---

## 📋 Response Status Codes

| Code | Status | When |
|------|--------|------|
| **200** | OK | Successful request |
| **201** | Created | Resource created |
| **400** | Bad Request | Invalid parameters |
| **422** | Validation Error | Request validation failed |
| **500** | Internal Error | Server error |
| **501** | Not Implemented | Feature not available |
| **502** | Bad Gateway | Upstream error |
| **503** | Unavailable | Service down |

---

## 🔐 Authentication

**Current:** Optional internal header validation

...
x-Kloud-internal: 1
...

**Recommended Production:**

- JWT Bearer tokens
- API key validation
- OAuth 2.0

---

## ⚡ Rate Limiting

...
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1701355440
....

**Limits:**

- General API: 100 req/min per IP
- Brain endpoints: 10 req/min per endpoint
- Signal processing: 20 req/min per endpoint

---

## 🔍 Error Format

All errors return:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": "Additional details",
    "timestamp": "2025-11-30T14:44:00Z",
    "request_id": "req_1234567890"
  }
}
```

---

## 📡 WebSocket Support

**Stream:** `WS /ws/signals`

Real-time signal streaming:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/signals');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Signal:', data);
};
```

---

## 🧪 Testing Endpoints

### Quick Tests

```bash
# Health check
curl http://localhost:8000/health

# Full status
curl http://localhost:8000/status

# System status
curl http://localhost:8000/api/system-status

# YouTube analysis
curl http://localhost:8000/brain/youtube/insight?video_id=dQw4w9WgXcQ

# Ask question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the system status?"}'
```

### PowerShell Tests

```powershell
# Test health
Invoke-WebRequest -Uri 'http://localhost:8000/health' | ConvertFrom-Json

# Get full status
$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/system-status'
$response.Content | ConvertFrom-Json | Format-Table

# Run test cycle
.\scripts\test-cycle.ps1
```

---

## 📚 Complete Endpoint Summary

**Total Endpoints:** 60+

### By Category

- **Core System:** 8 endpoints
- **Brain Intelligence:** 12 endpoints
- **Data Collection:** 9 endpoints
- **Payment/Billing:** 5 endpoints
- **Database:** 2 endpoints
- **ASI Trinity:** 2 endpoints
- **Media Upload:** 2 endpoints
- **Utility:** 20+ endpoints

---

## 🚀 Quick Start

1. **Verify System:**

   ```powershell
   .\scripts\test-cycle.ps1
   ```

2. **Access Documentation:**
   - Interactive: http: //localhost:8000/docs
   - ReDoc: http: //localhost:8000/redoc

3. **Test API:**

   ```bash
   curl http://localhost:8000/health
   ```

4. **Start Building:**
   - Use endpoints from this guide
   - Check OpenAPI docs for detailed schemas
   - See examples in the guide

---

**Generated:** November 30, 2025  
**Version:** 1.0.0  
**Status:** ✅ All Systems Operational

