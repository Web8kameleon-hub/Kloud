# Kloud Native Runtime File Map

This document consolidates the key files for the native fabric stack and local independent AI surfaces.

## WWWMMM + NDB + Stigma + Tide + Resonance

- Core runtime policy: `docs/TECHNOLOGY_FIRST_RUNTIME_POLICY.md`
- Main NodeDB engine: `nodendb_stigma.py`
- NodeDB integration layer: `nodendb_kloud_integration.py`
- NodeDB control plane API: `nodedb_control_plane_api.py`
- NodeDB snapshot artifact: `output/nodedb/nodedb_snapshot.json`
- Stigma architecture: `docs/STIGMA_CLOUD_COMPONENT_ARCHITECTURE.md`
- LPRI stigma fluid architecture: `docs/LPRI_STIGMA_FLUID_ARCHITECTURE.md`
- NodeDB stigma guide: `docs/NODENDB_STIGMA_GUIDE.md`
- NodeDB production gap map: `docs/NODENDB_PRODUCTION_GAP_MAP.md`
- NodeDB fluid membership recovery protocol: `docs/NODENDB_FLUID_MEMBERSHIP_RECOVERY_PROTOCOL.md`

## Snapshot Persistence And Restore (NodeDB)

- NodeMetadata deserialization: `nodendb_stigma.py` (from_dict)
- NodeState deserialization: `nodendb_stigma.py` (from_dict)
- Snapshot save path + write: `nodendb_stigma.py` (`_save_snapshot`)
- Snapshot load + restore: `nodendb_stigma.py` (`load_snapshot`)

## Tide + Resonant Surfaces

- Tide pressure and fallback logic: `9999/app.py`
- Resonant store/checkpointing variables: `9999/app.py`
- Resonant API outputs in Rust node API: `node/src/api.rs` (`/resonant/status`, `/resonant/events`)
- Tide calculation in Rust node runtime: `node/src/main.rs` (`compute_tide`)
- Tide-aware policy decisions: `node/src/policy_engine.rs`
- Tide-aware transport behavior: `protocol/src/lib.rs` (tide_send_digest/request/payload)

## Benchmark-Related Files

- EEG benchmark models and measurements: `eeg_metrics_fetcher.py`
- Observability benchmark section: `docs/observability/prometheus-metrics.md`
- General benchmark references: `COMPLETE_DELIVERY_SUMMARY.md`, `CLEANUP_REPORT_DEC2025.md`

## Local Independent AI And Domains

- CLX publisher engine: `clx_publisher.py`
- AI orchestration definitions (ALBA/ALBI/JONA): `agents.py`
- AI agent telemetry guide/docs: `AGENT_TELEMETRY_GUIDE.md`, `AGENT_TELEMETRY_DOCS.md`
- Public domain targets in deployment workflows:
  - `clisonix.ai` in `.github/workflows/deploy.yml`
  - `clx.clisonix.ai` in `.github/workflows/deploy.yml`
  - `lite.clisonix.ai` in `.github/workflows/deploy.yml`
  - `cxl.i` (requested as clx.i variant in runtime fabric tags) in `.github/workflows/deploy.yml`

## JONA + Sandbox Anchors

- JONA server endpoint surface: `jona_server.py`
- JONA service wrapper: `jona_service_7777.py`
- API-level JONA telemetry and status endpoints: `apps/api/main.py`
- Sandbox references:
  - `apps/web/src/components/asi/SandboxShield.tsx`
  - `research/sandbox_core.py`

## New Protocol Libraries Added In This Pass

- Governance contracts library: `protocol/src/governance_contracts.rs`
- Self-writing protocol library: `protocol/src/self_writing_protocol.rs`

These provide a Rust-native contract model for:

- Governance envelope validation
- Automatic approval/rejection gates
- JONA sandbox policy checks
- Self-writing protocol proposals, review, and promotion gates
