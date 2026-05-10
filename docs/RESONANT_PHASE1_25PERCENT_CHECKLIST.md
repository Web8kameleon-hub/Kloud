# Resonant Phase 1 25% Rollout Checklist

## Purpose

Promote rollout from 5% to 25% only after stability gates pass and WWWMMM is enforced as a required validation module on port 9999 adapter traffic.

## Scope

- Keep legacy endpoints active and unchanged.
- Keep old and new fields together.
- Route 25% of low-risk traffic to resonant adapter paths.
- Require WWWMMM validation before response promotion.
- Quarantine unresolved or non-verifiable fake concepts.

## Pre-Flight

1. Confirm 5% checklist was completed with no unresolved blockers.
2. Confirm `/api/v1/resonant/status` is reachable and stable.
3. Confirm `/api/v1/resonant/events` and `/api/v1/resonant/metrics` are reachable.
4. Confirm logging includes WWWMMM verdict and fake-concept flags.
5. Confirm rollback switch can return traffic to legacy path within one action.

## 25% Rollout Steps

1. Route 25% of selected low-risk calls through the resonant adapter.
2. Keep 75% on the legacy path.
3. Enforce WWWMMM gate on adapter responses before publish.
4. Compare latency, error rate, and schema shape against 5% baseline.
5. Mark any non-verifiable concept as quarantined and exclude from promoted output.
6. Verify client behavior remains backward-compatible.

## Pass Criteria

- WWWMMM gate is active on all promoted 25% adapter calls.
- Fake-concept filter is active and emits traceable flags.
- No breaking schema regressions.
- Error rate is at or below defined threshold.
- Latency remains within accepted envelope.
- No client-visible regression.

## Fail Criteria

- WWWMMM check missing or bypassed.
- Fake-concept detection disabled or non-traceable.
- Any contract-breaking payload difference.
- Sustained increase in errors or latency.
- Any client-visible regression.

## Rollback

1. Disable 25% adapter routing.
2. Return traffic to legacy path immediately.
3. Preserve evidence: WWWMMM outcomes, fake-concept flags, error traces.
4. Fix gate/filter logic before retry.

## Next Step

After a stable 25% window, propose the next controlled slice with the same gates and evidence discipline.
