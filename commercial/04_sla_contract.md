# Kloud Sovereign Fabric Suite
## Service Agreement & Service Level Agreement (SLA)
### Master Service Agreement (MSA) Template v1.0 · May 2026

---

> **IMPORTANT:** This document is a template. Before use with any client,  
> review with qualified legal counsel for your jurisdiction.  
> Fill in all `[BRACKETED]` fields before execution.

---

## MASTER SERVICE AGREEMENT

**This Master Service Agreement ("Agreement")** is entered into as of `[DATE]`  
between:

**Service Provider:**  
Kloud Sovereign Fabric ("Kloud")  
`[REGISTERED ENTITY NAME]`  
`[ADDRESS]`  
`[COUNTRY]`  
VAT: `[VAT NUMBER]`  
Email: enterprise@kloud.io

**Customer:**  
`[CUSTOMER LEGAL NAME]`  
`[REGISTERED ADDRESS]`  
`[COUNTRY]`  
VAT: `[CUSTOMER VAT NUMBER]`  
Contact: `[CUSTOMER EMAIL]`  
("Customer")

Together referred to as "the Parties."

---

## PART I — SERVICES

### 1. Scope of Services

1.1 Kloud agrees to provide Customer with access to the **Kloud Sovereign Fabric Suite**, comprising:

- **Service Layer 1 — Sovereign Node Deployment**: Deployment and configuration of sovereign compute nodes on Customer-designated infrastructure.
- **Service Layer 2 — Managed Fabric**: 24/7 monitoring, patch management, incident response, and operational observability.
- **Service Layer 3 — Security Posture Engine**: STIGMA behavioral telemetry and NDB cognitive deviation tracking.
- **Service Layer 4 — API Compute Credits**: Usage-based access to fabric endpoints including `/submit`, `/status`, `/compute`, `/task`, `/events`, and `/metrics`.

1.2 The specific services, tier, pricing, and node count are defined in **Schedule A — Order Form** attached hereto.

1.3 Kloud reserves the right to update, enhance, or modify services with 30 days written notice, provided no material degradation in functionality occurs.

---

### 2. Subscription Tier & Billing

2.1 Customer subscribes to the tier specified in Schedule A:
- **Starter** — €299/month
- **Pro** — €699/month
- **Enterprise** — as quoted in Schedule A

2.2 Billing occurs monthly in advance, or annually as agreed.

2.3 Overage charges apply as follows:
- Starter: €0.0001 per operation above 1M/month
- Pro: €0.00008 per operation above 5M/month
- Enterprise: as defined in Schedule A

2.4 Invoices are due within **14 days** of issuance (Starter/Pro) or **30 days** (Enterprise).

2.5 Late payment incurs a penalty of **1.5% per month** on outstanding amounts.

2.6 All prices are exclusive of VAT. Applicable taxes are Customer's responsibility.

---

### 3. Term

3.1 This Agreement commences on the Effective Date and continues:
- **Month-to-month** for Starter and Pro tiers
- **Minimum 12 months** for Enterprise, auto-renewing annually unless terminated with 90 days notice

3.2 Either party may terminate this Agreement:
- With 30 days written notice (Starter/Pro)
- With 90 days written notice (Enterprise)
- Immediately upon material breach that remains uncured after 14 days written notice

3.3 Upon termination, Customer data export will be available for 30 days. After that, all Customer data will be permanently deleted unless otherwise agreed.

---

## PART II — SERVICE LEVEL AGREEMENT (SLA)

### 4. Uptime Commitment

| Tier       | Monthly Uptime SLA | Maximum Downtime/Month |
| ---------- | ------------------ | ---------------------- |
| Starter    | 99.5%              | ~3.6 hours             |
| Pro        | 99.9%              | ~43 minutes            |
| Enterprise | 99.99%             | ~4.3 minutes           |

4.1 "Uptime" means the fabric node control plane and core API endpoints (`/submit`, `/status`) are accessible and responding within 5 seconds.

4.2 "Downtime" is measured from the time Customer submits a valid incident ticket to the time services are restored.

4.3 Scheduled maintenance windows (max 4 hours/month, with 72h advance notice) are excluded from downtime calculation.

---

### 5. Support Response Times

| Tier       | Severity P1 | Severity P2 | Severity P3 |
| ---------- | ----------- | ----------- | ----------- |
| Starter    | 48h         | 72h         | Best effort |
| Pro        | 12h         | 24h         | 48h         |
| Enterprise | 2h (24/7)   | 4h          | 8h          |

**Severity Definitions:**
- **P1 Critical:** Node completely unreachable, fabric down, data loss risk
- **P2 High:** Major feature degraded, STIGMA not recording, NDB unavailable
- **P3 Medium:** Minor degradation, cosmetic issues, documentation requests

---

### 6. SLA Credits

6.1 If Kloud fails to meet the uptime SLA, Customer is entitled to service credits:

| Uptime Achieved      | Credit (% of monthly fee) |
| -------------------- | ------------------------- |
| 99.0–99.5% (Starter) | 5%                        |
| 98.0–99.0%           | 10%                       |
| 95.0–98.0%           | 20%                       |
| < 95.0%              | 30%                       |

6.2 Credits are applied to the next invoice. Credits are the sole remedy for SLA failures unless otherwise negotiated in Enterprise terms.

6.3 Credit requests must be submitted within 30 days of the incident via enterprise@kloud.io.

---

### 7. Exclusions from SLA

The following are excluded from SLA calculations:

- Force majeure events (natural disasters, war, pandemics)
- Customer-caused outages (misconfiguration, unauthorized changes)
- Third-party infrastructure failures (cloud providers, ISPs)
- Security incidents caused by Customer's negligent credential management
- Scheduled maintenance (notified 72h in advance)
- Beta/experimental features explicitly labelled as such

---

## PART III — DATA & SECURITY

### 8. Data Sovereignty

8.1 **Customer Data Ownership:** All data processed through Customer's sovereign nodes is owned exclusively by Customer.

8.2 **No Data Access by Kloud:** Kloud does not have access to Customer node data, telemetry payloads, or CRDT state contents unless Customer explicitly grants temporary access for support purposes.

8.3 **Data Location:** Customer data resides on infrastructure designated by Customer. Kloud does not transfer Customer data to third-party servers without explicit written consent.

8.4 **CRDT State:** All CRDT state entries, event logs, and STIGMA traces are stored locally on Customer's node. Kloud retains no copies.

---

### 9. Security Obligations

9.1 **Kloud obligations:**
- Maintain the fabric software with security patches within 14 days of critical CVE disclosure
- Use encrypted channels (TLS 1.3+) for all API communications
- Never store Customer API keys or credentials in plaintext
- Conduct security reviews before major version releases

9.2 **Customer obligations:**
- Protect API keys and node access credentials
- Not share access with unauthorized parties
- Report suspected security incidents to security@kloud.io within 24 hours of discovery
- Maintain their underlying infrastructure security

---

### 10. GDPR & Data Protection

10.1 Each party is independently responsible for GDPR compliance regarding data under their control.

10.2 Kloud acts as **Data Processor** only for any personal data Customer chooses to process through the fabric. Customer is the **Data Controller**.

10.3 A Data Processing Agreement (DPA) is available on request and is mandatory for Enterprise clients processing EU personal data.

10.4 Kloud maintains the following for GDPR compliance:
- Right to erasure: Customer data deleted within 30 days of termination
- Data portability: Full export available in JSON/CSV at any time
- Audit log: All access events logged in STIGMA telemetry

---

## PART IV — INTELLECTUAL PROPERTY

### 11. Proprietary Technology

11.1 The following components of the Kloud platform are proprietary and protected:
- NDB (Node Deviation Baseline) scoring algorithm
- STIGMA behavioral telemetry classification system
- TIDE fabric tension monitoring architecture
- CRDT state store implementation
- Kloud Control Surface interface
- All associated software, algorithms, and documentation

11.2 Customer receives a limited, non-exclusive, non-transferable license to use the Kloud platform as provided under this Agreement.

11.3 Customer may not: reverse engineer, decompile, copy, sublicense, or create derivative works based on Kloud's proprietary technology.

---

### 12. Customer Data License

12.1 Customer grants Kloud a limited license to process Customer data solely for the purpose of delivering the services described herein.

12.2 Kloud may use **anonymized, aggregated** metrics (never containing Customer identifiers) to improve platform performance.

---

## PART V — LIABILITY & WARRANTIES

### 13. Warranties

13.1 Kloud warrants that:
- The platform will function materially as described in the documentation
- Security measures will be maintained as described in Section 9
- Kloud has the right to provide the services

13.2 **DISCLAIMER:** Except as expressly stated, services are provided "AS IS." Kloud disclaims all implied warranties of merchantability and fitness for a particular purpose.

---

### 14. Limitation of Liability

14.1 **Neither party shall be liable** for indirect, incidental, special, or consequential damages.

14.2 **Kloud's total liability** to Customer for any claim arising under this Agreement shall not exceed **6 months of fees paid** by Customer in the preceding 12 months.

14.3 This limitation does not apply to:
- Gross negligence or willful misconduct
- Breaches of Section 8 (Data Sovereignty)
- Death or personal injury caused by negligence

---

### 15. Indemnification

15.1 Each party shall indemnify the other against third-party claims arising from their own gross negligence or willful breach of this Agreement.

15.2 Kloud shall defend Customer against third-party IP infringement claims related to using the Kloud platform as intended.

---

## PART VI — GENERAL PROVISIONS

### 16. Confidentiality

16.1 Each party agrees to keep the other's Confidential Information (including pricing, technical specs, and business plans) strictly confidential.

16.2 Confidential Information may only be disclosed to employees or contractors on a need-to-know basis, bound by equivalent confidentiality obligations.

16.3 This obligation survives termination for **3 years**.

---

### 17. Governing Law & Dispute Resolution

17.1 This Agreement is governed by the laws of `[GOVERNING JURISDICTION — e.g., Albania, Germany, Switzerland]`.

17.2 Disputes shall first be addressed through good-faith negotiation. If unresolved within 30 days, disputes shall be subject to binding arbitration under `[ARBITRATION BODY]` rules.

17.3 Courts of `[JURISDICTION]` shall have exclusive jurisdiction for enforcement of arbitral awards.

---

### 18. Amendments & Notices

18.1 Amendments require written consent of both parties.

18.2 Notices must be sent to the email addresses specified in this Agreement and are effective when delivered.

18.3 Kloud may update standard service terms with 30 days notice via email.

---

### 19. Entire Agreement

This Agreement (including all Schedules) constitutes the entire agreement between the parties and supersedes all prior negotiations, representations, or agreements.

---

## SCHEDULE A — ORDER FORM

```
Customer:         [CUSTOMER NAME]
Effective Date:   [DATE]
Tier:             [ ] Starter  [ ] Pro  [ ] Enterprise
Monthly Fee:      €[AMOUNT]
Billing Cycle:    [ ] Monthly  [ ] Annual
Nodes:            [NUMBER]
API Ops/month:    [NUMBER]
Infrastructure:   [WHERE NODES WILL BE DEPLOYED]
Special Terms:    [ANY CUSTOM TERMS]

Service Start:    [DATE]
```

---

## SCHEDULE B — CONTACT PERSONS

```
Kloud Primary Contact:     enterprise@kloud.io
Kloud Technical Contact:   support@kloud.io
Kloud Security Contact:    security@kloud.io

Customer Primary Contact:  [NAME / EMAIL]
Customer Technical Contact:[NAME / EMAIL]
Customer Billing Contact:  [NAME / EMAIL]
```

---

## SIGNATURES

```
FOR KLOUD SOVEREIGN FABRIC:          FOR CUSTOMER:

Name:  ___________________________   Name:  ___________________________
Title: ___________________________   Title: ___________________________
Date:  ___________________________   Date:  ___________________________
Sig:   ___________________________   Sig:   ___________________________
```

---

*Document version: 1.0 · May 2026 · Kloud Sovereign Fabric*  
*Template for legal review. Not a substitute for qualified legal counsel.*  
*© 2026 Kloud · All rights reserved*
