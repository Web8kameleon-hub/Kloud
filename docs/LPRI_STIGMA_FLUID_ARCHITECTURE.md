# LPRI and Stigma Fluid Cloud Architecture

## Scope

This document formalizes the approved 4-layer direction:

1. LPRI (Low-Power Resonant Intelligence)
2. Stigma Fluid Cloud
3. Cross-platform gyp-fluid runtime
4. Integrity model (anti-corruption and anti-loss)

The architecture is designed for incremental adoption in Kloud without breaking existing APIs.

## Layer 1: LPRI (Low-Power Resonant Intelligence)

### Goal

Run resonant workloads on lightweight nodes instead of requiring heavy compute.

### Principles

- Compute follows resonance signal quality, not model size.
- NDB and Tide are first-class control signals.
- Processing units should be deterministic and small.
- Nodes must scale horizontally across mesh peers.

### Required Capabilities

- Lightweight node profile for Windows 11 and Linux.
- Adaptive task gating based on Tide and NDB thresholds.
- Backpressure routing through WWWMMM and mesh signals.
- Progressive quality mode when hardware resources are low.

### Metrics

- Node load under low-power profile
- Mean response latency per Tide band
- NDB stability drift per node
- Successful peer handoff rate in mesh

## Layer 2: Stigma Fluid Cloud

### Goal

Persist traces as long-lived resonant state while preserving replayability and continuity.

### Model

- Stigma trace is append-only.
- Trace history is immutable in write path.
- Trace recovery is deterministic from persisted chain state.
- Tide controls read/write pressure, not trace mutation.

### Data Contract (minimum)

- trace_id
- event_id
- timestamp_utc
- ndb_score
- ndb_delta
- stigma_level
- tide
- payload_hash
- prev_hash
- chain_hash

### Storage Behavior

- Append-only event segments.
- Periodic compaction without semantic loss.
- Snapshot plus replay model for fast startup.
- Multi-peer mirrored replication in nanogrid mesh.

## Layer 3: Cross-Platform gyp-fluid Runtime

### Goal

Use one runtime concept for Windows 11 and Linux with Python 3.12, 3.13, and 3.14 lanes.

### Runtime Contract

- Same command surface across operating systems.
- Runtime chooses compatible interpreter lane.
- Adapter layer normalizes OS and interpreter differences.
- Existing endpoints remain backward compatible.

### Interpreter Lanes

- py312 lane: compatibility-safe profile
- py313 lane: preferred profile
- py314 lane: experimental profile with strict gating

### Adapter Responsibilities

- Normalize filesystem and process differences.
- Normalize scheduling and environment variables.
- Surface common telemetry for WWWMMM, NDB, Tide, and Stigma.
- Fail closed with explicit compatibility reason codes.

## Layer 4: Integrity Model (Anti-Corruption and Anti-Loss)

### Goal

Guarantee trace integrity despite node failures, medium errors, or network partitions.

### Core Controls

- Hash-chain integrity: prev_hash -> chain_hash continuity.
- Merkle checkpoints per segment for efficient verification.
- Signed segment manifests from active writers.
- Quorum replication acknowledgments in mesh.
- Background audit and automatic repair from healthy peers.

### Verification Pipeline

1. Validate schema for each event.
2. Validate hash chain continuity.
3. Validate segment Merkle root.
4. Validate signature and writer identity.
5. Validate replication quorum state.

### Corruption Handling

- Mark segment read-only and quarantined.
- Recover from nearest valid checkpoint.
- Replay from replicated peers.
- Emit explicit NDB-delta anomaly event.

## Adoption Plan

### Step 1 (Current)

- Keep current API stable.
- Use resonant adapter endpoints in Node.
- Keep legacy payloads while emitting resonant fields.

### Step 2

- Map Protocol and Security internals to chain hash model.
- Introduce segment manifests and verification hooks.

### Step 3

- Move dashboard and web reads to resonant endpoints by default.
- Keep fallback to legacy endpoints for one release cycle.

### Step 4

- Enable stricter quorum and recovery automation.
- Mark legacy trace formats deprecated.

## Non-Goals

- No hard dependency on heavy GPU infrastructure.
- No breaking API switch in a single release.
- No silent mutation of historical trace records.

## Decision Record

Approved direction: 4-layer architecture is accepted for Kloud roadmap.

## Hardware Mesh Reference

- `docs/HARDWARE_MESH_BRIEF.md`
