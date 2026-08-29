# docs/legal — RESTRICTED (Confidential / Trade Secret)

Status: **RESTRICTED — Internal counsel & founders only**
Owner: Ledjan Ahmati / WEB8euroweb GmbH
Contact: clisonix@pm.me

## Purpose
This folder holds trade-secret baselines, invention disclosures, and patent-preparation
material for WWWMMM / XLC / NDB / Stigma. Contents are **not** for public release and
**must not** be mirrored into customer-facing docs, marketing, or public repositories.

## Access Rules
- Least-privilege: access limited to founders and engaged legal counsel.
- No copy/paste of internal formulas, tuning constants, or scoring matrices into:
  - public READMEs, SDK docs, blog posts, landing pages, issue trackers, or PRs.
- Any external disclosure requires written approval from the owner.

## What lives here (restricted)
| File | Purpose |
|------|---------|
| `WWWMMM_IP_MEMO.md` | Trade-secret posture baseline (quarterly update). |
| `INVENTION_DISCLOSURE_WWWMMM.md` | Counsel-ready disclosure package (measured vs proposed). |

## What must NOT live here
- Customer integration guides → `docs/public/`.
- Security-OS product designs (honeypot/eBPF/nanogrid) → separate product folder,
  never mixed into the trade-secret memo.

## Publication boundary (mirror of IP memo §6)
Allowed externally: high-level capability language, reliability outcomes, public API
contract behavior.
Restricted externally: internal resonance formulas, matrix/threshold calibration,
attack/defense tuning specifics, non-required source-level detail.

## Evidence hygiene
- Timestamp architecture decisions and benchmark outputs.
- Keep immutable changelogs for algorithm revisions.
- Track first public disclosures; avoid accidental over-disclosure.

> This folder is confidential. If you received it in error, delete it and notify the owner.
