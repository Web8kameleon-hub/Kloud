# Clisonix AI Global 9999

CPU-first multilingual orchestration gateway for Clisonix.

## What it does

- Runs on port `9999`
- Supports global multilingual prompts
- Enforces anti-discrimination response policy
- Exposes service array health checks
- Provides automation planning endpoint for staged full-system integration

## Endpoints

- `GET /health`
- `GET /api/v1/tools/status`
- `POST /api/v1/chat`
- `POST /api/v1/automation/plan`

## Local run

```powershell
Set-Location services/ai-global-9999
pip install -r requirements.txt
python app.py
```

## Docker run

```powershell
docker compose up -d --build ai-global-9999
```

## Example chat

```powershell
$body = @{ message = 'Hola, responde en español y resume en inglés.'; language_hint = 'Spanish' } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:9999/api/v1/chat" -Method Post -ContentType "application/json" -Body $body
```
