# Kloud Stigma Cloud Component Architecture

## Vision

This architecture defines Kloud as a low-power, resonance-first distributed system where traces are durable, verifiable, and recoverable across edge and cloud mesh nodes.

Primary direction:

- Stigma evolves into a fluid cloud memory layer.
- Traces are append-only and integrity-preserving.
- Nanogrid nodes run with low compute pressure (LPRI profile).
- Every write is identity-bound, signed, chained, and replay-protected.

## 1) Kloud Control Plane

Responsibilities:

- Node identity and policy distribution.
- Routing rules for edge and cloud paths.
- Service discovery across AI engines and data-plane peers.
- Observability aggregation (metrics, traces, system pressure).

Core contracts:

- Identity document per node (`node_id`, `writer_id`, `public metadata`).
- Policy bundle (`allowed_routes`, `write_roles`, `quorum_rules`).
- Route map (`service`, `region`, `edge_class`, `failover_group`).

## 2) Nanogrid Data Plane

Responsibilities:

- Mesh transport between N1/N2/N3 and cloud peers.
- Quorum-based replication for append-only traces.
- Failover and recovery when nodes are degraded/offline.

Data-plane mechanics:

- Mesh gossip for liveness and pressure sharing.
- Quorum replication (`W` writes, `R` reads, configurable by policy).
- Deterministic failover order by tide-pressure and latency.

## 3) Resonant Core

Resonant Core services:

- NDB: resonance quality signal for traces and nodes.
- Tide: dynamic pressure/tension signal for read/write flow.
- Stigma: canonical trace envelope and continuity model.
- Stigma Cloud: shared fluid memory field across nanogrid.
- LPRI: low-power runtime profile and scheduling mode.

Control intent:

- If Tide rises, throttle non-critical writes and prioritize integrity paths.
- If NDB delta increases, trigger validation and recovery workflows.

## 4) Fluid Memory Architecture

Rules:

- Append-only event ingestion.
- Immutable historical trail.
- Recovery by checkpoint + replay.
- Trace integrity verified continuously.

Persistence model:

- Event segments (append-only).
- Snapshot checkpoints for startup speed.
- Replay from chain continuity for exact reconstruction.

## 5) Event Chain

Every event includes:

- `prev_hash`
- `chain_hash`
- `signature`
- `writer_id`
- `nonce`
- `client_ts_ms`

Validation sequence:

1. Validate schema and writer identity.
2. Validate anti-replay nonce window.
3. Validate signature over canonical message.
4. Validate `prev_hash -> chain_hash` continuity.
5. Persist and replicate under quorum policy.

## 6) Security Envelope

Baseline controls:

- Writer identity binding per event.
- Replay protection (`writer_id + nonce + TTL`).
- Key rotation with active key ID (`kid`) and keyring.
- Signature verification on every write path.

Operational controls:

- Admin-gated rotation endpoint.
- Strict clock skew window for client timestamps.
- Structured audit events for rejected writes.

## 7) AI Engines

Registered engines:

- Ocean Core
- ALBA
- ALBI
- ALDA
- ASI
- JONA
- LIAM
- CYCLE

Engine role in this architecture:

- Engines produce and consume resonant traces.
- Engines should emit status and pressure metrics.
- Engine outputs should be chained into Stigma event continuity where applicable.

## 8) Inference Layer

Inference providers:

- Ollama
- vLLM
- CLX-I

Routing goals:

- Select inference path by availability, latency, and Tide pressure.
- Keep fallback routes deterministic and policy-driven.

## 9) Hotguard AutoLearning

Purpose:

- Analyze local materials and generate actionable knowledge.
- Produce traceable artifacts with source lineage.

Requirements:

- Material ingestion logs are append-only.
- Generated knowledge includes provenance metadata.
- Training/learning events join the same event-chain integrity rules.

## 10) API Platform

Minimum endpoints:

- `/health`
- `/status`
- `/api/v1/resonant/status`
- `/api/v1/resonant/events`

API rules:

- Status endpoints expose pressure, integrity, and chain head hash.
- Event write endpoints enforce signature, nonce, and hash continuity.

## 11) Edge Nodes (Windows + Linux)

Edge profile:

- N1, N2, N3 classes with lightweight runtime budgets.
- Same API contract across Windows and Linux.
- Graceful degradation under elevated Tide pressure.

Edge objective:

- Preserve trace continuity and mesh participation even on low-power hardware.

## 12) Cloudflare and DNS

Control goals:

- Secure ingress and route shaping.
- Zero-trust posture for write endpoints and control APIs.
- DNS and edge routing policy aligned with control-plane identity.

## 13) Observability

Required views:

- Dashboards for service health and route availability.
- Telemetry for NDB/Tide/Stigma continuity.
- Metrics for system pressure and queue depth.
- Event-chain integrity checks and replay-block counts.

Minimum metrics:

- `resonant_events_total`
- `resonant_chain_integrity_ok`
- `replay_rejections_total`
- `tide_pressure_ratio`
- `ndb_delta`
- `key_rotation_total`

## Future State: Stigma as Fluid Cloud

Target statement:

- Stigma Cloud becomes a fluid, non-lossy trace continuum.
- Historical traces are not mutated.
- Corruption is detectable, recoverable, and never silent.
- Trace continuity remains auditable end-to-end.

Roadmap phases:

1. Standardize identity and signing envelope on all write paths.
2. Expand quorum replication and checkpoint/replay automation.
3. Enforce integrity and pressure gates platform-wide.
4. Move dashboards and operators to resonance-first controls by default.
