# 🔌 Kloud Cloud - API Reference

## Base URLs

| Environment | URL |
|-------------|-----|
| Production | `https://api.kloud.cloud/v1` |
| Staging | `https://staging-api.kloud.cloud/v1` |
| Development | `http://localhost:8000/v1` |

## Authentication

All API requests require authentication via Bearer token.

```bash
curl -X GET https://api.kloud.cloud/v1/resources \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Getting an API Key

1. Login to Kloud Dashboard
2. Navigate to Settings → API Keys
3. Click "Generate New Key"
4. Store the key securely (it's only shown once)

---

## Endpoints

### 🧠 Curiosity Ocean AI

#### Chat Completion
```http
POST /ocean/v2/chat
```

**Request:**
```json
{
  "message": "What is machine learning?",
  "session_id": "optional-session-id",
  "options": {
    "temperature": 0.7,
    "max_tokens": 1024
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Machine learning is a subset of artificial intelligence...",
    "session_id": "abc123",
    "tokens_used": 256,
    "model": "llama3.1:8b"
  },
  "meta": {
    "latency_ms": 450,
    "timestamp": "2026-02-03T12:00:00Z"
  }
}
```

#### Streaming Response
```http
POST /ocean/v2/stream
```

Returns Server-Sent Events (SSE) for real-time streaming.

---

### 📊 Analytics

#### Get Analytics Summary
```http
GET /analytics/summary
```

**Query Parameters:**
- `from` (required): Start date (ISO 8601)
- `to` (required): End date (ISO 8601)
- `granularity`: `hour` | `day` | `week` | `month` (default: `day`)

**Response:**
```json
{
  "success": true,
  "data": {
    "total_requests": 15420,
    "unique_users": 342,
    "avg_latency_ms": 180,
    "success_rate": 99.8,
    "timeline": [
      { "date": "2026-02-01", "requests": 5120 },
      { "date": "2026-02-02", "requests": 5230 },
      { "date": "2026-02-03", "requests": 5070 }
    ]
  }
}
```

---

### 🔐 Authentication

#### Login
```http
POST /auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 86400,
    "user": {
      "id": "user123",
      "email": "user@example.com",
      "role": "admin"
    }
  }
}
```

#### Refresh Token
```http
POST /auth/refresh
```

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### 📁 Projects

#### List Projects
```http
GET /projects
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field (default: `created_at`)
- `order`: `asc` | `desc` (default: `desc`)

#### Create Project
```http
POST /projects
```

**Request:**
```json
{
  "name": "My Project",
  "description": "Project description",
  "settings": {
    "model": "llama3.1:8b",
    "temperature": 0.7
  }
}
```

#### Get Project
```http
GET /projects/:id
```

#### Update Project
```http
PUT /projects/:id
```

#### Delete Project
```http
DELETE /projects/:id
```

---

### 👤 Users

#### Get Current User
```http
GET /users/me
```

#### Update Profile
```http
PATCH /users/me
```

**Request:**
```json
{
  "name": "New Name",
  "avatar_url": "https://..."
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing API key |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limits

| Plan | Requests/Minute | Requests/Day |
|------|-----------------|--------------|
| Free | 10 | 100 |
| Pro | 100 | 10,000 |
| Enterprise | 1,000 | Unlimited |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## SDKs

### Python
```python
from kloud import KloudClient

client = KloudClient(api_key="your-api-key")
response = client.ocean.chat("What is AI?")
print(response.text)
```

### TypeScript
```typescript
import { KloudClient } from '@kloud/sdk';

const client = new KloudClient({ apiKey: 'your-api-key' });
const response = await client.ocean.chat('What is AI?');
console.log(response.text);
```

---

## Webhooks

Configure webhooks to receive real-time notifications:

```json
{
  "event": "project.created",
  "timestamp": "2026-02-03T12:00:00Z",
  "data": {
    "project_id": "proj123",
    "name": "My Project"
  }
}
```

### Available Events
- `project.created`
- `project.updated`
- `project.deleted`
- `user.created`
- `user.updated`
- `quota.exceeded`

---

*API Version: 1.0.0 | Last Updated: February 2026*

