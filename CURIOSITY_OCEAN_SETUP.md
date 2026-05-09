# 🌊 Curiosity Ocean - Groq + Hybrid Biometric Integration

## Overview

**Curiosity Ocean** is a conversational AI system that combines:
- **Groq LLM** - Fast, intelligent responses for natural conversations
- **Hybrid Biometric API** - Real-time phone sensors + clinic device data
- **Session Management** - Persistent conversation history with health context

Perfect for:
- Health-aware conversations
- Biometric data analysis with AI insights
- Real-time patient monitoring with chat
- Personalized medical recommendations

---

## Architecture

```
User Question
    ↓
[Curiosity Ocean Router]
    ├─→ Fetch Biometric Data (Hybrid API)
    │   ├─ Phone sensors (heart rate, temp, etc.)
    │   └─ Clinic devices (EEG, ECG, SpO2, etc.)
    │
    ├─→ Add Context to Prompt
    │   └─ "Heart Rate: 78 bpm, Temperature: 36.8°C"
    │
    ├─→ Call Groq LLM
    │   └─ Fast inference with biometric awareness
    │
    └─→ Return Response
        └─ Store in session history
```

---

## Quick Start

### 1. Configuration

Copy `.env.ocean` to `.env`:

```bash
cp .env.ocean .env
```

Set your Groq API key:

```bash
export GROQ_API_KEY="gsk_YOUR_KEY_HERE"
export HYBRID_BIOMETRIC_API="http://127.0.0.1:8000"
```

### 2. Start Services

**Terminal 1 - Hybrid Biometric API:**
```bash
python apps/api/hybrid_biometric_api.py
# Runs on http://localhost:8000
```

**Terminal 2 - Main API with Ocean:**
```bash
cd apps/api
python -m uvicorn main:app --host 0.0.0.0 --port 8010
# Ocean endpoints available at http://localhost:8010/api/ocean
```

### 3. Test Integration

```bash
curl -X POST "http://localhost:8010/api/ocean/test-integration"
```

Expected response:
```json
{
  "timestamp": "2025-01-10T...",
  "integration_test": {
    "groq": {
      "configured": true,
      "model": "mixtral-8x7b-32768",
      "status": "ready",
      "test": "success"
    },
    "hybrid_biometric": {
      "status": "connected",
      "endpoint": "http://127.0.0.1:8000",
      "response_time_ms": 45.2
    }
  }
}
```

---

## API Endpoints

### Chat with Ocean

**Request:**
```bash
curl -X POST "http://localhost:8010/api/ocean/chat?question=What%20is%20my%20heart%20rate?" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "question": "What is my heart rate?",
  "answer": "Your current heart rate is 78 bpm, which is in the healthy range for resting heart rate...",
  "biometric_context": {
    "heartRate": {
      "value": 78,
      "unit": "bpm",
      "timestamp": "2025-01-10T..."
    },
    "temperature": {
      "value": 36.8,
      "unit": "°C"
    }
  },
  "conversation_length": 1,
  "timestamp": "2025-01-10T..."
}
```

### Stream Chat (Real-time Response)

```bash
curl -X GET "http://localhost:8010/api/ocean/chat/stream?question=Tell%20me%20about%20my%20health" \
  --streaming
```

### Get Biometric Insights

```bash
curl -X GET "http://localhost:8010/api/ocean/biometric-insights"
```

Response:
```json
{
  "success": true,
  "phone_sensors": {
    "heartRate": { "value": 78, "unit": "bpm" },
    "temperature": { "value": 36.8, "unit": "°C" },
    "acceleration": { "x": 0.1, "y": 0.2, "z": 9.8 }
  },
  "clinic_devices": {
    "eeg": { "channels": 14, "sampling_rate": 256 },
    "ecg": { "channels": 1, "sampling_rate": 130 },
    "spo2": { "value": 98, "unit": "%" }
  },
  "timestamp": "2025-01-10T..."
}
```

### Get Session Info

```bash
curl -X GET "http://localhost:8010/api/ocean/session/SESSION_ID"
```

### Delete Session

```bash
curl -X DELETE "http://localhost:8010/api/ocean/session/SESSION_ID"
```

### Status Check

```bash
curl -X GET "http://localhost:8010/api/ocean/status"
```

---

## Session Management

Sessions persist conversation history and biometric context:

```python
# Same session continues conversation
response1 = await ocean_chat("What is my heart rate?", session_id="user-123")
response2 = await ocean_chat("How does it compare to yesterday?", session_id="user-123")
# Groq remembers context from response1
```

---

## Advanced Features

### 1. Analyze with Biometric Context

```bash
curl -X POST "http://localhost:8010/api/ocean/analyze-with-context" \
  -H "Content-Type: application/json" \
  -d '{"question": "Am I healthy today?"}'
```

Automatically includes:
- Real-time phone sensor data
- Clinical device readings
- Health insights from Groq

### 2. Custom Temperature (Creativity)

```bash
# More creative responses
POST /api/ocean/chat?question=...&temperature=1.5

# More factual responses
POST /api/ocean/chat?question=...&temperature=0.3
```

### 3. Conversation History Context

Automatically maintained per session. Groq uses previous messages for context.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | **Required** - Your Groq API key from console.groq.com |
| `GROQ_BASE_URL` | https://api.groq.com/openai/v1 | Groq API endpoint |
| `GROQ_MODEL` | mixtral-8x7b-32768 | LLM model to use |
| `GROQ_TIMEOUT` | 30 | API timeout in seconds |
| `GROQ_MAX_TOKENS` | 2000 | Max response length |
| `HYBRID_BIOMETRIC_API` | http://127.0.0.1:8000 | Hybrid Biometric API endpoint |
| `ENVIRONMENT` | development | deployment environment |
| `DEBUG` | true | Debug logging |

---

## Docker Deployment

### docker-compose.yml Addition

```yaml
services:
  # Hybrid Biometric API
  hybrid-biometric:
    build:
      context: .
      dockerfile: Dockerfile.hybrid-biometric
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    networks:
      - kloud-network

  # Main API with Ocean
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8010:8010"
    depends_on:
      - hybrid-biometric
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - HYBRID_BIOMETRIC_API=http://hybrid-biometric:8000
      - ENVIRONMENT=production
    networks:
      - kloud-network

networks:
  kloud-network:
    driver: bridge
```

Deploy:
```bash
docker-compose up -d
```

---

## Hetzner Server Setup

For Hetzner server deployment:

```bash
# 1. SSH into Hetzner server
ssh root@YOUR_SERVER_IP

# 2. Clone repository
git clone https://github.com/Kameleonlife/Kloud-cloud.git
cd Kloud-cloud

# 3. Set environment
export GROQ_API_KEY="gsk_YOUR_KEY"
export HYBRID_BIOMETRIC_API="http://internal-api:8000"
export ENVIRONMENT="production"

# 4. Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl http://localhost:8010/api/ocean/status
```

---

## Integration with Frontend

### React Example

```typescript
import { useState } from 'react';

export function OceanChat() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [sessionId, setSessionId] = useState('');

  const handleChat = async () => {
    const res = await fetch('/api/ocean/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        session_id: sessionId,
        use_biometric_context: true
      })
    });

    const data = await res.json();
    setResponse(data.answer);
    setSessionId(data.session_id);
  };

  return (
    <div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask Ocean..."
      />
      <button onClick={handleChat}>Ask</button>
      <p>{response}</p>
      {data.biometric_context && (
        <p>Heart Rate: {data.biometric_context.heartRate.value} bpm</p>
      )}
    </div>
  );
}
```

---

## Troubleshooting

### "Groq not configured"
```
Solution: Set GROQ_API_KEY environment variable
export GROQ_API_KEY="gsk_xxxxx"
```

### "Hybrid Biometric API unavailable"
```
Solution: Ensure Hybrid API is running on the configured endpoint
python apps/api/hybrid_biometric_api.py
```

### "Timeout calling Groq"
```
Solution: Increase timeout and check internet connection
export GROQ_TIMEOUT=60
```

### "Model not found"
```
Solution: Check available models at https://console.groq.com/docs/models
Common models:
- mixtral-8x7b-32768 (default, fast)
- llama-2-70b-chat (powerful)
- neural-chat-7b (lightweight)
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Groq Response Time | 50-200ms |
| Biometric Fetch | 30-100ms |
| Total Latency | 100-300ms |
| Max Concurrent Sessions | 1000+ |
| Session Memory | ~10KB per session |

---

## Future Enhancements

- [ ] Add voice input/output (Groq + TTS)
- [ ] Multi-modal analysis (images + biometrics)
- [ ] Advanced session persistence (Redis)
- [ ] Real-time streaming analysis
- [ ] Integration with Hetzner monitoring
- [ ] AI-powered health predictions
- [ ] Automated alerts based on patterns

---

## Support

For issues or questions:
1. Check `.env.ocean` configuration
2. Verify both services running: `/api/ocean/status`
3. Review logs in deployment directory
4. Check Groq status: https://status.groq.com

---

**Author:** Ledjan Ahmati  
**License:** Closed Source  
**Version:** 1.0.0  
**Last Updated:** January 10, 2025

