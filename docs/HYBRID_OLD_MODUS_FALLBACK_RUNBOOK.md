# Hybrid Old Modus Fallback Runbook

## Scope
Operational runbook for switching from native wwwmmm-ndb-stigma runtime to hybrid old modus and safely returning back.

## Decision Matrix
- Keep Native:
  - quality >= 0.75 and critical ratio <= 0.15
- Partial Fallback:
  - quality in [0.50, 0.75) or critical ratio in (0.15, 0.30]
- Full Hybrid Old Modus:
  - quality < 0.50 or critical ratio > 0.30

## Phase A: Detect
1. Read control-plane nodes snapshot.
2. Read sync-loop status.
3. Confirm repeated degradation across 3 cycles.

Evidence to capture:
- timestamp
- quality distribution
- affected node IDs
- recovery queue size

## Phase B: Enter Hybrid Old Modus
1. Mark incident state: `fallback-entering`.
2. Soft-isolate unstable nodes.
3. Shift traffic in stages (example):
   - Stage 1: 20% old modus
   - Stage 2: 40% old modus
   - Stage 3: 60% old modus (only if still unstable)
4. Keep sync loop active.
5. Keep membership updates active.

## Phase C: Stabilize
1. Trigger recovery plan for degraded nodes.
2. Monitor resonance and tide metrics every cycle.
3. Block aggressive topology changes.

## Phase D: Return to Native
1. Verify return criteria for 5 consecutive cycles.
2. Reverse traffic stages:
   - Stage 1: 40% old modus
   - Stage 2: 20% old modus
   - Stage 3: 0% old modus
3. Mark incident state: `native-restored`.

## Safety Rules
- Never hard-cut all traffic in one step.
- Never disable sync loop during fallback.
- Never remove nodes from membership history.

## Incident Template
- Incident ID:
- Trigger condition:
- Start time:
- Fallback level reached:
- Recovery actions executed:
- End time:
- Final mode:
- Lessons learned:

## Related Documents
- docs/TECHNOLOGY_FIRST_RUNTIME_POLICY.md
- docs/NODENDB_PRODUCTION_GAP_MAP.md
- docs/NODENDB_FLUID_MEMBERSHIP_RECOVERY_PROTOCOL.md
