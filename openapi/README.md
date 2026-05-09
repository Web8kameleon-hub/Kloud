# Kloud OpenAPI Contract Specifications

**Last Updated:** December 11, 2025  
**Platform Version:** 1.0.0  
**Status:** ✅ Contracts Defined

---

## 📄 Overview

This directory contains OpenAPI 3.1.0 specifications for all Kloud agent services. These contracts serve as the authoritative API documentation and enable:

- **API Documentation:** Auto-generated interactive docs (Swagger UI, ReDoc)
- **Client Generation:** Auto-generated SDKs for Python, TypeScript, Go, etc.
- **Contract Testing:** Validate requests/responses against schemas
- **Mock Servers:** Generate mock services for testing
- **API Governance:** Enforce consistency across microservices

---

## 🤖 Agent Service Contracts

### 1. Alba API (Port 5555)
**File:** `alba-api-v1.yaml`  
**Service:** Content generation and creative workflows  
**Endpoints:**
- `GET /health` - Health check
- `POST /content/generate` - Generate creative content
- `POST /frames/generate` - Generate animation frames
- `GET /tasks/{task_id}` - Get task status
- `POST /workflows/create` - Create multi-step workflow

**Key Features:**
- Async task processing with UUID tracking
- Frame-by-frame animation generation
- Multi-format output (MP4, WebM, PNG, JPG)
- Workflow orchestration

---

### 2. Albi API (Port 6666)
**File:** `albi-api-v1.yaml`  
**Service:** Data analytics and pattern detection  
**Endpoints:**
- `GET /health` - Health check
- `POST /analytics/process` - Process analytics data
- `POST /patterns/detect` - Detect patterns in data
- `POST /insights/generate` - Generate business insights
- `POST /correlations/analyze` - Analyze data correlations

**Key Features:**
- Real-time pattern detection (anomaly, trend, seasonality, clustering)
- Business intelligence insights (predictive, descriptive, prescriptive)
- Statistical correlation analysis (Pearson, Spearman, Kendall)
- Time-series analytics with customizable metrics

---

### 3. Jona API (Port 7777)
**File:** `jona-api-v1.yaml`  
**Service:** Neural audio generation and signal processing  
**Endpoints:**
- `GET /health` - Health check
- `POST /audio/generate` - Generate neural audio from EEG
- `POST /audio/upload` - Upload EEG data files
- `GET /audio/stream/{session_id}` - Real-time audio streaming
- `POST /signals/process` - Process multi-modal signals
- `POST /synthesis/create` - Create data synthesis
- `GET /tasks/{task_id}` - Get task status

**Key Features:**
- EEG-to-audio conversion
- Multi-channel signal processing (up to 256 channels)
- Real-time audio streaming
- Support for multiple signal types (EEG, ECG, EMG, generic)
- Multiple output formats (WAV, MP3, FLAC, OGG)
- Sample rates: 22.05kHz to 96kHz

---

## 🔐 Authentication

All agent services use **API Key authentication** via the `x-api-key` header.

### Example Request:
```bash
curl -X POST https://api.kloud.com/alba/content/generate \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "animation", "format": "mp4", "duration": 30}'
```

---

## 📊 Standard Response Codes

All services follow these HTTP status code conventions:

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful synchronous operation |
| 201 | Created | Resource created (workflows, uploads) |
| 202 | Accepted | Async task accepted for processing |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File upload exceeds size limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

---

## 🎯 Rate Limiting

All endpoints enforce rate limiting with the following headers:

```
X-RateLimit-Limit: 1000         # Requests per hour
X-RateLimit-Remaining: 987      # Remaining requests
X-RateLimit-Reset: 1702310400   # Unix timestamp when limit resets
```

**Default Limits:**
- **Free Tier:** 100 requests/hour
- **Pro Tier:** 1,000 requests/hour
- **Enterprise Tier:** 10,000 requests/hour

---

## 🔄 Async Task Pattern

Services that perform long-running operations (Alba, Jona) follow the async task pattern:

1. **Submit Request:** `POST /audio/generate` → Returns `202 Accepted` with `task_id`
2. **Poll Status:** `GET /tasks/{task_id}` → Returns task status and progress
3. **Retrieve Result:** When `status: completed`, result is available in response

### Example Flow:
```bash
# Step 1: Submit task
curl -X POST https://api.kloud.com/jona/audio/generate \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"signal_type": "eeg", "duration": 60}'
# Response: {"task_id": "550e8400-e29b-41d4-a716-446655440000", "status": "pending"}

# Step 2: Check status (poll every 2-5 seconds)
curl https://api.kloud.com/jona/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "x-api-key: YOUR_API_KEY"
# Response: {"task_id": "...", "status": "processing", "progress": 45.2}

# Step 3: Retrieve result
curl https://api.kloud.com/jona/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "x-api-key: YOUR_API_KEY"
# Response: {"task_id": "...", "status": "completed", "result": {"audio_url": "https://..."}}
```

---

## 🛠️ Client SDK Generation

### Generate Python SDK:
```bash
openapi-generator generate \
  -i openapi/alba-api-v1.yaml \
  -g python \
  -o clients/python/alba-sdk
```

### Generate TypeScript SDK:
```bash
openapi-generator generate \
  -i openapi/albi-api-v1.yaml \
  -g typescript-axios \
  -o clients/typescript/albi-sdk
```

### Generate Go SDK:
```bash
openapi-generator generate \
  -i openapi/jona-api-v1.yaml \
  -g go \
  -o clients/go/jona-sdk
```

---

## 📚 Interactive Documentation

### Swagger UI (Auto-generated from OpenAPI specs):
- **Alba:** http://localhost:5555/docs
- **Albi:** http://localhost:6666/docs
- **Jona:** http://localhost:7777/docs

### ReDoc (Alternative documentation UI):
- **Alba:** http://localhost:5555/redoc
- **Albi:** http://localhost:6666/redoc
- **Jona:** http://localhost:7777/redoc

---

## ✅ Contract Validation

### Validate OpenAPI Specs:
```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate specs
swagger-cli validate openapi/alba-api-v1.yaml
swagger-cli validate openapi/albi-api-v1.yaml
swagger-cli validate openapi/jona-api-v1.yaml
```

### Contract Testing with Dredd:
```bash
# Install Dredd
npm install -g dredd

# Test Alba service against contract
dredd openapi/alba-api-v1.yaml http://localhost:5555

# Test Albi service
dredd openapi/albi-api-v1.yaml http://localhost:6666

# Test Jona service
dredd openapi/jona-api-v1.yaml http://localhost:7777
```

---

## 🔄 Versioning Strategy

### Current Version: v1 (1.0.0)

**Semantic Versioning:**
- **Major (v2.0.0):** Breaking changes (endpoint removal, schema changes)
- **Minor (v1.1.0):** New features (new endpoints, optional fields)
- **Patch (v1.0.1):** Bug fixes, documentation updates

**Deprecation Policy:**
- Deprecated endpoints receive 6-month notice
- Old API versions supported for 12 months after deprecation
- Deprecation warnings in response headers:
  ```
  X-API-Deprecation: true
  X-API-Sunset: 2026-12-11T00:00:00Z
  ```

---

## 📋 Schema Validation Examples

### Valid Alba Request:
```json
{
  "type": "animation",
  "style": "modern",
  "duration": 30,
  "format": "mp4",
  "parameters": {
    "resolution": "1920x1080",
    "fps": 60
  }
}
```

### Valid Albi Request:
```json
{
  "dataset_id": "user_behavior_2025",
  "timeframe": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z"
  },
  "metrics": ["engagement_rate", "conversion_rate", "retention"]
}
```

### Valid Jona Request:
```json
{
  "signal_type": "eeg",
  "channels": 8,
  "duration": 60,
  "output_format": "wav",
  "parameters": {
    "sample_rate": 44100,
    "bit_depth": 16,
    "mood": "calm"
  }
}
```

---

## 🚀 Next Steps

### Immediate Actions:
1. **Enable FastAPI Auto-Documentation:**
   - Add `docs_url="/docs"` and `redoc_url="/redoc"` to FastAPI app initialization
   - Ensure Pydantic models match OpenAPI schemas

2. **Implement Contract Testing:**
   - Set up Dredd in CI/CD pipeline
   - Add automated contract validation on each deployment

3. **Generate Client SDKs:**
   - Create Python SDK for internal use
   - Create TypeScript SDK for web frontend
   - Publish SDKs to internal package registry

4. **Set Up API Gateway:**
   - Configure Kong/Tyk to enforce rate limits
   - Add request/response validation middleware
   - Implement API key rotation

### Future Enhancements:
- [ ] Add webhook support for async task completion
- [ ] Implement GraphQL gateway for unified API access
- [ ] Add pagination standards for list endpoints
- [ ] Create composite API specs (multi-agent workflows)
- [ ] Add performance SLAs to contracts (p95 response times)

---

## 📞 Support

**Documentation:** API_DOCS.md  
**Contract Issues:** Open GitHub issue with `openapi` label  
**Contact:** Ledjan Ahmati (LedjanAhmati/Kloud-cloud)  

---

**Last Updated:** December 11, 2025  
**Maintained By:** Kloud Engineering Team

