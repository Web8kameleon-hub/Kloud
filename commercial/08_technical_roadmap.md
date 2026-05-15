# Kloud Sovereign Fabric Suite
## Technical & Commercial Roadmap — 6 Months
### Version 1.0 · May 2026 – November 2026

---

## OVERVIEW

This roadmap governs both the technical evolution of the Kloud Sovereign Fabric and the commercial actions required to generate revenue and reach market. Each month has clear deliverables, priorities, and go/no-go criteria.

**North Star Metric:** €50,000 MRR by Month 6 with 15+ paying clients.

**Current State (May 2026):**
- ✅ Node #1 live in production
- ✅ STIGMA L2 telemetry operational
- ✅ NDB score tracking active (0.041 — stable)
- ✅ CRDT state store committed (2 keys)
- ✅ /submit and /status endpoints live
- ✅ Control Surface panel fully operational
- ✅ Rust core compiled, Python FastAPI stack (75+ services)
- ✅ Commercial suite created (this document + 9 peers)

---

## MONTH 1 — MAY 2026 · "FOUNDATION"

### Theme: Solidify infrastructure. Launch commercial readiness.

### Technical Milestones

| Priority | Task                                                   | Status |
| -------- | ------------------------------------------------------ | ------ |
| P0       | Deploy Peer Node #2 (activate multi-peer mesh)         | 🔲 TODO |
| P0       | CRDT replication across peer #1 and #2                 | 🔲 TODO |
| P0       | TIDE dynamics between two peers validated              | 🔲 TODO |
| P1       | STIGMA L3 escalation logic + alerts                    | 🔲 TODO |
| P1       | NDB drift alerting (threshold crossing → webhook)      | 🔲 TODO |
| P1       | /events endpoint pagination + filtering                | 🔲 TODO |
| P2       | /crdt/state export endpoint (JSON + CSV)               | 🔲 TODO |
| P2       | Docker health checks and auto-restart                  | 🔲 TODO |
| P3       | Node ID generation deterministic (not timestamp-based) | 🔲 TODO |

### Commercial Milestones

| Priority | Task                                                      | Status |
| -------- | --------------------------------------------------------- | ------ |
| P0       | Launch commercial/ suite (complete ✅)                     | ✅ DONE |
| P0       | Register email addresses (enterprise@, sales@, security@) | 🔲 TODO |
| P0       | Landing page live on clisonix.com/kloud                   | 🔲 TODO |
| P1       | Identify first 10 outreach targets (LinkedIn, CTOs)       | 🔲 TODO |
| P1       | Send first 5 outreach messages                            | 🔲 TODO |
| P2       | Set up Stripe for payment processing                      | 🔲 TODO |
| P2       | SEPA direct debit setup                                   | 🔲 TODO |

### Go/No-Go Criteria for Month 2
- [ ] Peer #2 deployed and communicating
- [ ] CRDT replication confirmed across 2 nodes
- [ ] Landing page live
- [ ] At least 1 demo call scheduled

---

## MONTH 2 — JUNE 2026 · "FIRST CLIENTS"

### Theme: Onboard first paying clients. Harden production.

### Technical Milestones

| Priority | Task                                                       |
| -------- | ---------------------------------------------------------- |
| P0       | Multi-tenant node isolation (client-per-node or namespace) |
| P0       | API key per client provisioning system                     |
| P1       | Grafana dashboard template for client observability        |
| P1       | Prometheus metrics export for all core endpoints           |
| P1       | TLS termination validated on client deployments            |
| P2       | Structured logging (JSON) for all fabric services          |
| P2       | /metrics endpoint (Prometheus-compatible scrape)           |
| P3       | Python SDK v0.1 — /submit, /status, /events                |

### Commercial Milestones

| Priority | Task                                       |
| -------- | ------------------------------------------ |
| P0       | First client onboarded (Starter or Pro)    |
| P0       | Contract signed (Schedule A complete)      |
| P1       | Second client pilot initiated              |
| P1       | First invoice issued and paid              |
| P2       | Referral program activated                 |
| P2       | Social media presence activated (LinkedIn) |

### Go/No-Go Criteria for Month 3
- [ ] 2+ paying clients
- [ ] API key provisioning automated
- [ ] MRR ≥ €1,000

---

## MONTH 3 — JULY 2026 · "SECURITY POSTURE COMPLETE"

### Theme: Complete STIGMA + NDB feature set. Start enterprise conversations.

### Technical Milestones

| Priority | Task                                                |
| -------- | --------------------------------------------------- |
| P0       | STIGMA L3 full classification + alerting            |
| P0       | NDB baseline recalibration after 30 days live       |
| P1       | SIEM webhook integration (Datadog/Splunk/custom)    |
| P1       | Security posture history endpoint (/stigma/history) |
| P1       | CRDT conflict resolution visualization              |
| P2       | Peer mesh latency tracking (P50, P95, P99)          |
| P2       | Bandwidth measurement per endpoint                  |
| P3       | TypeScript SDK v0.1                                 |

### Commercial Milestones

| Priority | Task                                          |
| -------- | --------------------------------------------- |
| P0       | First Enterprise client conversation          |
| P0       | 5 paying clients total                        |
| P1       | Case study from Client #1 (brief written)     |
| P1       | LinkedIn content series started (1 post/week) |
| P2       | Partner outreach: Hetzner partner program     |
| P2       | EU AI Act compliance positioning document     |

### Go/No-Go Criteria for Month 4
- [ ] 5+ clients
- [ ] STIGMA L1–L3 all validated in production
- [ ] Enterprise conversation in pipeline
- [ ] MRR ≥ €5,000

---

## MONTH 4 — AUGUST 2026 · "KLOUD BRIDGE"

### Theme: Activate Kloud Bridge. Multi-node mesh at scale.

### Technical Milestones

| Priority | Task                                                   |
| -------- | ------------------------------------------------------ |
| P0       | Kloud Bridge activation — upstream fabric connectivity |
| P0       | 3+ node mesh tested under load                         |
| P1       | TIDE escalation across multi-node topology             |
| P1       | CRDT merge conflict test suite                         |
| P1       | Node failover and recovery tested                      |
| P2       | API rate limiting per client                           |
| P2       | Overage metering and billing integration               |
| P3       | Air-gap deployment tested (Enterprise only)            |

### Commercial Milestones

| Priority | Task                                           |
| -------- | ---------------------------------------------- |
| P0       | First Enterprise client signed                 |
| P0       | 10 paying clients total                        |
| P1       | Annual billing option activated                |
| P1       | Professional services first engagement         |
| P2       | Partnership agreement with 1 system integrator |
| P2       | Second case study published                    |

### Go/No-Go Criteria for Month 5
- [ ] Bridge active
- [ ] 10+ clients
- [ ] First Enterprise contract signed
- [ ] MRR ≥ €15,000

---

## MONTH 5 — SEPTEMBER 2026 · "SCALE"

### Theme: Multi-tenant management at scale. SDK v1 release.

### Technical Milestones

| Priority | Task                                        |
| -------- | ------------------------------------------- |
| P0       | Multi-tenant management panel (admin view)  |
| P0       | Python SDK v1.0 — stable, documented        |
| P0       | TypeScript SDK v1.0 — stable, documented    |
| P1       | Automated provisioning: new node in < 5 min |
| P1       | Automated billing: Stripe + SEPA metering   |
| P2       | Custom STIGMA rule engine (Enterprise)      |
| P2       | NDB custom threshold per client             |
| P3       | Kubernetes Helm chart for enterprise deploy |

### Commercial Milestones

| Priority | Task                              |
| -------- | --------------------------------- |
| P0       | 15+ paying clients                |
| P0       | Developer documentation site live |
| P1       | Enterprise deal #2 closed         |
| P1       | Referral revenue tracked (> 0)    |
| P2       | Conference presentation prepared  |

### Go/No-Go Criteria for Month 6
- [ ] 15+ clients
- [ ] SDKs v1 shipped
- [ ] Automated provisioning working
- [ ] MRR ≥ €25,000

---

## MONTH 6 — OCTOBER 2026 · "MILESTONE"

### Theme: €50k MRR milestone. Series A groundwork.

### Technical Milestones

| Priority | Task                                    |
| -------- | --------------------------------------- |
| P0       | 99.9% uptime audit for past 90 days     |
| P0       | Security penetration test + remediation |
| P1       | Enterprise SLA automated monitoring     |
| P1       | STIGMA L3 auto-response playbooks       |
| P2       | Fabric performance benchmark published  |
| P2       | Node count autoscaling (Enterprise)     |
| P3       | v2 architecture planning begins         |

### Commercial Milestones

| Priority | Task                                                |
| -------- | --------------------------------------------------- |
| P0       | €50,000 MRR achieved                                |
| P0       | 20+ paying clients                                  |
| P0       | Seed investor pitch deck updated with real traction |
| P1       | 3 Enterprise clients on annual contracts            |
| P1       | NPS survey sent to all clients                      |
| P2       | Series A groundwork: metrics deck, growth model     |

---

## TECHNICAL DEBT & RISK REGISTER

| Risk Item                             | Severity | Mitigation                   |
| ------------------------------------- | -------- | ---------------------------- |
| Single node = single point of failure | High     | Peer #2 deployment (Month 1) |
| No automated provisioning yet         | Medium   | Month 5 milestone            |
| Manual billing                        | Medium   | Stripe integration Month 2   |
| No pen test                           | Medium   | Month 6 security audit       |
| CRDT not tested under conflict load   | Low      | Month 4 test suite           |
| SDK not stable                        | Low      | Month 5 v1 release           |

---

## RESOURCE REQUIREMENTS

### Bootstrap Phase (Month 1–3, no hires)
- Ledjan: full-stack architecture, engineering, sales outreach
- Tools: Hetzner VPS, GitHub, Stripe, LinkedIn Premium
- Budget: ~€1,300/month

### Funded Phase (Month 4–6, with hire)
- Engineer #1: Backend/distributed systems
- Part-time sales support
- Budget: ~€8,000–€12,000/month

---

## SUCCESS DEFINITION

| Milestone                 | Target Date  | Status |
| ------------------------- | ------------ | ------ |
| Node #1 live              | ✅ May 2026   | DONE   |
| Commercial suite complete | ✅ May 2026   | DONE   |
| First paying client       | June 2026    | 🔲      |
| 5 clients                 | July 2026    | 🔲      |
| First Enterprise contract | August 2026  | 🔲      |
| €50k MRR                  | October 2026 | 🔲      |
| Series A ready            | Q1 2027      | 🔲      |

---

*Document version: 1.0 · May 2026 · Kloud Sovereign Fabric*  
*Living document — update monthly with actual vs. target*  
*© 2026 Kloud · All rights reserved*
