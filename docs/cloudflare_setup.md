
# Cloudflare minimal urgent configuration (Import + hardening)

Përmbledhje e shkurtër:

- Përdor Cloudflare për të filtruar trafikun malicioz para origjinës (edge).
- Aktivizo proxy (orange cloud) për A records të publikuara (web, api) dhe vendos SSL: Full (Strict) nëse përdor certifikata origin ose Cloudflare Origin Certificate.

Hapat urgjentë (minimal):

1) Importo zonën

   - Shko në Cloudflare → DNS → Import dhe ngarko `docs/kloud.cloudflare.zone`.

2) Proxy A records kritike

   - Bëj proxied (orange cloud) për `@`, `www`, `api`, `agi` — kjo vendos filtrin edge.

3) SSL/TLS

   - Settings → SSL/TLS → Mode: `Full (Strict)`.

   - Në server origjinë instaloni Cloudflare Origin Certificate (rekomanduar) ose një certifikatë valide publike.

4) WAF

   - Security → WAF: Enable.

   - Aktivizo rregullat e OWASP, SQLi, XSS.

5) Firewall Rules (shembuj)

   - Admin lock (bllokon rrugët /admin përveç IP-ve të zyrës):

     - Expression: `(http.request.uri.path contains "/admin") and not ip.src in {YOUR_OFFICE_IPS}`

     - Action: `Block`

   - API protection (sfidë për rrezik të lartë):

     - Expression: `http.request.uri.path starts_with "/api/" and cf.threat_score > 10`

     - Action: `Challenge`

   - Block bad referrers:

     - Expression: `http.referer contains "badsite.com"`

     - Action: `Block`

6) Rate limiting (shembuj):

   - `/api/ask` → 10 req / 10s per IP → Action: `Block` ose `Challenge` për 60s.

   - Upload endpoints (EEG/audio) → 1 req / 30s per IP → Action: `Challenge`.

7) Under Attack Mode

   - Security → Overview → `Under Attack` (UI) — aktivizo për një valë të akute.

   - Mund ta vendosësh me API (shiko script-in PowerShell më poshtë).

8) Bot Management / JavaScript Challenge

   - Nëse ke Pro/Enterprise, aktivizo Bot Management dhe JavaScript Challenge për trafikun e dyshimtë.

9) Page Rules (shembuj)

   - `api.kloud.com/*` → Cache Level: `Bypass`, Security: `High`.

   - `kloud.com/*` → Cache Everything (opsionale), Edge Cache TTL si dëshiron.

10) DNS nameservers

- Pasi importoni zonën tek Cloudflare, përditësoni nameserver-at tek registrar (jean/justin) për të shkruar Cloudflare nameservers.

11)-Monitoring

- Enable Alerts (email + Slack) për spikes dhe sulme nga Cloudflare Analytics.

API Examples (replace `ZONE_ID` and `CF_API_TOKEN`):

Turn on "I'm under attack":

```bash
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/settings/security_level" \
 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
 -H "Content-Type: application/json" \
 --data '{"value":"under_attack"}'
```

Create Firewall Rule (admin lock):

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/firewall/rules" \
 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
 -H "Content-Type: application/json" \
 --data '[{
   "action":"block",
   "filter":{"expression":"(http.request.uri.path contains \"/admin\") and not ip.src in {1.2.3.4/32}","paused":false,"description":"Block admin except office"},
   "description":"Block admin paths from non-office IPs"
 } ]'
```

Create Rate Limit (example for /api/ask):

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/rate_limits" \
 -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
 -H "Content-Type: application/json" \
 --data '{
   "threshold": 10,
   "period": 10,
   "action": {"mode": "block", "timeout": 60},
   "match": {"request": {"methods": ["POST"], "schemes": ["HTTP","HTTPS"], "url": "https://api.kloud.com/api/ask*"}},
   "enabled": true,
   "description": "Protect /api/ask"
 }'
```

Shënim: Zëvendëso `<ZONE_ID>` dhe `$CLOUDFLARE_API_TOKEN` me vlerat e tua. Unë mund të prodhoj një template për të krijuar tokenin me privilegjet e duhura.

----
Small checklist for immediate run:

- Import zone
- Proxy A records for `@`, `www`, `api`, `agi`
- Set SSL/TLS: Full (Strict) + install origin cert
- Enable WAF + OWASP rules
- Add firewall rules + rate-limits shown above
- Monitor and enable Under Attack if needed

