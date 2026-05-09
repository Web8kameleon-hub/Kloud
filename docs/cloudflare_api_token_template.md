# Cloudflare API token template

When creating a scoped API token for the helper scripts and automated tasks, use the Minimum Privilege principle.

Recommended token permissions (Scope: Zone -> select the kloud.com zone):

- Zone:Zone - Read
- Zone:DNS - Edit (if you want the script to modify DNS records)
- Zone:Settings - Edit (for security_level changes)
- Zone:Firewall Services - Edit (for firewall rules)
- Zone:Rate Limits - Edit (for rate limits)

If you manage multiple zones in one token, consider using Account-level tokens cautiously.

Token name: Kloud-cloudflare-automation
Expiry: 90 days (rotate regularly)

Example usage in PowerShell:

```powershell
$ZoneId = '<ZONE_ID>'
$ApiToken = '<TOKEN>'
. .\scripts\cloudflare_apply_examples.ps1 -ZoneId $ZoneId -ApiToken $ApiToken -DryRun
```

Store the token in a secret manager (GitHub Secrets, Azure Key Vault, etc.) and never commit it to source.

