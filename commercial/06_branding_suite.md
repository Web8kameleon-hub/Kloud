# Kloud Sovereign Fabric Suite
## Brand Identity & Style Guide
### Version 1.0 · May 2026

---

## 1. BRAND ESSENCE

### Mission
> To give every organization total control over their compute, intelligence, and security — without compromise.

### Vision
> A world where sovereign infrastructure is the default, not the exception.

### Brand Personality
- **Precise** — we speak in facts, data, and measurable outcomes
- **Sovereign** — self-sufficient, uncompromising, independent
- **Technical authority** — we earn trust through depth, not hype
- **Austere** — no unnecessary ornamentation; everything serves a purpose
- **Calm confidence** — we don't shout; the results speak

### Taglines

**Primary:**
> "Sovereign by Design."

**Secondary variants:**
> "Deploy. Observe. Secure. Scale."  
> "Your infrastructure. Your rules."  
> "The intelligence layer for the post-cloud era."  
> "Zero trust. Zero compromise. Full sovereignty."  
> "Where fabric meets cognition."

---

## 2. NAMING CONVENTIONS

### Product Name
**Kloud** — always with capital K, never "cloud" with a lowercase k in product context.

### Suite Name
**Kloud Sovereign Fabric Suite** — full name in formal documents.  
**Kloud Fabric** — shortened in casual/marketing contexts.  
**KSF** — internal abbreviation only.

### Module Names

| Internal Name | Display Name              | Never Say          |
| ------------- | ------------------------- | ------------------ |
| Layer 01      | Sovereign Node Deployment | "hosting"          |
| Layer 02      | Managed Fabric            | "managed services" |
| Layer 03      | Security Posture Engine   | "monitoring"       |
| NDB           | Deviation Amplitude Score | "anomaly detector" |
| STIGMA        | Behavioral Trace Index    | "logging system"   |
| TIDE          | Fabric Tension Monitor    | "load meter"       |
| CRDT          | Distributed State Store   | "database"         |

### Engine Names (internal, preserved as proprietary IP)
- **ALBI** — preserved
- **ALBA** — preserved
- **JONA** — preserved
- **Ocean** — preserved
- **ASI** — preserved
- **CLX / CLX.I** — preserved
- **NDB / STIGMA** — preserved
- **Curiosity Ocean** — preserved

These names are never simplified or replaced in documentation or marketing.

### Enterprise Mapping (official)

| Proprietary Term | Enterprise Term                  | Definition                                                       |
| ---------------- | -------------------------------- | ---------------------------------------------------------------- |
| STIGMA           | Behavioral Trace Index (BTI)     | Behavioral fingerprint of each operation in the fabric           |
| NDB              | Deviation Amplitude Score (DAS)  | Scalar deviation from expected baseline behavior                 |
| Rezonance        | Propagation Field Dynamics (PFD) | How deviation propagates across nodes and changes fabric tension |

Use the proprietary term first in product context, then the enterprise alias in parentheses.
Example: `STIGMA (Behavioral Trace Index)`.

---

## 3. VISUAL IDENTITY

### Color Palette

```
Primary Background:  #090E1A  (Deep Navy — "Sovereign Dark")
Surface:             #10182B  (Panel background)
Surface 2:           #16213A  (Card background)
Accent Blue:         #3B82F6  (Primary action, links, highlights)
Accent Indigo:       #6366F1  (Secondary accent, badges)
Success Green:       #10B981  (Stable, accepted, healthy)
Warning Amber:       #F59E0B  (Caution, medium TIDE)
Error Red:           #EF4444  (Error, breach, anomaly)
Text Primary:        #E2E8F0  (Main text)
Text Muted:          #64748B  (Secondary text, labels)
Border:              #1E2D4A  (Card/panel borders)
```

### Color Usage Rules
- **Blue (#3B82F6)** → primary actions, CTAs, node identity
- **Green (#10B981)** → STABLE status, accepted operations, healthy metrics
- **Amber (#F59E0B)** → caution states, medium severity
- **Red (#EF4444)** → anomalies, L3 BTI events, errors
- **Indigo (#6366F1)** → BTI badges, secondary UI elements

### Dark Mode First
Kloud is always presented in dark mode. Light mode is not supported in the core product UI.

---

## 4. TYPOGRAPHY

### Font Stack
```css
font-family: 'Inter', system-ui, -apple-system, sans-serif;
```

### Code / Telemetry Data
```css
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

### Type Scale
| Usage          | Size     | Weight |
| -------------- | -------- | ------ |
| Hero H1        | 3.5rem   | 800    |
| Section H2     | 2.2rem   | 700    |
| Card H3        | 1.1rem   | 700    |
| Body           | 1rem     | 400    |
| Small/Muted    | 0.875rem | 400    |
| Labels/Badges  | 0.75rem  | 600    |
| Monospace data | 0.875rem | 400    |

### Gradient Text (Hero headings only)
```css
background: linear-gradient(135deg, #E2E8F0 30%, #3B82F6 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
```

---

## 5. UI COMPONENT STANDARDS

### Status Indicators
```
● STABLE     → green dot + text
● CAUTION    → amber dot + text
● ANOMALY    → red dot + text (pulsing animation)
● OFFLINE    → muted gray dot + text
```

### BTI Badges (STIGMA levels)
```
L1 MINIMAL  → indigo bg, indigo text
L2 STANDARD → blue bg, blue text
L3 COMPACT  → amber bg, amber text (or red if escalated)
```

### Metric Cards (Control Surface)
- Dark surface background
- Single metric value (large, colored)
- Label below in muted text
- Thin colored top border by category:
  - Node: blue
  - Security: indigo  
  - Performance: green
  - State: amber

### Buttons
```
Primary: bg #3B82F6, white text, 10px radius, box-shadow glow
Outline: border #1E2D4A, text #E2E8F0, hover border → accent
Danger:  bg #EF4444, white text (confirmation dialogs only)
```

---

## 6. TONE OF VOICE

### Writing Principles

**1. Precise over vague**
- ❌ "advanced AI security features"
- ✅ "STIGMA (BTI) classifies every API request as L1, L2, or L3"

**2. Data-led**
- ❌ "industry-leading performance"
- ✅ "16ms latency — 6.4% of nominal band"

**3. Sovereign confidence (no hype)**
- ❌ "revolutionary game-changing disruptive platform"
- ✅ "a distributed runtime you control entirely"

**4. Technical depth without gatekeeping**
- Write for a CTO who respects precision, but also for a CFO who needs clarity
- Offer depth gradually: headline → sub-description → technical detail

**5. Short sentences. Active voice.**
- ❌ "The platform has been designed to be capable of processing..."
- ✅ "The fabric processes operations in real time."

---

## 7. MESSAGING FRAMEWORK

### For CTOs / Technical Buyers
> "Kloud gives you a distributed runtime with CRDT state, NDB (DAS) deviation tracking, and STIGMA (BTI) behavioral tracing — all running on your own infrastructure, under your control."

### For CISOs / Security Buyers
> "Every API request is classified, scored, and logged before execution. STIGMA (BTI) and NDB (DAS) expose behavioral risk signals with real-time propagation visibility through PFD."

### For CFOs / Business Buyers
> "One subscription. Four service layers. Predictable costs. No cloud lock-in. No hidden fees."

### For Investors
> "Kloud is the sovereign intelligence layer for the post-cloud era — a defensible, deep-tech platform with unique IP (STIGMA/BTI + NDB/DAS + PFD) operating in a €126B+ addressable market."

### For Developer Audiences
> "Deploy a sovereign node in 30 minutes. Submit operations via REST. Track BTI traces, DAS deviation, and PFD propagation in real time. Full CRDT state store."

---

## 8. WHAT WE ARE NOT

To maintain brand clarity, never position Kloud as:

| Don't say we are...     | Say instead...                               |
| ----------------------- | -------------------------------------------- |
| A CDN                   | A sovereign intelligence fabric              |
| A hosting provider      | A sovereign compute fabric                   |
| A monitoring tool       | A behavioral telemetry + security engine     |
| An AI chatbot           | A cognitive fabric runtime                   |
| "Like [other platform]" | A category-defining sovereign fabric runtime |
| "Just observability"    | Behavioral integrity + runtime control       |

---

## 9. SOCIAL MEDIA PROFILES

### LinkedIn
> **Kloud Sovereign Fabric** · Infrastructure · Distributed Systems · Zero-Trust AI  
> "The autonomous intelligence layer for modern infrastructure. Deploy. Observe. Secure. Scale."  
> URL: kloud.io | enterprise@kloud.io

### Twitter/X
> @KloudFabric  
> "Sovereign compute. Behavioral security. Distributed intelligence. NDB + STIGMA. #ZeroTrust #DistributedSystems #SovereignAI"

### GitHub
> Organization: Web8kameleon-hub  
> Bio: "Kloud Sovereign Fabric — Rust + Python + Go sovereign compute runtime with NDB/STIGMA security telemetry."

---

## 10. EMAIL SIGNATURE TEMPLATE

```
[NAME]
[TITLE] · Kloud Sovereign Fabric
────────────────────────────────
enterprise@kloud.io
kloud.io

Node #1 · STIGMA STABLE · NDB 0.041
"Sovereign by Design."
```

---

*Document version: 1.0 · May 2026 · Kloud Sovereign Fabric*  
*Internal use — branding guidelines for all team members and contractors*  
*© 2026 Kloud · All rights reserved*
