# Kloud Cloud — Copilot Tool Sets

## Tool Set: Deployment & DevOps

- deploy-ssh.yml (GitHub Actions)
- deploy-aviation-weather.sh (Aviation microservice)
- docker-compose.yml (multi-service orchestration)
- Health endpoints: /health, /status (all services)

## Tool Set: Backend Microservices

- FastAPI entrypoints for each engine (ALBI, ALBA, JONA, Ocean, ASI, Curiosity Ocean)
- Dockerfile per shërbim
- requirements/README.md (dependency isolation)
- API patterns: /health, /status, webhooks

## Tool Set: Frontend & SDKs

- Next.js app (apps/web)
- SDKs: sdk/python, sdk/typescript
- Official API key management
- Demo API key for testing

## Tool Set: Monitoring & Observability

- Grafana dashboards (docs/observability)
- Metrics via psutil
- Service health scoring

## Tool Set: Payments & Security

- Stripe, SEPA, PayPal webhook handlers
- Environment variable secrets
- Never hardcode credentials

---

> Për çdo agjent Copilot: Kontrollo kufijtë e shërbimeve, rregullat e varësive, dhe endpoint-et e shëndetit para çdo ndryshimi. Përdor SDK-të zyrtare dhe izolo varësitë sipas rregullave të projektit.
