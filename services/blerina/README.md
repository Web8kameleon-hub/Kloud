# BLERINA Pillar Content Engine v2.0

High-quality pillar article generation with quality gate.

## Features

- **Pillar Articles**: 3000-5000 word deep-dive articles
- **Quality Gate**: Validates content against quality standards
- **LLM Integration**: Uses CLX for content generation
- **Video Integration**: Triggers video generator for supporting content
- **YouTube Ready**: Configured for Kloud YouTube channel

## API Endpoints

| Endpoint | Method | Description |
<<<<<<< HEAD
| ---------- | -------- | ------------- |
=======
|----------|--------|-------------|
>>>>>>> fc9063a0 (feat: BLERINA Pillar Engine v2.0 - 3000-5000 word articles with quality gate)
| `/health` | GET | Health check |
| `/status` | GET | Detailed status |
| `/api/v1/topics` | GET | List available topics |
| `/api/v1/pillars/generate` | POST | Generate pillar article |
| `/api/v1/pillars` | GET | List generated pillars |
| `/api/v1/pillars/{id}` | GET | Get specific pillar |
| `/api/v1/quality/check` | POST | Check content quality |

## Generate a Pillar

```bash
curl -X POST http://localhost:8035/api/v1/pillars/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "bci_fundamentals", "target_words": 4000}'
```

## Quality Standards

- Minimum 3000 words for pillar articles
- Quality score >= 0.85
- No fake imports (validated)
- No placeholder data
- Real code examples required

## Environment Variables

| Variable | Default | Description |
<<<<<<< HEAD
| ---------- | --------- | ------------- |
| `PORT` | 8035 | Service port |
| `CLX_HOST` | <http://localhost:11434> | CLX URL |
| `MODEL` | llama3.1:8b | LLM model |
| `YOUTUBE_API_KEY` | - | YouTube Data API key |
| `YOUTUBE_CHANNEL_ID` | UCuCd7kgikh6CM2hAh5eAIMA | Channel ID |
| `VIDEO_GENERATOR_URL` | <http://localhost:8029> | Video generator |
=======
|----------|---------|-------------|
| `PORT` | 8035 | Service port |
| `CLX_HOST` | http://localhost:11434 | CLX URL |
| `MODEL` | llama3.1:8b | LLM model |
| `YOUTUBE_API_KEY` | - | YouTube Data API key |
| `YOUTUBE_CHANNEL_ID` | UCuCd7kgikh6CM2hAh5eAIMA | Channel ID |
| `VIDEO_GENERATOR_URL` | http://localhost:8029 | Video generator |
>>>>>>> fc9063a0 (feat: BLERINA Pillar Engine v2.0 - 3000-5000 word articles with quality gate)

## Pillar Topics

1. **EEG Clinical Validation** - FDA, MDR, ISO 62304
2. **ALDA Architecture** - Deep technical dive
3. **BCI Fundamentals** - Complete guide
4. **Neural Signal Processing** - Real-time implementation
5. **EU AI Act Compliance** - Regulatory guide
6. **Edge AI Medical** - Medical device AI

