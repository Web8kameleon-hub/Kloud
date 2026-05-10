# 🌊 Ocean Multimodal Deployment Guide

## Quick Start

### 1. Add to docker-compose.yml

Add the ocean-multimodal service to your main `docker-compose.yml`:

```yaml
ocean-multimodal:

  build:
    context: ./ocean-core
    dockerfile: Dockerfile.multimodal
  container_name: kloud-ocean-multimodal
  ports:
    - "8031:8031"
  environment:
    PORT: 8031
    CLX_HOST: http://kloud-06-clx:11434
    VISION_MODEL: clx.i:latest
    AUDIO_MODEL: whisper:latest
    REASONING_MODEL: llama3.1:8b
    PYTHONUNBUFFERED: 1
  depends_on:
    - clx
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8031/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  restart: always

```

### 2. Pull Required Models

```bash
# On the server with CLX running

docker exec kloud-06-clx clx pull clx.i:latest
docker exec kloud-06-clx clx pull whisper:latest
docker exec kloud-06-clx clx pull llama3.1:8b

```

### 3. Deploy Services

```bash
# Rebuild all services

docker compose build --no-cache

# Start only Ocean Multimodal
docker compose up -d ocean-multimodal

# Or start all services
docker compose up -d

# Check status
docker compose ps | grep ocean

```

### 4. Verify Health

```bash
# Check health endpoint

curl http://localhost:8031/health

# Expected response
{
  "status": "healthy",
  "pipelines": {
    "vision": "online",
    "audio": "online",
    "document": "online",
    "reasoning": "online"
  }
}

```

---

## Testing Pipelines

### Run Test Suite

```bash
# Install test dependencies

pip install pytest pytest-asyncio httpx

# Run tests
python ocean-core/test_multimodal.py

```

### Manual Testing

#### Vision Pipeline

```bash
curl -X POST http://localhost:8031/api/v1/vision \

  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANS...",
    "prompt": "What is in this image?",
    "analyze_objects": true,
    "extract_text": true
  }'

```

#### Audio Pipeline

```bash
curl -X POST http://localhost:8031/api/v1/audio \

  -H "Content-Type: application/json" \
  -d '{
    "audio_base64": "SUQzBAAAAAAAI1...",
    "language": "en",
    "include_timestamps": true
  }'

```

#### Document Pipeline

```bash
curl -X POST http://localhost:8031/api/v1/document \

  -H "Content-Type: application/json" \
  -d '{
    "content": "Your document text here...",
    "doc_type": "text",
    "analyze_entities": true,
    "extract_summary": true
  }'

```

#### Reasoning Pipeline

```bash
curl -X POST http://localhost:8031/api/v1/reason \

  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the meaning of life?",
    "context": {
      "domain": "philosophy"
    }
  }'

```

#### Multimodal Fusion

```bash
curl -X POST http://localhost:8031/api/v1/analyze \

  -H "Content-Type: application/json" \
  -d '{
    "mode": "multimodal",
    "vision_input": {...},
    "audio_input": {...},
    "document_input": {...}
  }'

```

---

## File Structure

```text
ocean-core/

├── ocean_nanogrid.py           # Core Ocean service (existing)
├── ocean_multimodal.py         # NEW: Multimodal engine
├── Dockerfile                  # Original Ocean Dockerfile
├── Dockerfile.multimodal       # NEW: Multimodal Dockerfile
├── requirements.txt            # Dependencies
└── test_multimodal.py          # NEW: Test suite

Root directory:
├── ocean-multimodal.compose.yml # NEW: Service config snippet
├── OCEAN_MULTIMODAL_API.md      # NEW: Complete API documentation
├── OCEAN_MULTIMODAL_DEPLOYMENT.md # This file

```

---

## Architecture

### Service Dependencies

```text
ocean-multimodal (port 8031)

    ↓
kloud-06-clx (port 11434)
    ├── clx.i:latest          (Vision)
    ├── whisper:latest        (Audio)
    └── llama3.1:8b           (Reasoning)

```

### Processing Pipeline

```text
Request → Router (SensorMode)

    ├→ VISION     → VisionPipeline   → clx.i model
    ├→ AUDIO      → AudioPipeline    → whisper model
    ├→ DOCUMENT   → DocumentPipeline → llama model
    ├→ REASON     → ReasoningEngine  → llama model
    └→ MULTIMODAL → Fusion Engine    → All models
        ↓
Response (AnalysisResult)

```

---

## Environment Variables

```bash
# Service Configuration

PORT=8031                           # Service port
CLX_HOST=http://localhost:11434  # CLX endpoint

# Model Selection
VISION_MODEL=clx.i:latest           # Image analysis
AUDIO_MODEL=whisper:latest          # Speech-to-text
REASONING_MODEL=llama3.1:8b         # LLM inference

# Runtime
PYTHONUNBUFFERED=1                  # No buffering

```

---

## Performance Tuning

### For High Throughput

```yaml
ocean-multimodal:

  # ...
  environment:
    # Increase CLX parallelism
    CLX_NUM_PARALLEL: 4
    # Increase CLX context size
    CLX_NUM_PREDICT: 1024
  # Increase container resources
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G

```

### For Low Latency

- Use smaller models (e.g., `clx.i-7b` instead of `clx.i-13b`)
- Enable GPU acceleration if available
- Use caching layers for repeated queries
- Set `CLX_NUM_PARALLEL: 1` for consistency

---

## Monitoring & Logs

### Container Logs

```bash
# Real-time logs

docker compose logs -f ocean-multimodal

# Last 50 lines
docker compose logs --tail=50 ocean-multimodal

# Specific time range
docker compose logs --since 2026-02-04 ocean-multimodal

```

### Health Metrics

```bash
# Monitor health endpoint continuously

watch -n 5 'curl -s http://localhost:8031/health | jq'

# Check request count growth
curl http://localhost:8031/health | jq '.requests_processed'

```

### Container Stats

```bash
# Memory and CPU usage

docker stats kloud-ocean-multimodal

# Detailed inspection
docker inspect kloud-ocean-multimodal

```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs

docker compose logs ocean-multimodal

# Verify CLX is running
docker ps | grep clx

# Test CLX connectivity
curl http://localhost:11434/api/tags

```

### Out of Memory

```bash
# Increase container memory

docker compose up -d --no-recreate ocean-multimodal
docker update --memory 8g kloud-ocean-multimodal

# Restart container
docker restart kloud-ocean-multimodal

```

### Model Not Found

```bash
# List available models

docker exec kloud-06-clx clx list

# Pull missing model
docker exec kloud-06-clx clx pull clx.i:latest

```

### Slow Responses

```bash
# Check CLX load

curl http://localhost:11434/api/ps

# Monitor system resources
docker stats kloud-ocean-multimodal
docker stats kloud-06-clx

# Increase parallelism if needed

```

---

## Integration Examples

### FastAPI Integration

```python
import httpx

from fastapi import APIRouter

router = APIRouter(prefix="/ocean")

async def call_ocean(mode: str, data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://kloud-ocean-multimodal:8031/api/v1/analyze",
            json={"mode": mode, **data}
        )
        return response.json()

@router.post("/vision")
async def analyze_image(image_b64: str, prompt: str):
    return await call_ocean("vision", {
        "vision_input": {
            "image_base64": image_b64,
            "prompt": prompt
        }
    })

```

### Service Mesh (Istio)

```yaml
apiVersion: networking.istio.io/v1beta1

kind: VirtualService
metadata:
  name: ocean-multimodal
spec:
  hosts:
  - kloud-ocean-multimodal
  http:
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: kloud-ocean-multimodal
        port:
          number: 8031
    timeout: 60s
    retries:
      attempts: 3
      perTryTimeout: 20s

```

---

## Security Considerations

### Rate Limiting

- Default: 1000 requests/hour per user
- Admin bypass: `X-Admin: true` header
- Admin user IDs: "adm" or "admin"

### Input Validation

- Base64 images/audio are validated
- Document content is sanitized
- Prompts are limited to 10KB

### HTTPS/TLS

```yaml
ocean-multimodal:

  # Enable reverse proxy with HTTPS
  labels:
    - "traefik.http.routers.ocean.rule=Host(`ocean.kloud.com`)"
    - "traefik.http.routers.ocean.entrypoints=websecure"
    - "traefik.http.routers.ocean.tls=true"

```

---

## Scaling Considerations

### Horizontal Scaling

For multiple instances:

```yaml
ocean-multimodal-1:

  # ... same config
  container_name: kloud-ocean-multimodal-1
  ports:
    - "8031:8031"

ocean-multimodal-2:
  # ... same config
  container_name: kloud-ocean-multimodal-2
  ports:
    - "8032:8031"

# Load balancer (Nginx/HAProxy)
# Routes to both instances

```

### Vertical Scaling

Increase resources for single instance:

```yaml
ocean-multimodal:

  deploy:
    resources:
      limits:
        cpus: '8'
        memory: 16G

```

---

## Version History

- **v1.0.0** (Feb 4, 2026): Initial multimodal release
  - Vision pipeline with clx.i
  - Audio transcription with whisper
  - Document reasoning with llama3.1
  - Multimodal fusion capability
  - Rate limiting and admin bypass

---

## Support & Documentation

- 📖 **API Docs**: See `OCEAN_MULTIMODAL_API.md`
- 🧪 **Tests**: Run `python ocean-core/test_multimodal.py`
- 📊 **Monitoring**: Check `/health` endpoint
- 💬 **Support**: Contact the Kloud development team

---

**Deployment Status**: ✅ Ready for production

Last Updated: Feb 4, 2026

