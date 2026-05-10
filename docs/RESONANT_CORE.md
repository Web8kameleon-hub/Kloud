# Resonant Core

## Purpose

Resonant Core is the shared technical contract for the Kloud/Kloud ecosystem. It defines how noise, resonance, traces, and operational pressure are represented across services, dashboards, and storage layers without breaking existing REST/JSON interfaces.

## Core Primitives

### NDB

- Nano-decibel resonance metric.
- Used to score signal pressure, behavioral drift, and operational stability.
- Exposed as `ndb_score`, `ndb_delta`, and `ndb_threshold`.

### Stigma

- Noise trace memory imprint.
- Represents persistent traces left by symbolic or operational events.
- Used for event audit, memory retention, and risk classification.

### Tide

- Operational pressure band.
- Controls gating, throttling, and allowed actions.
- Typical levels: `Low`, `Normal`, `High`.

### Stigma Cloud

- Fluid, durable memory layer for trace preservation.
- Designed to avoid corruption of trace history and allow recovery of resonance state.
- Acts as the long-lived storage model for trace and event history.

## Compatibility Rules

1. Keep existing REST and JSON endpoints stable.
2. Add Resonant Core adapters rather than replacing public contracts at once.
3. Expose old and new fields together during migration.
4. Prefer deterministic, small, testable increments.
5. Treat safety, security, and observability as first-class concerns.

## Migration Targets

The first repositories and services to adopt this model should be:

- `node` API and dashboard
- `protocol` message, transport, and memory layers
- `security` event and policy logic
- `apps/web` dashboards and widgets
- `backend/layers` policy and sandbox behavior
- deployment manifests, smoke scripts, and observability docs

## Canonical Fields

- `state`
- `tide`
- `ndb_score`
- `ndb_delta`
- `ndb_threshold`
- `stigma_level`
- `high_risk`
- `event_count`
- `trace_id`
- `trace_state`

## Rollout Strategy

### Phase 1

Define the contract and keep the current endpoints compatible.

Test the first slice at 5% on one low-risk service path, with old and new fields returned together.

Expand to 25% only after the 5% slice is stable and WWWMMM validation is enforced on the adapter path.

Treat unresolved or non-verifiable "fake concepts" as quarantine candidates and keep them out of promoted 25% traffic.

### Phase 2

Move service internals to consume the shared contract.

### Phase 3

Normalize dashboards, exporters, and policy engines.

### Phase 4

Add optional advanced storage behavior for Stigma Cloud while preserving legacy access patterns.

## Non-Goals

- Do not remove current APIs in the first migration step.
- Do not force heavyweight compute.
- Do not introduce breaking schema changes without adapters.

## Status

This file is the starting point for the shared architecture model.

## Measurable Schemas

- `docs/schemas/resonant-status.schema.json`
- `docs/schemas/resonant-event.schema.json`

## Migration Plan

- `docs/RESONANT_MIGRATION_PLAN.md`

## LPRI and Fluid Architecture

- `docs/LPRI_STIGMA_FLUID_ARCHITECTURE.md`
