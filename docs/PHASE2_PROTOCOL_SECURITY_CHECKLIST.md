# Phase 2 Protocol/Security Implementation Checklist

## Scope

This checklist converts the architecture brief into concrete delivery tasks for:

- payload standardization
- signing and verification
- chain hash continuity
- quorum replication

Target modules:

- protocol
- security
- node API integration points

## Workstream A: Payload Contract

### A1. Define Protocol Payload Types

- [ ] Add canonical protocol event structure aligned with Resonant schema.
- [ ] Require the following fields in event payloads:
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
- [ ] Add explicit version field for payload evolution.
- [ ] Add strict serde validation and reject malformed payloads.

### A2. Normalize Severity/Tide Mapping

- [ ] Map existing severity classes to Tide bands deterministically.
- [ ] Add conversion function and tests for old-to-new mapping.
- [ ] Document unsupported values and fallback behavior.

### A3. API Compatibility

- [ ] Keep legacy payload support in adapter path.
- [ ] Emit both legacy and resonant fields during transition.
- [ ] Add compatibility metrics (legacy read/write counts).

## Workstream B: Signing and Verification

### B1. Canonical Signing Input

- [ ] Define canonical serialization order for signed fields.
- [ ] Exclude volatile transport headers from signing input.
- [ ] Add deterministic hash function choice to config.

### B2. Writer Identity and Key Management

- [ ] Add writer_id validation against trusted key ring.
- [ ] Add key rotation support with active + next key window.
- [ ] Add key revocation list checks.

### B3. Signature Lifecycle

- [ ] Sign every appendable event segment at write time.
- [ ] Verify signature before ingestion into persistent chain.
- [ ] Reject and quarantine invalid signatures.
- [ ] Emit explicit security event for verification failures.

### B4. Tests

- [ ] Unit tests: valid/invalid signature scenarios.
- [ ] Property tests: canonical serialization stability.
- [ ] Integration tests: key rotation and revocation handling.

## Workstream C: Chain Hash Continuity

### C1. Chain Construction

- [ ] Compute payload_hash from canonical payload bytes.
- [ ] Compute chain_hash from payload_hash + prev_hash + metadata.
- [ ] Persist prev_hash and chain_hash for each event.

### C2. Chain Verification

- [ ] Verify prev_hash continuity on append and replay.
- [ ] Detect forks and split-brain chain branches.
- [ ] Mark invalid segments as read-only and quarantined.

### C3. Checkpoints

- [ ] Add segment-level Merkle root checkpoints.
- [ ] Persist checkpoint manifest with signature.
- [ ] Support replay from last valid checkpoint.

### C4. Tests

- [ ] Unit tests: hash continuity across append/restart.
- [ ] Fault tests: corrupted segment detection.
- [ ] Replay tests: recovery from checkpoint.

## Workstream D: Quorum Replication

### D1. Replication Policy

- [ ] Define quorum policy (for example 2 of 3 peers).
- [ ] Support policy override by Tide band.
- [ ] Distinguish acked, pending, and failed replication states.

### D2. Peer Protocol

- [ ] Add idempotent peer ingest endpoint behavior.
- [ ] Add duplicate detection by event_id and chain_hash.
- [ ] Add anti-replay nonce/timestamp checks.

### D3. Commit Semantics

- [ ] Mark event durable only after quorum ack threshold.
- [ ] Keep local pending queue for below-quorum events.
- [ ] Retry with backoff and peer health weighting.

### D4. Tests

- [ ] Integration tests: quorum reached and durability state.
- [ ] Partition tests: degraded mode under peer loss.
- [ ] Rejoin tests: backfill and convergence.

## Workstream E: Observability and Runtime Safety

### E1. Metrics and Logs

- [ ] Add counters for signature_failures_total.
- [ ] Add counters for chain_breaks_total.
- [ ] Add counters for quorum_ack_ratio.
- [ ] Add histogram for replication_latency_ms.

### E2. Real-Time Health Signals

- [ ] Expose status fields: security_mode, runtime_lane, active_peers.
- [ ] Expose chain health state in resonant status endpoint.
- [ ] Emit NDB delta anomaly events on integrity incidents.

### E3. Guardrails

- [ ] Fail closed on signature and chain continuity errors.
- [ ] Do not mutate accepted historical events.
- [ ] Keep adapter compatibility during entire phase.

## Server Prerequisites for Phase 2 Testing

Install and verify on local/edge server:

- docker
- nginx
- certbot
- python3-certbot-nginx
- git
- curl
- jq
- tini

## Real-Time Test Checklist

### R1. Endpoint Liveness

- [ ] GET /health returns healthy state.
- [ ] GET /status returns tide and ndb fields.
- [ ] GET /resonant/status includes security_mode and runtime_lane.

### R2. Event Integrity

- [ ] POST valid signed event is accepted.
- [ ] POST invalid signature is rejected and logged.
- [ ] Chain hash continuity violations are quarantined.

### R3. Quorum Behavior

- [ ] Event is durable only after quorum is reached.
- [ ] Below-quorum events remain pending and retried.
- [ ] Recovered peers converge on same chain tip.

## Definition of Done (Phase 2)

- All protocol/security writes are signed and verified.
- Chain hash continuity is enforced and monitored.
- Quorum replication durability is active.
- Real-time tests pass on local server with documented evidence.
- Legacy compatibility path remains functional.
