# Rust 2000-2030 Transition Plan

This plan translates the requested "Rust 2000-2030" progression into a practical modernization ladder for Kloud native runtime.

## Phase 2000 (Baseline)

- Keep Python/TS compatibility surfaces active.
- Route critical control-plane through NodeDB and JONA checks.
- Preserve snapshot persistence and restore behavior as the single source of runtime continuity.

## Phase 2010 (Protocol Consolidation)

- Move governance contracts into Rust protocol crate.
- Add self-writing proposal lifecycle with sandbox-only gates.
- Require NDB + tide checks before protocol promotion.

## Phase 2020 (Governance Automation)

- Enforce JONA sandbox for all self-learning and self-writing proposals.
- Allow auto-promote only when risk and NDB quality thresholds pass.
- Add signed audit records per proposal decision.

## Phase 2030 (Native-First Runtime)

- Run Rust-native fabric as first-class core path.
- Keep Python/TS as adapter layers and observability surfaces.
- Execute benchmark gates for latency, stability, and recovery before rollout.

## Required Gates

- Snapshot restore integrity gate
- Tide pressure safety gate
- Stigma recovery gate
- Governance rejection gate
- JONA sandbox mandatory gate for elevated-risk protocol changes
