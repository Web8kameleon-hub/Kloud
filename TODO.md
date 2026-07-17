# TODO - Internal Auth (Email + OTP) Migration & Validation

- [x] Audit and remove Google/Clerk auth references from active web auth flow
- [x] Enforce internal-only auth policy in middleware and auth library
- [ ] Update developer-facing auth documentation text to internal email+OTP only
- [x] Verify/complete internal auth API routes: request-code, verify-code, me, logout
- [ ] Run API auth flow tests (request-code -> verify-code -> me -> logout)
- [ ] Run UI sign-in flow tests (email + OTP) and confirm token/session behavior
- [ ] Summarize changes, test results, and PR readiness
