# Hardware Mesh Brief

## Purpose

This brief turns the shared vision into an executable shape across three layers:

1. Contract: Resonant Core and Stigma Cloud semantics
2. Network: Kloud, Nanogrid, DNS, and security orchestration
3. Hardware: distributed AI hardware nodes

The target is low-power, cross-platform operation with strong trace integrity.

## Layer A: Contract (Resonant Core, Stigma Cloud, LPRI)

### Contract Baseline

All hardware nodes and services must align to Resonant Core fields and behavior:

- ndb_score
- ndb_delta
- ndb_threshold
- tide
- stigma_level
- trace_id
- trace_state
- event_count

Stigma Cloud behavior remains append-only and replay-safe.

### LPRI Constraints

- Favor deterministic processing over heavy model execution.
- Prioritize signal quality and stability over throughput spikes.
- Support degraded mode with explicit Tide state changes.

## Layer B: Network Orchestration (Kloud, Nanogrid, DNS, Security)

### Kloud Control Plane

Kloud is responsible for:

- Node enrollment and identity issuance
- Policy distribution
- Version and lane compatibility control
- Health rollup and fleet-level routing decisions

### Nanogrid Data Plane

Nanogrid is responsible for:

- Peer discovery and mesh topology updates
- Event replication and replay propagation
- Quorum acknowledgment for trace durability
- Local failover and peer handoff under pressure

### DNS and Addressing

- Each node exposes a stable service identity.
- DNS names resolve to active node endpoints.
- Service discovery must tolerate partial partition and dynamic peer changes.

### Security Envelope

Minimum controls:

- Mutual authentication between node and Kloud plane.
- Signed event segments and writer identity validation.
- Policy-based access control for status/events APIs.
- Rotating credentials and replay-resistant request signatures.

## Layer C: Distributed Hardware

## What is an AI Hardware Node in this ecosystem?

An AI hardware node is a lightweight compute endpoint that:

- Runs resonant adapters and mesh client logic
- Produces and consumes Resonant Core events
- Persists append-only local trace segments
- Replicates traces to peers in nanogrid mesh
- Operates on Windows 11 or Linux through gyp-fluid runtime lanes

It is not required to host heavy GPU workloads.

## Node Capability Tiers

- Tier N1: edge-safe, low-memory, basic resonance processing
- Tier N2: standard node with richer policy and buffering
- Tier N3: coordination node for quorum and recovery acceleration

## Required Node APIs

Every node must expose:

- GET /health
- GET /status
- GET /resonant/status
- GET /resonant/events
- POST /resonant/events (ingestion from trusted peers)

## Required Resonant Fields to Expose

Status payload minimum:

- node_id
- state
- tide
- ndb_score
- ndb_delta
- stigma_level
- event_count
- active_peers
- security_mode
- runtime_lane

Event payload minimum:

- event_id
- trace_id
- timestamp_utc
- tide
- ndb_score
- ndb_delta
- stigma_level
- payload_hash
- prev_hash
- chain_hash
- writer_id
- signature

## Node to Nanogrid and Kloud Binding

### Status Flow

1. Node emits local status and resonant status.
2. Nanogrid aggregates peer awareness.
3. Kloud control plane consumes summarized health for routing and policy.

### Security Flow

1. Node authenticates with control plane.
2. Node receives policy bundle and trust anchors.
3. Node signs event segments.
4. Peers validate signature before ingest.

### Events Flow

1. Node appends local event to chain.
2. Node publishes event metadata to mesh.
3. Peers replicate by policy and quorum rules.
4. Kloud indexes operational events for observability.

## Compatibility with gyp-fluid Runtime

- py312 lane: baseline compatibility
- py313 lane: preferred production lane
- py314 lane: gated and policy-controlled lane

Adapters hide OS/runtime differences and keep API behavior stable.

## Hardware Planning Guidance

- Prefer many low-power nodes over a small number of heavyweight nodes.
- Keep local storage append-only and checkpointed.
- Size network links for replication durability, not peak model throughput.
- Use fault domains to avoid correlated node failures.

## Success Criteria

- Stable service under low-power conditions.
- No unverified event accepted into trace chain.
- Deterministic recovery after node restart.
- Quorum replication reaches policy threshold.
- Compatible operation on Windows 11 and Linux.

## Next Implementation Steps

1. Add node capability advertisement in resonant status payloads.
2. Add signed segment manifest generation in protocol/security layers.
3. Add fleet-level health and lane dashboards in Kloud.
4. Add automated audit jobs for chain and Merkle verification.

## Phase 2 Execution Checklist

- `docs/PHASE2_PROTOCOL_SECURITY_CHECKLIST.md`
