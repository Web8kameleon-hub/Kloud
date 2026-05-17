# Kloud Documentation Index

## Deployment & Operations

### 🚀 Quick Start
**→ [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** (1 page)
- Step-by-step checklist for server deployments
- Health checks and rollback procedures
- Referenced by: deploy.sh, HOSTING_EXECUTION_BASELINE.md

### 📋 Hosting Execution Baseline
**→ [HOSTING_EXECUTION_BASELINE.md](HOSTING_EXECUTION_BASELINE.md)** (14 sections)
- **Purpose:** Single source of truth for hosting, orchestration, and deployment
- **Contents:** Service inventory, orchestration map, routing paths, deployment flow, network error playbook, change control
- **Audiences:** DevOps, deployment team, architects
- **Key metrics:** 89 services, 887 route handlers, 4 documented call chains
- **When to use:** Before any deployment, when troubleshooting network issues, to understand service choreography

### 🏗️ Architecture Wiring & Deep Analysis
**→ [../ARCHITECTURE_WIRING_DEEP_ANALYSIS_KLOUD.md](../ARCHITECTURE_WIRING_DEEP_ANALYSIS_KLOUD.md)** (6 sections)
- **Purpose:** Technical deep dive into service contracts, risk points, and failure modes
- **Contents:** Docker Compose wiring, port/env validation, startup order risks, endpoint mismatches, architectural stability rules
- **Audiences:** Developers, architects, debugging teams
- **Key patterns:** Rules of boundaries, agent purity, storage access contracts
- **When to use:** When designing new services, debugging cross-service failures, understanding architectural constraints

---

## Deployment Tools

### 🔧 deploy.sh (Root Directory)
**→ [../deploy.sh](../deploy.sh)** (Bash script)
- Automated deployment script following HOSTING_EXECUTION_BASELINE.md exactly
- Includes: ENV validation, targeted service restart (no global down), health checks, error recovery
- **Usage:** `bash deploy.sh`
- **Environment variables:** `SERVER_HOST`, `SERVER_USER`, `SERVER_PORT`, `SERVICES_TO_BUILD`
- **Output:** Color-coded status, rollback guidance if health checks fail

---

## Documentation Relationships

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ARCHITECTURE_WIRING_DEEP_ANALYSIS.md (Technical/Design)                │
│ ├─ Risk points, failure modes, boundary rules                          │
│ └─ Referenced by → HOSTING_EXECUTION_BASELINE.md                       │
└─────────────────────────────────────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ HOSTING_EXECUTION_BASELINE.md (Operational/Reference)                  │
│ ├─ Service counts, orchestration map, routing paths                    │
│ ├─ Mandatory deployment flow with exact commands                       │
│ ├─ Network error playbook (active endpoints)                           │
│ └─ Change control rules (stable vs volatile sections)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT_CHECKLIST.md (Quick Reference / 1-Page)                     │
│ ├─ Step-by-step checklist for deploy team                              │
│ ├─ Pre-deployment validation                                           │
│ ├─ Rollback procedures                                                 │
│ └─ Points to baseline docs for detailed reference                      │
└─────────────────────────────────────────────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ deploy.sh (Automated / Executable)                                     │
│ ├─ Implements HOSTING_EXECUTION_BASELINE.md procedures in bash         │
│ ├─ Error handling and health checks                                    │
│ └─ Remote SSH execution to server                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## When To Use Which Document

| Scenario                                      | Document                                             | Why                                                                      |
| --------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| **Designing a new service**                   | Architecture Wiring                                  | Understand boundary rules, storage contracts, observability requirements |
| **Preparing a deployment**                    | Deployment Checklist                                 | Quick, actionable steps                                                  |
| **Deploying automatically**                   | deploy.sh                                            | Bash script with error handling                                          |
| **Understanding the system**                  | Hosting Execution Baseline                           | Single source of truth for running services                              |
| **Debuggging "works local, fails on server"** | Hosting Execution Baseline § 8 + Architecture Wiring | Root cause analysis                                                      |
| **Network error "active endpoints"**          | Hosting Execution Baseline § 10                      | Playbook with recovery steps                                             |
| **Verifying topology hasn't drifted**         | Hosting Execution Baseline § 3, § 4                  | Service counts and orchestration map                                     |

---

## Key Governance Rules

From **HOSTING_EXECUTION_BASELINE.md § 13: Change Control**

### Stable Core Sections (Must Never Be Removed)
- Purpose
- Orchestration Map
- Mandatory Deployment Flow
- Network Active Endpoints Playbook
- Release Discipline
- Change Control Rules

### Volatile Sections (Allowed To Change)
- Service counts (§ 2 Snapshot Inventory)
- Route handler totals
- Service lists (§ 3)

### Trigger Updates
Any PR that changes **these must also update HOSTING_EXECUTION_BASELINE.md**:
- docker-compose service topology
- proxy/rewrite rules
- router registration paths
- deployment command flow

**If not updated → deployment readiness is incomplete.**

---

## Metadata

| Document                             | Last Updated | Author       | Type                  |
| ------------------------------------ | ------------ | ------------ | --------------------- |
| ARCHITECTURE_WIRING_DEEP_ANALYSIS.md | 2026-05-17   | blackbox AI  | Technical/Design      |
| HOSTING_EXECUTION_BASELINE.md        | 2026-05-17   | Kloud team   | Operational/Reference |
| DEPLOYMENT_CHECKLIST.md              | 2026-05-17   | AI Assistant | Quick Reference       |
| deploy.sh                            | 2026-05-17   | AI Assistant | Operational Script    |

---

## Questions or Issues?

1. **How do I deploy?** → Start with DEPLOYMENT_CHECKLIST.md
2. **Why did my deploy fail?** → Check HOSTING_EXECUTION_BASELINE.md § 8-10
3. **How do services talk to each other?** → See HOSTING_EXECUTION_BASELINE.md § 4-6 (Orchestration Map)
4. **Can I add a new microservice?** → Read ARCHITECTURE_WIRING_DEEP_ANALYSIS.md § 5.1 (Rules of Boundaries)
5. **How do I know what changed?** → Check HOSTING_EXECUTION_BASELINE.md § 14 (Update Procedure)
