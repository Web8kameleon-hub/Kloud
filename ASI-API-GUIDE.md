# Kloud Cloud - ASI-API Documentation

## Overview

The **ASI-API** (Advanced System Intelligence API) is the core REST interface for the Kloud Cloud system. It provides comprehensive endpoints for neural processing, signal analysis, system monitoring, and intelligent operations.

**Base URL:** `http://localhost:8000`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [Health & Diagnostics](#health--diagnostics)
4. [Brain Intelligence](#brain-intelligence)
5. [Signal Processing](#signal-processing)
6. [System Status](#system-status)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [WebSocket Support](#websocket-support)
10. [Examples](#examples)

---

## Authentication

Currently, the API uses **internal header validation** for trusted services.

### Header Requirements (Optional)

```
x-Kloud-internal: 1
```

**Note:** Production deployment should implement:
- JWT Bearer tokens
- API key validation
- OAuth 2.0 integration

---

## Core Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Quick health status of the API

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-30T14:44:00Z",
  "uptime_seconds": 1234
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service degraded

---

### 2. System Status

**Endpoint:** `GET /api/system-status`

**Description:** Comprehensive system diagnostics and metrics

**Response:**
```json
{
  "system": {
    "status": "operational",
    "uptime": "2h 45m",
    "cpu_usage": 34.2,
    "memory_usage": 62.1,
    "disk_usage": 45.8
  },
  "services": {
    "api": { "status": "running", "port": 8000 },
    "mesh": { "status": "running", "port": 7777 },
    "orch": { "status": "running", "port": 5555 },
    "frontend": { "status": "running", "port": 3000 }
  },
  "database": {
    "postgres": "connected",
    "redis": "connected",
    "neo4j": "connected"
  },
  "timestamp": "2025-11-30T14:44:00Z"
}
```

---

## Health & Diagnostics

### 3. Detailed Health Check

**Endpoint:** `GET /health/detailed`

**Response:**
```json
{
  "api": {
    "status": "healthy",
    "response_time_ms": 2.3,
    "request_count": 1523
  },
  "database": {
    "postgres": { "status": "connected", "latency_ms": 1.2 },
    "redis": { "status": "connected", "latency_ms": 0.8 },
    "neo4j": { "status": "connected", "latency_ms": 3.1 }
  },
  "cache": {
    "hit_rate": 87.3,
    "size_mb": 245
  }
}
```

---

## Brain Intelligence

### 4. YouTube Insight Analysis

**Endpoint:** `POST /api/brain/youtube-insight`

**Description:** Analyze YouTube content using AI neural processing

**Request:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "analysis_type": "full",
  "include_sentiment": true,
  "include_topics": true
}
```

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Sample Video",
  "duration_seconds": 212,
  "analysis": {
    "sentiment": {
      "overall": 0.82,
      "label": "positive"
    },
    "topics": [
      { "name": "technology", "confidence": 0.95 },
      { "name": "innovation", "confidence": 0.88 }
    ],
    "summary": "Engaging content about emerging technologies..."
  },
  "timestamp": "2025-11-30T14:44:00Z"
}
```

---

### 5. Energy Analysis

**Endpoint:** `POST /api/brain/energy-check`

**Description:** Analyze system energy consumption and optimization

**Request:**
```json
{
  "component": "api",
  "analysis_depth": "detailed",
  "include_predictions": true
}
```

**Response:**
```json
{
  "component": "api",
  "current_consumption_watts": 245.3,
  "efficiency_score": 0.87,
  "optimization_suggestions": [
    "Enable connection pooling for 15% improvement",
    "Reduce cache TTL by 10% without performance impact"
  ],
  "predicted_24h_consumption_kwh": 5.89
}
```

---

### 6. Cortex Map Analysis

**Endpoint:** `POST /api/brain/cortex-map`

**Description:** Generate neural network topology and connectivity map

**Request:**
```json
{
  "depth": "full",
  "include_weights": true,
  "visualization": true
}
```

**Response:**
```json
{
  "nodes": 1247,
  "connections": 3891,
  "avg_connectivity": 3.12,
  "clusters": [
    {
      "id": "cluster_001",
      "size": 156,
      "density": 0.78,
      "role": "processing"
    }
  ],
  "visualization_url": "/api/brain/cortex-map/viz",
  "graph_data": { ... }
}
```

---

## Signal Processing

### 7. Neural Synthesis

**Endpoint:** `POST /api/signals/neural-synthesis`

**Description:** Generate synthetic neural signals

**Request:**
```json
{
  "signal_type": "eeg",
  "frequency_hz": 40,
  "amplitude": 0.8,
  "duration_seconds": 10,
  "pattern": "sine_wave"
}
```

**Response:**
```json
{
  "signal_id": "sig_1234567890",
  "type": "eeg",
  "frequency": 40,
  "samples": 40000,
  "data_url": "/api/signals/neural-synthesis/data/sig_1234567890",
  "created_at": "2025-11-30T14:44:00Z"
}
```

---

### 8. Audio Processing

**Endpoint:** `POST /api/signals/process-audio`

**Description:** Process and analyze audio signals

**Request:**
```multipart/form-data
audio_file: [binary]
analysis_type: "full"
sample_rate: 44100
```

**Response:**
```json
{
  "analysis": {
    "duration_seconds": 5.3,
    "sample_rate": 44100,
    "channels": 2,
    "frequency_spectrum": { ... },
    "mfcc_features": [ ... ],
    "detected_speech": true,
    "noise_level_db": -45.2
  },
  "processing_time_ms": 234
}
```

---

## System Status

### 9. Service Status

**Endpoint:** `GET /api/status/services`

**Response:**
```json
{
  "services": [
    {
      "name": "FastAPI Backend",
      "port": 8000,
      "status": "running",
      "uptime_seconds": 3456,
      "requests_total": 1523,
      "errors_24h": 2
    },
    {
      "name": "MESH Network",
      "port": 7777,
      "status": "running",
      "nodes_connected": 12,
      "traffic_mbps": 45.3
    },
    {
      "name": "ORCH Orchestrator",
      "port": 5555,
      "status": "running",
      "jobs_running": 3,
      "jobs_completed": 156
    },
    {
      "name": "Next.js Frontend",
      "port": 3000,
      "status": "running",
      "active_sessions": 42,
      "response_time_ms": 23
    }
  ]
}
```

---

### 10. Metrics

**Endpoint:** `GET /api/metrics`

**Query Parameters:**
- `interval`: `1h`, `24h`, `7d` (default: `24h`)
- `metrics`: comma-separated list

**Response:**
```json
{
  "interval": "24h",
  "timestamp": "2025-11-30T14:44:00Z",
  "metrics": {
    "requests_per_second": [23.4, 24.1, 22.8],
    "average_response_time_ms": [45, 48, 43],
    "error_rate": [0.002, 0.001, 0.003],
    "cache_hit_rate": [0.87, 0.89, 0.86]
  }
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request validation failed",
    "details": "Field 'analysis_type' is required",
    "timestamp": "2025-11-30T14:44:00Z",
    "request_id": "req_1234567890"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200  | OK | Successful request |
| 201  | Created | Resource created |
| 400  | Bad Request | Invalid parameters |
| 401  | Unauthorized | Missing authentication |
| 403  | Forbidden | Insufficient permissions |
| 404  | Not Found | Resource not found |
| 429  | Too Many Requests | Rate limit exceeded |
| 500  | Internal Server Error | Server error |
| 503  | Service Unavailable | Service down |

---

## Rate Limiting

**Limits:**
- **General API:** 100 requests/minute per IP
- **Brain Intelligence:** 10 requests/minute per endpoint
- **Signal Processing:** 20 requests/minute per endpoint

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1701355440
```

---

## WebSocket Support

### Real-time Signal Streaming

**Endpoint:** `WS /ws/signals`

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/signals');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New signal data:', data);
};
```

**Message Format:**
```json
{
  "type": "signal_update",
  "signal_id": "sig_1234567890",
  "timestamp": "2025-11-30T14:44:00.123Z",
  "values": [0.23, 0.45, 0.67, ...]
}
```

---

## Examples

### Example 1: Complete Health Check

```bash
curl -X GET http://localhost:8000/health \
  -H "Accept: application/json"
```

### Example 2: Analyze YouTube Content

```bash
curl -X POST http://localhost:8000/api/brain/youtube-insight \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "analysis_type": "full",
    "include_sentiment": true
  }'
```

### Example 3: Get System Status with PowerShell

```powershell
$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/system-status' \
  -Method GET \
  -Headers @{'Accept' = 'application/json'}

$response.Content | ConvertFrom-Json | Format-Table
```

### Example 4: Process Audio File

```bash
curl -X POST http://localhost:8000/api/signals/process-audio \
  -F "audio_file=@recording.wav" \
  -F "analysis_type=full" \
  -F "sample_rate=44100"
```

### Example 5: Stream Signals via WebSocket (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/signals');

ws.onopen = () => {
  console.log('Connected to signal stream');
  ws.send(JSON.stringify({
    action: 'subscribe',
    signal_type: 'eeg',
    sample_rate: 256
  }));
};

ws.onmessage = (event) => {
  const signal = JSON.parse(event.data);
  console.log(`Signal update at ${signal.timestamp}:`, signal.values);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

---

## Advanced Features

### Batch Processing

**Endpoint:** `POST /api/batch/process`

```json
{
  "operations": [
    {
      "id": "op_1",
      "endpoint": "/api/brain/youtube-insight",
      "method": "POST",
      "body": { "video_id": "video1" }
    },
    {
      "id": "op_2",
      "endpoint": "/api/brain/energy-check",
      "method": "POST",
      "body": { "component": "api" }
    }
  ]
}
```

### Webhooks

**Endpoint:** `POST /api/webhooks/register`

```json
{
  "event": "analysis_complete",
  "url": "https://your-service.com/webhook",
  "retry_policy": "exponential_backoff"
}
```

---

## Performance Tips

1. **Use Batch Endpoints** - Process multiple requests in one call
2. **Enable Caching** - Add appropriate cache headers
3. **Use Pagination** - For large result sets
4. **Connection Pooling** - Keep connections alive
5. **Compression** - Use gzip for large responses

---

## Support & Resources

- **OpenAPI Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Schema:** http://localhost:8000/openapi.json
- **Status Page:** http://localhost:8000/api/system-status
- **Test Cycle:** `.\scripts\test-cycle.ps1`

---

**Last Updated:** November 30, 2025
**Version:** 1.0.0

