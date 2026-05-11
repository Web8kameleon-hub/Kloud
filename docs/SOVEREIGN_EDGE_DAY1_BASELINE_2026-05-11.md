# Sovereign Edge Day 1 Baseline Report

Date: 2026-05-11
Environment: Kloud production control surface

## Snapshot

- node identity: #1
- tide: low
- active peers: 1
- ndb score: 0.040
- ndb delta: -0.611 vs threshold 0.65
- security posture: stable
- tracked security events: 6
- latency: 15 ms
- node load: 0.00
- state keys: 2

## Event Summary

Recent operations include accepted submit operations and read-status checks with stigma level 2 and outcome ok/accepted.

## Baseline Verdict

Day 1 baseline is healthy and suitable for PoP expansion planning.

## Risks To Watch

1. single active peer remains a single-fault condition
2. DNS authority is not yet sovereign
3. multi-region failover has not yet been drilled

## Actions Approved For Day 2

1. harden PoP 1 routing and write-path protections
2. validate adaptive writes and state continuity
3. prepare PoP 2 deployment assets
