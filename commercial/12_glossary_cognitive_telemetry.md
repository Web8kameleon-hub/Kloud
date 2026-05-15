# Cognitive Telemetry Glossary
## One-page Reference for CTO/CISO/Platform Teams
### Kloud Sovereign Fabric · Version 1.0

---

## Quick Definition

**Cognitive Telemetry** is Kloud's behavioral integrity layer for distributed systems, built on three core signals:
- **BTI** (Behavioral Trace Index / STIGMA)
- **DAS** (Deviation Amplitude Score / NDB)
- **PFD** (Propagation Field Dynamics / Rezonance)

---

## Core Terms

| Term            | Enterprise Name                  | Short Definition                                  | Why it matters                                          |
| --------------- | -------------------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| STIGMA          | Behavioral Trace Index (BTI)     | Behavioral fingerprint of each operation          | Converts raw events into posture-aware behavior classes |
| NDB             | Deviation Amplitude Score (DAS)  | Scalar deviation from expected baseline           | Detects drift early before hard failures                |
| Rezonance       | Propagation Field Dynamics (PFD) | Spread of deviation across nodes over time        | Shows blast radius and stability risk                   |
| TIDE            | Fabric Tension Monitor           | Pressure indicator of mesh stability              | Early warning for distributed stress                    |
| CRDT State      | Distributed State Store          | Conflict-free, causally ordered state persistence | Keeps multi-node state consistent and auditable         |
| Control Surface | Operations UI Layer              | Live runtime, security, and state visibility      | Gives one operator view for decisions                   |

---

## STIGMA / BTI Levels

| Level | Label    | Meaning                        | Typical action                     |
| ----- | -------- | ------------------------------ | ---------------------------------- |
| L1    | Minimal  | Low-friction expected behavior | Observe                            |
| L2    | Standard | Normal operational behavior    | Continue with standard controls    |
| L3    | Compact  | Elevated behavioral pressure   | Escalate review and tighten policy |

---

## DAS Interpretation (example policy)

| DAS Band      | Interpretation      | Suggested response                          |
| ------------- | ------------------- | ------------------------------------------- |
| 0.000 - 0.200 | Stable              | Normal operations                           |
| 0.201 - 0.650 | Watch zone          | Increase monitoring and trace sampling      |
| > 0.650       | High-risk deviation | Trigger escalation and containment workflow |

---

## Plain-language Mapping

| Proprietary phrase  | Enterprise phrase                        |
| ------------------- | ---------------------------------------- |
| Behavioral imprint  | Behavioral trace                         |
| Deviation amplitude | Baseline-relative drift score            |
| Resonance field     | Propagation dynamics in distributed mesh |
| Fabric tension      | Stability pressure indicator             |

---

## Standard Usage Pattern

Use proprietary + enterprise alias on first mention:
- `STIGMA (BTI)`
- `NDB (DAS)`
- `Rezonance (PFD)`

Then use enterprise alias consistently in technical documentation.

---

## 30-second Elevator Line

Kloud applies per-operation behavioral tracing (BTI), baseline deviation scoring (DAS), and propagation analysis (PFD) to provide proactive security and stability control in sovereign distributed infrastructure.

---

*Document ID: KSF-GL-CT-001*  
*© 2026 Kloud Sovereign Fabric*