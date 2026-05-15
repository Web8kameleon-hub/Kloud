# Kloud Sovereign Fabric Suite
## Revenue Model & Financial Projections
### Internal Strategic Document · Version 1.0 · May 2026

---

## SECTION 1 — REVENUE STREAMS

### Primary Revenue (Recurring Subscription)

| Stream                | Model           | Tier       | Price               |
| --------------------- | --------------- | ---------- | ------------------- |
| Sovereign Node Bundle | Monthly/Annual  | Starter    | €299/month          |
| Sovereign Node Bundle | Monthly/Annual  | Pro        | €699/month          |
| Sovereign Node Bundle | Annual contract | Enterprise | €1,499–€4,999/month |

### Secondary Revenue (Variable)

| Stream                  | Model          | Rate        |
| ----------------------- | -------------- | ----------- |
| API Overage (Starter)   | Per operation  | €0.0001/op  |
| API Overage (Pro)       | Per operation  | €0.00008/op |
| Extra Nodes (add-on)    | Per node/month | €149/node   |
| Security Posture Plus   | Monthly add-on | €99/month   |
| STIGMA SIEM Integration | Monthly add-on | €149/month  |
| Grafana Advanced        | Monthly add-on | €49/month   |
| Extra API Credits (10M) | Pack           | €79/pack    |

### One-Time Revenue (Professional Services)

| Service                 | Range          |
| ----------------------- | -------------- |
| Custom Deployment       | €2,500–€5,000  |
| Migration & Integration | €3,500–€8,000  |
| Enterprise Setup        | €5,000–€15,000 |
| Training & Enablement   | €1,500/session |
| Security Audit          | €3,000–€7,500  |

---

## SECTION 2 — UNIT ECONOMICS

### Customer Acquisition Cost (CAC)

| Channel                    | Estimated CAC |
| -------------------------- | ------------- |
| Direct outreach (LinkedIn) | €200–€400     |
| Partner referral           | €150–€300     |
| SEO / inbound              | €100–€250     |
| Conference / events        | €500–€1,200   |
| **Target blended CAC**     | **< €600**    |

### Average Revenue Per User (ARPU)

| Scenario                         | Calculation                  | ARPU/month      |
| -------------------------------- | ---------------------------- | --------------- |
| Starter only                     | €299 base                    | €299            |
| Starter + add-ons                | €299 + €99 + €49             | €447            |
| Pro only                         | €699 base                    | €699            |
| Pro + add-ons                    | €699 + €149 + €99 + €79      | €1,026          |
| Enterprise (low)                 | €1,499 base                  | €1,499          |
| Enterprise (mid)                 | €2,999 + pro services amort. | €3,600          |
| Enterprise (high)                | €4,999 + add-ons             | €5,800          |
| **Blended ARPU target (Year 1)** | Mix of tiers                 | **€900–€1,200** |

### Lifetime Value (LTV)

Assumptions: average churn 8% annually, average tenure 2.5 years

| Tier       | ARPU/month | Avg Tenure | LTV      | LTV/CAC |
| ---------- | ---------- | ---------- | -------- | ------- |
| Starter    | €399       | 18 months  | €7,182   | 12x     |
| Pro        | €900       | 28 months  | €25,200  | 42x     |
| Enterprise | €3,000     | 36 months  | €108,000 | 180x+   |

### Gross Margin

| Component           | % of Revenue |
| ------------------- | ------------ |
| Infrastructure cost | 8–12%        |
| Engineering (ops)   | 5–8%         |
| Support             | 4–6%         |
| **Gross Margin**    | **74–83%**   |

---

## SECTION 3 — GROWTH SCENARIOS

### Base Case — Conservative

| Month | New Clients | Total Clients | MRR     | ARR (annualized) |
| ----- | ----------- | ------------- | ------- | ---------------- |
| M1    | 1           | 1             | €699    | €8,388           |
| M2    | 2           | 3             | €2,097  | €25,164          |
| M3    | 2           | 5             | €3,495  | €41,940          |
| M4    | 3           | 8             | €7,192  | €86,304          |
| M5    | 3           | 11            | €9,900  | €118,800         |
| M6    | 4           | 15            | €13,485 | €161,820         |
| M9    | 5           | 30            | €30,000 | €360,000         |
| M12   | 5           | 50            | €52,500 | **€630,000**     |

*Assumptions: avg ARPU €1,050, 3% monthly churn*

---

### Mid Case — Target

| Month | New Clients | Total Clients | MRR      | ARR (annualized) |
| ----- | ----------- | ------------- | -------- | ---------------- |
| M3    | 5           | 10            | €9,000   | €108,000         |
| M6    | 8           | 30            | €31,500  | €378,000         |
| M9    | 10          | 55            | €68,750  | €825,000         |
| M12   | 10          | 80            | €112,000 | **€1,344,000**   |
| M18   | 12          | 150           | €225,000 | **€2,700,000**   |

*Assumptions: avg ARPU €1,400, active sales motion, partner referrals*

---

### Upside Case — With Seed Investment

| Month | New Clients | Total Clients | MRR      | ARR             |
| ----- | ----------- | ------------- | -------- | --------------- |
| M6    | 15          | 50            | €62,500  | €750,000        |
| M12   | 20          | 150           | €225,000 | €2,700,000      |
| M18   | 25          | 280           | €504,000 | **€6,048,000**  |
| M24   | 30          | 450           | €900,000 | **€10,800,000** |

*Assumptions: funded sales team, EU enterprise push, government contracts*

---

## SECTION 4 — CLIENT MIX STRATEGY

### Year 1 Target Mix

| Tier       | Target Clients | % of ARR |
| ---------- | -------------- | -------- |
| Starter    | 25             | 12%      |
| Pro        | 20             | 28%      |
| Enterprise | 5              | 60%      |
| **Total**  | **50**         | 100%     |

**Key insight:** 5 Enterprise clients generate more ARR than 45 Starter/Pro clients combined.  
→ Enterprise sales should be the primary focus from month 3 onward.

---

## SECTION 5 — COST STRUCTURE

### Operating Costs (Bootstrap Phase — no full-time hires)

| Cost Item                | Monthly    | Annual      |
| ------------------------ | ---------- | ----------- |
| Infrastructure (Hetzner) | €300       | €3,600      |
| Domain + SSL + CDN       | €50        | €600        |
| Software licenses        | €100       | €1,200      |
| Accounting / legal       | €200       | €2,400      |
| Marketing (ads/tools)    | €500       | €6,000      |
| Misc (comms, tools)      | €150       | €1,800      |
| **Total Bootstrap Burn** | **€1,300** | **€15,600** |

### Break-Even Analysis

At €1,300/month burn:
- **Break-even:** 5 Starter clients OR 2 Pro clients OR 1 Enterprise client
- **This is achievable in Month 1–2**

---

### Funded Phase Costs (Post-Seed, €300k–€750k)

| Cost Item               | Monthly     | Annual       |
| ----------------------- | ----------- | ------------ |
| Engineering (2 FTEs)    | €8,000      | €96,000      |
| Sales (1 FTE)           | €4,500      | €54,000      |
| Marketing               | €3,000      | €36,000      |
| Infrastructure (scaled) | €2,000      | €24,000      |
| Legal / compliance      | €1,500      | €18,000      |
| Operations              | €1,000      | €12,000      |
| **Total Funded Burn**   | **€20,000** | **€240,000** |

Break-even at €20,000 burn → ~19 Pro clients or 5–8 Enterprise clients.

---

## SECTION 6 — PRICING SENSITIVITY ANALYSIS

### What happens if we drop prices by 20%?

| Scenario            | Impact on MRR (50 clients) |
| ------------------- | -------------------------- |
| Starter: €239/month | -€1,500 MRR (-7%)          |
| Pro: €559/month     | -€2,800 MRR (-14%)         |
| Enterprise: €1,199  | -€1,500 MRR (-8%)          |
| **Total impact**    | **-€5,800 MRR (-29%)**     |

→ A 20% price drop requires 40% more clients to maintain same MRR.  
→ **Recommendation: hold pricing. Compete on value, not price.**

### What if we raise prices by 20%?

A 20% price raise with 10% client churn still results in:
- Net MRR change: +8–14%
- Signals premium positioning
- **Justified by STIGMA/NDB uniqueness**

---

## SECTION 7 — KEY METRICS TO TRACK

| Metric             | Target (Month 12) |
| ------------------ | ----------------- |
| MRR                | €50,000+          |
| ARR                | €600,000+         |
| Total clients      | 50+               |
| Enterprise clients | 5+                |
| Churn rate         | < 5%/month        |
| LTV/CAC            | > 12x             |
| Gross margin       | > 78%             |
| NPS (Net Promoter) | > 40              |
| Time-to-value      | < 30 minutes      |

---

## SECTION 8 — FUNDING ALLOCATION

### Seed Round: €300k–€750k

| Use                        | % Allocation | €300k Raise | €750k Raise |
| -------------------------- | ------------ | ----------- | ----------- |
| Engineering (2 FTEs, 12mo) | 45%          | €135,000    | €337,500    |
| Sales & Marketing          | 25%          | €75,000     | €187,500    |
| Infrastructure             | 15%          | €45,000     | €112,500    |
| Legal & Compliance         | 10%          | €30,000     | €75,000     |
| Operations                 | 5%           | €15,000     | €37,500     |

### Expected outcomes from €300k raise:
- 2 engineers hired (Full-Stack + DevOps)
- 50+ clients by Month 12
- €630k ARR
- Series A ready at Month 18–24

### Expected outcomes from €750k raise:
- 3 engineers + 1 sales hire
- 150+ clients by Month 18
- €2.7M ARR
- Strong Series A position at Month 24

---

*Document version: 1.0 · May 2026 · Kloud Sovereign Fabric*  
*Confidential — Internal use only*  
*© 2026 Kloud · All rights reserved*
