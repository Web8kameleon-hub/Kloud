# Technology-First Runtime Policy

## Purpose

Define the mandatory runtime rule for Kloud fabric:

1. Always run the native stack first: wwwmmm -> ndb -> stigma -> nodesndb -> fluid resonance -> metric-tide.
2. If native stack quality drops below safe thresholds, switch to hybrid old modus without hard cut.

## Mandatory Principle

- First mode is always technology-native mode.
- Hybrid old modus is a controlled fallback mode, not a default mode.

## Activation Order (Native)

1. Bootstrap control-plane.
2. Bootstrap nodes and membership.
3. Start sync loop.
4. Validate resonance metrics and tide stability.
5. Keep traffic in native mode while quality is healthy.

## Health Gates (Native Mode)

Native mode remains active if all are true:

- Global quality score >= 0.75
- Critical node ratio <= 0.15
- Sync loop freshness <= 2 x interval
- Recovery queue is not saturated

## Fallback Triggers (Hybrid Old Modus)

Switch to hybrid old modus when any trigger persists across 3 consecutive cycles:

- Global quality score < 0.50
- Critical node ratio > 0.30
- Sync loop stalled for > 3 intervals
- Recovery failures on same node > 2

## Fallback Strategy (Non-Aggressive)

- Do not hard stop native mode.
- Shift traffic gradually by staged weights.
- Keep collecting native metrics during fallback.
- Keep recovery orchestration active.

## Return-to-Native Criteria

Return from hybrid old modus to native mode only when all are true for 5 consecutive cycles:

- Global quality score >= 0.80
- Critical node ratio <= 0.10
- Sync loop healthy and stable
- No active hard failures

## Operator Checklist

Before enabling native mode:

- Control-plane service healthy.
- Membership registry loaded.
- Snapshot restore completed.
- Sync loop interval set and running.

Before enabling fallback:

- Trigger reason recorded.
- Node recovery plan created.
- Traffic shift plan approved.

Before returning to native mode:

- Stability window completed.
- Metrics evidence exported.
- Incident note attached.

## Related Documents

- docs/NODENDB_PRODUCTION_GAP_MAP.md
- docs/NODENDB_FLUID_MEMBERSHIP_RECOVERY_PROTOCOL.md
- docs/HYBRID_OLD_MODUS_FALLBACK_RUNBOOK.md
