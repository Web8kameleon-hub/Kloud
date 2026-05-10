# Resonant Phase 1 5% Pilot Checklist

## Purpose

Validate the first rollout slice at 5% before expanding the Resonant Core contract to more service paths.

## Scope

- Keep existing endpoints unchanged.
- Return old and new fields together.
- Test one low-risk service path first.
- Do not widen rollout until the checklist passes.

## Pre-Flight

1. Confirm the target service is healthy.
2. Confirm the legacy endpoint still returns the original payload.
3. Confirm the resonant adapter endpoint returns deterministic fields.
4. Confirm logging and metrics are enabled.

## Pilot Test Steps

1. Route 5% of reads or calls to the resonant adapter path.
2. Keep 95% on the legacy path.
3. Compare response time, error rate, and schema shape.
4. Record any mismatch in `ndb_score`, `ndb_delta`, or `trace_state`.
5. Verify there is no break in existing client behavior.

## Pass Criteria

- Legacy endpoint remains stable.
- Adapter endpoint matches the contract.
- Error rate stays at or below the current baseline.
- Response latency stays within the acceptable envelope.
- No schema regression appears in logs or smoke checks.

## Fail Criteria

- Any breaking payload change.
- Any missing field required by the contract.
- Any repeatable spike in latency or errors.
- Any client-visible regression.

## Rollback

1. Disable the 5% adapter routing.
2. Keep the legacy path active.
3. Capture the failure evidence.
4. Fix the adapter before retrying.

## Next Step

If this 5% pilot passes, execute the 25% checklist in `docs/RESONANT_PHASE1_25PERCENT_CHECKLIST.md` and keep the same test structure.
