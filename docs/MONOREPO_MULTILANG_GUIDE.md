# Monorepo Multilangue & Multipaketa Guide

## Purpose

This document clarifies how this repository is organized across **JavaScript/TypeScript**, **Rust**, and **Python**, and provides a practical checklist for consistent development and PR preparation.

---

## 1) Repository Language/Package Topology

## JavaScript / TypeScript (Workspace Layer)

Source of truth: `package.json`

- Package manager: `yarn@4.10.3`
- Workspace roots:
  - `apps/*`
  - `packages/*`
- Typical commands are currently defined via root scripts that delegate to app/package folders.

Key root scripts:
- `dev`, `dev:web`, `dev:api`
- `build`, `build:web`, `build:api`
- `test`, `test:web`, `test:api`
- `lint`, `lint:web`

Notes:
- Root scripts currently use `cd ... && npm run ...` patterns.
- Workspace exists, but command style is mixed (`yarn` as packageManager, `npm run` in scripts).

---

## Rust (Workspace Layer)

Source of truth: `Cargo.toml`

Workspace members:
- `algebra`
- `protocol`
- `security`
- `node`
- `crates/core_api`
- `crates/ocean_core`
- `crates/asi_trinity`
- `crates/edge_gateway`
- `crates/worker_compute`
- `crates/telemetry_agent`
- `crates/telemetry_collector`

Recommended baseline commands:
```bash
cargo check --workspace
cargo test --workspace
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
```

---

## Python (Packaging + Isolated Dependency Strategy)

Source of truth: `pyproject.toml`

- Build backend: setuptools
- Python: `>=3.11`
- Core project deps are minimal.
- Optional extras split by domains:
  - `api`, `data`, `ocean`, `excel`, `ml`, `payments`, `observability`, `dev`
- Explicit isolation strategy is already present (especially for excel/ml).

Recommended installation patterns:
```bash
# Core
pip install -e .

# API profile
pip install -e ".[api]"

# Dev quality profile
pip install -e ".[dev]"
```

---

## 2) Operational Rules (Practical)

1. Keep package boundaries strict:
   - JS/TS code in `apps/*`, `packages/*`
   - Rust crates in Cargo workspace members
   - Python services/libs through `pyproject.toml` extras

2. Do not mix isolated Python domains casually:
   - `excel` and `ml` extras should remain isolated when required by constraints.

3. Keep deploy orchestration aligned with docs:
   - `docs/README.md`
   - `docs/HOSTING_EXECUTION_BASELINE.md`
   - `docs/DEPLOYMENT_CHECKLIST.md`
   - `deploy.sh`

4. For topology changes:
   - Any change in docker/service routing/deploy flow must update baseline docs per governance.

---

## 3) PR Prep Checklist (Multilang)

- [ ] JS/TS workspace commands run successfully for modified scope
- [ ] Rust workspace check/tests pass for impacted crates
- [ ] Python profile installs/tests pass for impacted services
- [ ] Documentation links and command examples remain accurate
- [ ] Deployment-related changes reflected in docs baseline/checklist

---

## 4) Server-Side GitHub CLI Recovery (gh vs gitsome conflict)

If `gh` command is missing on Ubuntu server and `apt install gitsome` removed it:

```bash
# remove gitsome if it conflicts in your environment
sudo apt remove -y gitsome

# install gh
sudo apt update
sudo apt install -y gh

# verify
gh --version
gh auth status
```

If distribution package is not sufficient, use GitHub CLI official installation method for Ubuntu.

PR view example:
```bash
gh pr view 5 --json number,title,headRefName,baseRefName,url,state
```

---

## 5) Recommended Standardization Path (Incremental)

1. Keep current scripts working (no disruptive refactor).
2. Gradually standardize root JS/TS scripts toward one toolchain style (prefer Yarn workspace-native flow).
3. Add language-specific CI jobs with explicit scope:
   - JS/TS workspace lint/test/build
   - Rust workspace check/test/fmt/clippy
   - Python extras-based validation per service profile
4. Maintain docs first-class: architecture/deployment docs must move together with runtime changes.
