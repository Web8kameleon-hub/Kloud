# Cloudflare quick run guide (Albanian)

Ky dokument përmbledh hapat e shpejtë për të vendosur konfigurimin minimal urgjent në Cloudflare.

1) Importo zonën
   - Shko tek Cloudflare → DNS → Import dhe ngarko `docs/kloud.cloudflare.zone`.

2) Vendos proxy për rekordet A
   - Bëj proxied (orange cloud) për `@`, `www`, `api`, `agi`.

3) Aktivizo SSL Full (Strict)
   - Settings → SSL/TLS → `Full (Strict)` dhe instaloni Cloudflare Origin Certificate tek serveri origjinë.

4) Aktivizo WAF dhe OWASP rules
   - Security → WAF: Enable, dhe aktivizo OWASP/SQLi/XSS.

5) Ekzekuto skriptin PowerShell (ose përdor UI)

PowerShell (DryRun - test):

```powershell
# Load helper functions
. .\scripts\cloudflare_apply_examples.ps1

# Dry run of all baseline changes
Invoke-CFApplyAll -ZoneId '<ZONE_ID>' -ApiToken '<TOKEN>' -OfficeIp '1.2.3.4/32' -DryRun
```

PowerShell (live):

```powershell
# Run live (removes -DryRun)
Invoke-CFApplyAll -ZoneId '<ZONE_ID>' -ApiToken '<TOKEN>' -OfficeIp '1.2.3.4/32'
```

-Pas aplikimit

- Verifiko që `@`, `www`, `api`, `agi` janë proxied dhe TLS funksionon.
- Verifiko që MX dhe mail.* janë DNS-only.
- Kontrollo Cloudflare Analytics dhe aktivizo Alerts.

***

Nëse dëshiron, unë mund ta propozoj versionin për GitHub Actions (idempotent) që përdor secrets për `CF_ZONE_ID` dhe `CF_API_TOKEN` dhe ekzekuton `Invoke-CFApplyAll` me `-DryRun:false`.

