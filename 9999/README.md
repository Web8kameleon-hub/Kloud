# Kloud 9999 Gateway

Dedicated `9999/app.py` service connected to core app functions.

## Capabilities

- Multilingual chat orchestration
- Discussion/debate proxy to ocean-core
- Vision analyze (CLX.I via CLX)
- Vision create (image generation file output)
- Document reader + summarizer
- Document writer
- Video create (MP4) and process (ffmpeg)
- Music create (WAV/MP3) with do/re/mi/fa/sol/la/si
- Binary algebra for solfege notes

## Run in Docker

```powershell
docker compose up -d --build ai-global-9999
```

## Health

```powershell
Invoke-WebRequest -Uri "http://localhost:9999/health" -UseBasicParsing
```

