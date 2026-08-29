# docs/public — Customer & Integration Docs (PUBLIC)

Status: **PUBLIC — safe for customers, SDK users, and marketing**
Owner: WEB8euroweb GmbH

## Scope
This folder contains **integration-only** documentation: how to call the public API,
authenticate, and use the SDKs. It intentionally excludes internal algorithms.

## Publication Boundary (must-follow)
**Allowed here:**
- High-level capability descriptions.
- Public API contract behavior (endpoints, request/response shapes, status codes).
- Performance/reliability *outcomes* (e.g. latency envelopes) without internal math.
- SDK usage examples (Python / TypeScript).

**Never here (→ `docs/legal/`, restricted):**
- Internal resonance / NDB formulas, scoring matrices, threshold calibration.
- Attack/defense tuning specifics.
- Trade-secret source-level detail not required by customers.
- Invention disclosures or patent-preparation material.

## Public API Surface (integration)
| Area | Public endpoints (examples) | Notes |
|------|-----------------------------|-------|
| Sovereign chat | `POST /api/v1/chat` (clx-sovereign :40400) | CLX→CLX.I routing, structured error on outage. |
| Agents | `GET /agents`, `POST /agents/submit` (:40401) | Scalable agent orchestrator. |
| Data sources | `GET /api/v1/sources`, `GET /api/v1/categories` (:40402) | 4053 real free/open sources, 1001-category taxonomy. |
| Translation | `POST /api/v1/translate`, `POST /api/v1/detect` (:8036) | 72 languages. |
| Ocean chat | `POST /api/v1/chat`, `POST /api/v1/chat/stream` (:8030) | Multilingual (AL/DE/EN…). |

> Endpoint availability depends on deployment. See SDK docs for authenticated usage.

## SDKs
- Python SDK: `sdk/python/README.md`
- TypeScript SDK: `sdk/typescript/README.md`

## Contributing to public docs
- Keep examples runnable and honest (no fabricated numbers).
- If a doc would reveal internal math or tuning, it belongs in `docs/legal/`, not here.
