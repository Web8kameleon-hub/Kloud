# Sovereign Edge 7-Day Rollout Plan

## Objective

Deliver a production-safe 3-PoP sovereign edge rollout in seven days with measurable gates.

## Day 1: Baseline and Freeze

Goals:

- freeze current routing and deployment surfaces
- capture baseline telemetry
- confirm control-plane stability

Tasks:

1. Record current status, resonant metrics, and scan-print output.
2. Confirm sync-loop cadence and cycles.
3. Verify current API ingress path and nginx routing.
4. Mark current DNS records and TTL values.

Exit criteria:

- baseline report stored
- no unknown failing nodes
- rollback owner assigned

Reference artifact:

- `docs/SOVEREIGN_EDGE_DAY1_BASELINE_2026-05-11.md`

## Day 2: PoP 1 Hardening

Goals:

- make primary edge deterministic and observable

Tasks:

1. Validate PoP 1 runtime endpoints.
2. Validate TLS termination.
3. Enforce route-level protections for write paths.
4. Verify resonant adaptive write and state key creation.

Exit criteria:

- PoP 1 health checks all pass
- adaptive write accepted
- state map non-empty

## Day 3: PoP 2 Bring-Up

Goals:

- add warm standby edge in separate region

Tasks:

1. Deploy edge proxy and runtime on PoP 2.
2. Register PoP 2 in control-plane route map.
3. Validate health and status endpoints.
4. Confirm PoP 2 appears in scan-print without stale duplicates.

Exit criteria:

- PoP 2 is reachable and healthy
- control plane sees PoP 2 as available

## Day 4: PoP 3 Recovery Node

Goals:

- add recovery PoP in separate fault domain

Tasks:

1. Deploy PoP 3 runtime and ingress.
2. Register PoP 3 with failover_group and low default weight.
3. Run smoke checks on health, status, and resonant status.

Exit criteria:

- PoP 3 is in standby and healthy
- no regression on PoP 1 and PoP 2

## Day 5: DNS Transition and Routing Policy

Goals:

- enable independent DNS strategy and failover order

Tasks:

1. Configure authoritative DNS targets for all PoPs.
2. Apply low TTL for fast rollback.
3. Apply weighted or latency-aware records.
4. Validate global lookup and response consistency.

Exit criteria:

- DNS returns expected targets
- health-based routing policy is active

## Day 6: Failure Drills

Goals:

- prove resilience before promotion

Tasks:

1. Simulate PoP 1 outage.
2. Verify traffic shift to PoP 2.
3. Simulate PoP 2 outage.
4. Verify recovery route to PoP 3.
5. Restore all PoPs and validate return-to-normal.

Exit criteria:

- service continuity maintained
- no data integrity break
- recovery time recorded

## Day 7: Promotion and Monitoring

Goals:

- finalize production routing and enforce operations cadence

Tasks:

1. Promote 3-PoP policy to production.
2. Enable alerts for latency, health, and resonant integrity.
3. Freeze change window for 24h observation.
4. Publish operations handoff checklist.

Exit criteria:

- production stable for 24h
- incident log empty or resolved
- handoff completed

## Global Rollback Criteria

Rollback if any of the following occurs:

- sustained status failure > 5 min
- chain integrity failure > 0 during rollout
- write rejection spike > 5%
- unresolved sync-loop interruption

Rollback actions:

1. route to PoP 1 only
2. disable write routing to secondary PoPs
3. restart bootstrap and sync-loop
4. re-run smoke checks
