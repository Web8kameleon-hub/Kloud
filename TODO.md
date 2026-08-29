# TODO - Internal Auth (Email + OTP) Migration & Validation

- [x] Audit and remove Google/Clerk auth references from active web auth flow
- [x] Enforce internal-only auth policy in middleware and auth library
- [ ] Update developer-facing auth documentation text to internal email+OTP only
- [x] Verify/complete internal auth API routes: request-code, verify-code, me, logout
- [ ] Run API auth flow tests (request-code -> verify-code -> me -> logout)
- [ ] Run UI sign-in flow tests (email + OTP) and confirm token/session behavior
- [ ] Summarize changes, test results, and PR readiness

---

# TODO - Monorepo Multilangue / Multipaketa Clarity

- [x] Identify language/package managers and workspace boundaries from root manifests
- [x] Add `docs/MONOREPO_MULTILANG_GUIDE.md` with JS/TS + Rust + Python topology and commands
- [x] Link new multilang guide from `docs/README.md`
- [x] Add server-side `gh` recovery note (gh vs gitsome conflict) in multilang guide
- [ ] Cross-check doc links and command snippets for consistency before PR
