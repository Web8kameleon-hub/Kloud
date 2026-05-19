# Kloud Hosting And Orchestration Baseline

## Index

1. Purpose
2. Snapshot Inventory
3. Service Classification
4. Orchestration Map (Who Calls Whom)
5. Routing And Rewrite Paths
6. Backend Internal Wiring
7. XLC Resonant Reading Wiring (MMM -> WWW)
8. Why Changes Did Not Reach Hosting
9. Mandatory Deployment Flow
10. Network Active Endpoints Playbook
11. Release Discipline
12. Minimum Functional Checks
13. Change Control And Stability Rules
14. Update Procedure For This Document

## Purpose

This document is the single source of truth for hosting, orchestration, and deployment execution in Kloud.

Goals:

- Keep production deployment deterministic.
- Keep architecture readable and auditable.
- Prevent "works local but not on server" drift.
- Preserve one stable reference that survives deploys and branch switches.

## Snapshot Inventory (measured on 2026-05-17)

- Docker Compose services in [docker-compose.yml](../docker-compose.yml): 89
- Infra services (classified): 12
- Backend/application services (classified): 77
- Top-level directories in repository: 85
- Total directories (recursive): 20971
- Python route handlers detected in backend scopes (apps, backend, ocean-core, services, routes, src): 887
- Module map bullets in [CLISONIX_MODULE_MAP.md](../CLISONIX_MODULE_MAP.md): 9
- Service registry reference in [ocean-core/service_registry.py](../ocean-core/service_registry.py): All 56+ Kloud Microservices

## Service Classification

### Infra services (12)

postgres, redis, neo4j, minio, victoriametrics, prometheus, grafana, loki, jaeger, tempo, traefik, web

### Backend/application services (77)

All remaining services in [docker-compose.yml](../docker-compose.yml) not listed as infra.

## Orchestration Map (Who Calls Whom)

This section defines runtime call chains. These are operational chains, not just code ownership.

### Chain A: Public HTTP To Frontend

1. Client request enters reverse proxy layer.
2. Reverse proxy forwards to frontend container.
3. Frontend may serve UI directly or rewrite to backend APIs.

Evidence:

- [nginx/default.conf](../nginx/default.conf) forwards root traffic to web:3000.
- [docker-compose.yml](../docker-compose.yml) exposes traefik on 80 and dashboard on 8088.

### Chain B: Frontend Rewrite To Main API

1. Browser hits Next.js route like /api/*.
2. Next.js rewrite sends traffic to API_INTERNAL_URL or kloud-api:8000.
3. FastAPI app resolves router and executes domain module.

Evidence:

- [apps/web/next.config.js](../apps/web/next.config.js) rewrites /api/* namespaces to API_BASE.
- [apps/api/main.py](../apps/api/main.py) includes routers via app.include_router(...).

### Chain C: Frontend Rewrite To Ocean-Core

1. Browser hits /api/zurich/*, /api/debate/*, or /api/ocean/*.
2. Next.js rewrite sends to OCEAN_BASE (kloud-ocean-core:8030 in production).
3. Ocean Core handles /api/v1/* endpoints and orchestrates internal engines.

Evidence:

- [apps/web/next.config.js](../apps/web/next.config.js) defines OCEAN_BASE and related rewrites.
- [docker-compose.yml](../docker-compose.yml) maps ocean-core at 8030.

### Chain D: Backend Service To Internal Module

1. Request reaches backend service process.
2. Service dispatches through router registration.
3. Router delegates to domain implementation modules.

Evidence:

- [apps/api/routers/__init__.py](../apps/api/routers/__init__.py) exports eeg_router, audio_router, brain_api_router.
- [apps/api/main.py](../apps/api/main.py) includes many routers (brain, eeg, audio, fabric, reporting, billing, jona, dns, and others).

## Routing And Rewrite Paths

### Reverse proxy layer

- Traefik service exists as gateway and load balancer in [docker-compose.yml](../docker-compose.yml).
- Nginx fallback/default proxy forwards root traffic to frontend in [nginx/default.conf](../nginx/default.conf).

### Rewrite layer (frontend)

In [apps/web/next.config.js](../apps/web/next.config.js), rewrites include:

- /api/crypto/* -> API_BASE
- /api/weather/* -> API_BASE
- /api/ai/* -> API_BASE
- /api/alba/*, /api/albi/*, /api/asi/*, /api/jona/* -> API_BASE
- /api/zurich/*, /api/debate/*, /api/ocean/* -> OCEAN_BASE
- /health and /backend/* -> API_BASE

### Internal backend target layer

Targets are container DNS names in docker network, for example:

- kloud-api:8000
- kloud-ocean-core:8030
- kloud-clx:11434

## Backend Internal Wiring

Backend wiring is controlled by app.include_router(...) in [apps/api/main.py](../apps/api/main.py).

Observed include points include domains like:

- unified
- neural
- fabric
- brain
- eeg
- audio
- fitness
- alba
- reporting
- kitchen
- excel
- user_data
- stripe_billing
- mymirror
- postman
- jona
- dns

This means the runtime chain is:

1. Gateway/rewrite selects backend service.
2. FastAPI main app selects router.
3. Router executes module handler.

## XLC Resonant Reading Wiring (MMM -> WWW)

Reference model is documented in [docs/architecture/XLC_RESONANT_READING_MODEL.md](architecture/XLC_RESONANT_READING_MODEL.md).

Operational wiring summary:

1. Input is normalized into known symbol sequence.
2. LayerBuilder computes WW, MM, CC (12D each).
3. XLCInspector.inspect_scan finds strongest resonance window.
4. Best combined score is selected.
5. Command/result is passed to response writer path.

Architecture components explicitly named in source document:

- LayerBuilder
- XLCInspector.inspect
- XLCInspector.inspect_scan
- XLCCommandMap
- XLCResponseWriter

This wiring must stay aligned with API orchestration when XLC-backed routes are added.

## Why Changes Did Not Reach Hosting

Most frequent root causes:

1. Local commit not synced to server checkout.
2. Server path mismatch or wrong target directory.
3. Wrong env filename edited (env instead of .env).
4. Service recreated without pulling latest branch SHA.
5. Full network teardown attempted and blocked by active endpoints.
6. Health check passed for one service but upstream rewrite still pointed elsewhere.

## Mandatory Deployment Flow

Run on server in /opt/kloud.

```bash
cd /opt/kloud

# 1) Sync code exactly
git fetch origin
git reset --hard origin/master
git rev-parse --short HEAD

# 2) Validate env filename and critical keys
[ -f .env ] || cp env .env
grep -n '^STRIPE_WEBHOOK_SECRET=' .env

# 3) Build only changed services
docker compose build ocean-core asi

# 4) Restart only changed services (no global down)
docker compose stop ocean-core asi
docker compose rm -f ocean-core asi
docker compose up -d --no-deps ocean-core asi

# 5) Verify runtime
docker compose ps | grep -E 'ocean-core|asi'
curl -s http://localhost:8030/health
curl -s http://localhost:9094/health
```

## Network Active Endpoints Playbook

Error pattern:

- network kloud_default has active endpoints

Golden rule:

- Do not run global docker compose down as first action.

Step-by-step:

```bash
# A) Prefer targeted restart
docker compose stop ocean-core asi
docker compose rm -f ocean-core asi
docker compose up -d --no-deps ocean-core asi

# B) If still blocked, inspect network attachments
docker network inspect kloud_default --format '{{json .Containers}}'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Networks}}'

# C) Remove only stale/disconnected offenders, then retry targeted up
```

## Release Discipline

1. Merge or push final code to master.
2. Sync hosting checkout to exact remote SHA.
3. Record deployed SHA and date in deployment log.
4. Restart only impacted services.
5. Run health plus one functional endpoint per changed service.
6. Confirm rewrite path from frontend reaches the updated backend.

## Minimum Functional Checks

For ocean-core:

- GET /health returns HTTP 200.
- docker compose logs ocean-core --tail 80 shows successful startup and no crash loop.

For asi:

- GET /health returns HTTP 200.
- docker compose logs asi --tail 80 shows successful startup and no crash loop.

For frontend rewrite integrity:

- /api/health resolves to backend health.
- One /api/ocean/* route resolves to ocean-core.

## Change Control And Stability Rules

This document must remain stable across deploys and branch switches.

### Stable core sections (must not be removed)

- Purpose
- Orchestration Map
- Mandatory Deployment Flow
- Network Active Endpoints Playbook
- Release Discipline
- Change Control Rules

### Volatile sections (allowed to change)

- Snapshot Inventory counts
- Service lists
- Route totals

### Governance rule

Any PR that changes one of these must also update this file:

- docker-compose service topology
- proxy/rewrite rules
- router registration paths
- deployment command flow

If not updated, deployment readiness is incomplete.

## Update Procedure For This Document

When updating counts or topology:

1. Recompute service count from [docker-compose.yml](../docker-compose.yml).
2. Recompute route handler count from backend scopes.
3. Revalidate proxy/rewrite chain from [nginx/default.conf](../nginx/default.conf) and [apps/web/next.config.js](../apps/web/next.config.js).
4. Revalidate backend include_router map from [apps/api/main.py](../apps/api/main.py).
5. Keep index section consistent with headings.

Last updated: 2026-05-17
