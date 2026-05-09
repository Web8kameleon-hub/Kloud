# 🌊 Ocean Multimodal API Guide

## Overview

Ocean Multimodal is a unified interface for AI perception and reasoning with four sensory modes:

- **👁️ Vision**: Image analysis, object detection, OCR, scene understanding
- **🎙️ Audio**: Speech-to-text, transcription, audio analysis  
- **📄 Document**: Text extraction, document reasoning, entity recognition
- **🧠 Reasoning**: Direct LLM inference over any input

---

## API Endpoints

### Health Check

```bash
GET /health

```

**Response:**

```json
{
  "status": "healthy",
  "pipelines": {
    "vision": "online",
    "audio": "online",
    "document": "online",
    "reasoning": "online"
  },
  "requests_processed": 42,
  "uptime_seconds": 3600.5,
  "timestamp": "2026-02-04T10:30:00Z"
}

```

---

## 👁️ Vision Pipeline

### Image Analysis

```bash
POST /api/v1/vision
Content-Type: application/json

{
  "image_base64": "iVBORw0KGgoAAAANS...",
  "prompt": "What objects are in this image?",
  "analyze_objects": true,
  "extract_text": true
}

```

**Response:**

```json
{
  "status": "success",
  "objects_detected": [
    {"name": "person", "confidence": 0.95},
    {"name": "car", "confidence": 0.87}
  ],
  "text_extracted": "License plate: ABC123",
  "confidence": "high",
  "processing_time_ms": 1234.5
}

```

### Audio via Multimodal

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "mode": "vision",
  "vision_input": {
    "image_base64": "iVBORw0KGgoAAAANS...",
    "prompt": "Describe this image in detail",
    "analyze_objects": true,
    "extract_text": true
  }
}

```

**Response:**

```json
{
  "mode": "vision",
  "confidence": "high",
  "timestamp": "2026-02-04T10:30:45Z",
  "processing_time_ms": 2150.3,
  "output": {
    "status": "success",
    "objects_detected": [...],
    "text_extracted": "...",
    "confidence": "high"
  }
}

```

---

## 🎙️ Audio Pipeline

### Speech-to-Text Transcription

```bash
POST /api/v1/audio
Content-Type: application/json

{
  "audio_base64": "SUQzBAAAAAAAI1...",
  "language": "en",
  "include_timestamps": true
}

```

**Response:**

```json
{
  "status": "success",
  "transcript": "Hello, this is a test message for the audio pipeline",
  "language": "en",
  "confidence": "high",
  "duration_seconds": 5.2,
  "processing_time_ms": 3450.0,
  "words": ["Hello", "this", "is", "a", "test", "message", "..."],
  "timestamps": [
    {"word": "Hello", "start": 0.0, "end": 0.1},
    {"word": "this", "start": 0.1, "end": 0.2}
  ]
}

```

### Using Multimodal Endpoint

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "mode": "audio",
  "audio_input": {
    "audio_base64": "SUQzBAAAAAAAI1...",
    "language": "en",
    "include_timestamps": true
  }
}

```

---

## 📄 Document Pipeline

### Document Analysis & Reasoning

```bash
POST /api/v1/document
Content-Type: application/json

{
  "content": "The quick brown fox jumps over the lazy dog...",
  "doc_type": "text",
  "analyze_entities": true,
  "extract_summary": true
}

```

**Response:**

```json
{
  "status": "success",
  "analysis": "This text appears to be about animal behavior...",
  "entities": {
    "people": ["Fox", "Dog"],
    "organizations": [],
    "dates": []
  },
  "summary": "A narrative describing animal interactions...",
  "confidence": "medium",
  "processing_time_ms": 4120.5
}

```

### Supported Document Types

- `text`: Plain text files
- `markdown`: Markdown formatted text
- `pdf`: PDF files (requires text extraction)
- `docx`: Microsoft Word documents (requires extraction)

### Document via Multimodal

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "mode": "document",
  "document_input": {
    "content": "Extracted PDF or DOCX content here...",
    "doc_type": "pdf",
    "analyze_entities": true,
    "extract_summary": true
  }
}

```

---

## 🧠 Reasoning Pipeline

### Direct LLM Inference

```bash
POST /api/v1/reason
Content-Type: application/json

{
  "prompt": "What are the implications of quantum computing for cryptography?",
  "context": {
    "domain": "technology",
    "expertise_level": "advanced",
    "previous_queries": [...]
  }
}

```

**Response:**

```json
{
  "status": "success",
  "reasoning": "Quantum computers could break current encryption...",
  "processing_time_ms": 5600.0
}

```

### Reasoning via Multimodal

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "mode": "reason",
  "reasoning_prompt": "Explain the significance of this discovery",
  "context": {
    "domain": "science",
    "field": "biology"
  }
}

```

---

## 🔄 Multimodal Fusion

### Combine Multiple Inputs

```bash
POST /api/v1/analyze
Content-Type: application/json

{
  "mode": "multimodal",
  "vision_input": {
    "image_base64": "iVBORw0KGgoAAAANS...",
    "prompt": "What's happening?"
  },
  "audio_input": {
    "audio_base64": "SUQzBAAAAAAAI1...",
    "language": "en"
  },
  "document_input": {
    "content": "Additional context document...",
    "doc_type": "text"
  },
  "reasoning_prompt": "Synthesize all inputs into coherent understanding"
}

```

**Response:**

```json
{
  "mode": "multimodal",
  "confidence": "high",
  "timestamp": "2026-02-04T10:31:00Z",
  "processing_time_ms": 8450.0,
  "output": {
    "status": "success",
    "fused_analysis": {
      "vision": {...},
      "audio": {...},
      "document": {...}
    },
    "integrated_understanding": "Combined analysis across all sensory inputs"
  }
}

```

---

## Integration Examples

### Python Example

```python
import requests
import base64

# Vision Analysis
def analyze_image(image_path):
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    response = requests.post(
        "http://localhost:8031/api/v1/analyze",
        json={
            "mode": "vision",
            "vision_input": {
                "image_base64": image_b64,
                "prompt": "What's in this image?",
                "analyze_objects": True
            }
        }
    )
    return response.json()

# Audio Transcription
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    response = requests.post(
        "http://localhost:8031/api/v1/audio",
        json={
            "audio_base64": audio_b64,
            "language": "en"
        }
    )
    return response.json()

# Direct Reasoning
def reason(prompt, context=None):
    response = requests.post(
        "http://localhost:8031/api/v1/reason",
        json={"prompt": prompt, "context": context}
    )
    return response.json()

```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');
const fs = require('fs');

// Vision analysis
async function analyzeImage(imagePath) {
  const imageBuffer = fs.readFileSync(imagePath);
  const imageB64 = imageBuffer.toString('base64');
  
  const response = await axios.post(
    'http://localhost:8031/api/v1/analyze',
    {
      mode: 'vision',
      vision_input: {
        image_base64: imageB64,
        prompt: "What's in this image?",
        analyze_objects: true
      }
    }
  );
  return response.data;
}

// Audio transcription
async function transcribeAudio(audioPath) {
  const audioBuffer = fs.readFileSync(audioPath);
  const audioB64 = audioBuffer.toString('base64');
  
  const response = await axios.post(
    'http://localhost:8031/api/v1/audio',
    {
      audio_base64: audioB64,
      language: 'en'
    }
  );
  return response.data;
}

```

---

## Error Handling

### Error Responses

```json
{
  "detail": "Error processing request",
  "status_code": 500,
  "timestamp": "2026-02-04T10:30:45Z"
}

```

### Common Status Codes

- `200`: Success
- `400`: Invalid request format
- `422`: Validation error (missing required fields)
- `429`: Rate limit exceeded
- `500`: Internal processing error
- `503`: Service unavailable (Ollama offline)

---

## Rate Limiting

- **Regular users**: 1000 requests/hour
- **Admin users**: Unlimited (pass `X-Admin: true` header)
- **Admin ID**: "adm" or "admin" in `X-User-ID`

### Headers

```bash
curl -X POST http://localhost:8031/api/v1/analyze \
  -H "X-User-ID: user@example.com" \
  -H "X-Admin: true" \
  -H "Content-Type: application/json" \
  -d '{...}'

```

---

## Performance Benchmarks

| Pipeline | Typical Time | Notes |
|----------|--------------|---------|
| Vision | 1.5-2.5s | Depends on image size |
| Audio | 2.0-4.0s | Depends on audio length |
| Document | 1.0-3.0s | Depends on content length |
| Reasoning | 2.0-5.0s | Depends on prompt complexity |
| Multimodal | 6.0-12.0s | Combined processing |

---

## Deployment

### Docker Compose

```yaml
ocean-multimodal:
  build:
    context: ./ocean-core
    dockerfile: Dockerfile.multimodal
  container_name: kloud-ocean-multimodal
  ports:
    - "8031:8031"
  environment:
    OLLAMA_HOST: http://kloud-06-ollama:11434
    VISION_MODEL: llava:latest
    AUDIO_MODEL: whisper:latest
    REASONING_MODEL: llama3.1:8b
  depends_on:
    - ollama
  restart: always

```

### Manual Start

```bash
# Install dependencies
pip install -r ocean-core/requirements.txt

# Run service
python ocean-core/ocean_multimodal.py

# Test health
curl http://localhost:8031/health

```

---

## Troubleshooting

### Ollama Connection Error

```

Error: Connection refused (Ollama offline)

```

**Solution**: Ensure Ollama is running on the configured host

```bash
docker ps | grep ollama

```

### Model Not Found

```

Error: Model 'llava:latest' not found

```

**Solution**: Pull the model first

```bash
ollama pull llava
ollama pull whisper
ollama pull llama3.1:8b

```

### Memory Issues

```

Error: Out of memory

```

**Solution**: Use smaller models or increase container limits

```bash
docker update --memory 8g kloud-ocean-multimodal

```

---

## Future Enhancements

- [ ] Real-time streaming audio/video
- [ ] Advanced object tracking across frames
- [ ] Multi-language document analysis
- [ ] Vector-based semantic search
- [ ] Federated learning support
- [ ] GPU acceleration
- [ ] Custom model fine-tuning

---

**Last Updated**: Feb 4, 2026  
**Version**: 1.0.0  
**Status**: Stable

