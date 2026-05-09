# Resonant Migration Plan

## Objective

Adopt Resonant Core (NDB, Stigma, Tide, Stigma Cloud) across Clisonix/Kloud with clear contracts, measurable schemas, compatibility adapters, and gradual rollout.

## Existing Adapter Foundations

- Python engine adapter contract: `core/engines/contract.py`
- Ollama implementation adapter: `core/engines/ollama_adapter.py`
- Ocean adapter layer: `ocean_core_adapter.ts`
- Existing pipeline framework: `ai_agi_pipeline.py`

These are reused as adapter patterns instead of introducing a parallel architecture.

## Contract and Schema

- Canonical contract: `docs/RESONANT_CORE.md`
- Architecture baseline: `docs/LPRI_STIGMA_FLUID_ARCHITECTURE.md`
- Hardware mesh brief: `docs/HARDWARE_MESH_BRIEF.md`
- Measurable schemas:
  - `docs/schemas/resonant-status.schema.json`
  - `docs/schemas/resonant-event.schema.json`

## Cross-Platform Runtime Alignment

- Adopt gyp-fluid runtime lanes for Python 3.12, 3.13, and gated 3.14.
- Keep one command surface for Windows 11 and Linux nodes.
- Route compatibility differences through adapters, not API breaks.

## Compatibility Adapters (Phase by Phase)

### Phase 1: Node API (Completed)
- Keep legacy endpoints unchanged.
- Add adapter endpoints:
  - `/resonant/status`
  - `/resonant/events`
- Return deterministic fields for compatibility and observability.

### Phase 2: Protocol and Security
- Map protocol memory/event outputs into Resonant event schema.
- Standardize trace identity and severity mapping.
- Keep old internals available while adapters are active.
- Concrete implementation checklist: `docs/PHASE2_PROTOCOL_SECURITY_CHECKLIST.md`

### Phase 3: Web and Dashboards
- Consume `/resonant/status` and `/resonant/events` in dashboards.
- Preserve legacy widgets with fallback reads from old endpoints.

## Rollout Guardrails

1. Never remove old endpoints in the same phase where new adapter endpoints are introduced.
2. Add schema validation in CI for resonant payloads.
3. Track success metrics:
   - adapter error rate
   - schema validation pass rate
   - endpoint latency
   - event ingestion consistency

## Exit Criteria

- All critical services expose or consume Resonant schemas.
- Compatibility layer remains stable for one release cycle.
- Legacy endpoints can then be marked deprecated (not removed immediately).
