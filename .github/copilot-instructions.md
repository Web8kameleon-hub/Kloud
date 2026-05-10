# 🧠 Kloud Cloud — Copilot Instructions

## Big Picture Architecture

- **Multi-service industrial backend**: FastAPI microservices for EEG, audio, ML, payment, and monitoring. Major engines: ALBI, ALBA, JONA, Ocean, ASI, Curiosity Ocean.
- **Service boundaries**: Each engine/service has its own Dockerfile, requirements, and API entrypoint. See `docker-compose.yml` for all service definitions and ports.
- **Data flows**: Real-time data (EEG, audio, metrics) flows between services via REST APIs, Redis, and internal HTTP calls. Payment events handled via webhooks.
- **Why**: Isolation for reliability, security, and scaling. ML/Excel dependencies are strictly separated (see `requirements/README.md`).

## Developer Workflows

- **Build & Run**: Use `docker-compose up --build` for full stack. For individual services, use their Dockerfile and requirements file.
- **Testing**: No global test runner; each service may have its own test scripts. For SDKs, see `sdk/python/README.md` and `sdk/typescript/README.md` for usage and examples.
- **Debugging**: Health endpoints (`/health`, `/status`) on every service. Use `docker ps` and `curl` for live status. Payment/webhook debugging via logs and webhook endpoints.
- **Frontend**: Next.js app in `apps/web` (see its README for dev commands).

## Project-Specific Conventions

- **Dependency isolation**: Never mix ML and Excel dependencies. Use separate requirements files and containers.
- **Secrets**: All credentials (SEPA, PayPal, Stripe) are injected via environment variables or GitHub secrets. Never hardcode.
- **API patterns**: All APIs expose `/health` and `/status`. Payment APIs use webhooks for activation.
- **Naming**: Service containers use `kloud-<service>` naming. Ports are unique per service (see `docker-compose.yml`).

## Integration Points & External Dependencies

- **Payments**: Stripe, SEPA, PayPal integrated via webhooks and API endpoints. See payment logic in backend and webhook handlers.
- **LLM/AI**: CLX / CLX.I inference, vLLM (GPU), HuggingFace, PyTorch, Transformers. Ocean/Curiosity engines use internal/external models.
- **Monitoring**: Metrics via psutil, health scoring, and Grafana dashboards (`docs/observability`).
- **SDKs**: Official Python and TypeScript SDKs in `sdk/python` and `sdk/typescript`.

## Key Files & Directories

- `docker-compose.yml`: Service definitions, ports, environment variables.
- `requirements/README.md`: Dependency isolation rules.
- `README.md`: High-level architecture and business context.
- `apps/web/README.md`: Frontend dev workflow.
- `sdk/python/README.md`, `sdk/typescript/README.md`: SDK usage and patterns.
- `docs/observability/README.md`: Monitoring and metrics.

---

> For new agents: Always check service boundaries, dependency rules, and health endpoints before making changes. Use the provided SDKs and follow isolation patterns for reliability.
