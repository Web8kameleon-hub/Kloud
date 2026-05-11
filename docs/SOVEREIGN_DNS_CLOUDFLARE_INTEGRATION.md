# Sovereign DNS Cloudflare Integration Guide

## Purpose

This guide links the sovereign DNS policy template with practical Cloudflare execution.

It is intended for phased migration where Cloudflare is still used as DNS control while edge logic becomes sovereign.

## Files

- Policy template: `docs/templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json`
- Apply script: `scripts/apply-sovereign-dns-policy-cloudflare.ps1`
- Failover drill: `scripts/test-sovereign-failover.ps1`

## Step 1: Dry Run

Run safe preview first:

```powershell
.\scripts\apply-sovereign-dns-policy-cloudflare.ps1 `
  -ZoneId <ZONE_ID> `
  -ApiToken <CF_API_TOKEN> `
  -DryRun
```

## Step 2: Apply Records

Apply policy to Cloudflare DNS:

```powershell
.\scripts\apply-sovereign-dns-policy-cloudflare.ps1 `
  -ZoneId <ZONE_ID> `
  -ApiToken <CF_API_TOKEN> `
  -Apply
```

Optional: disable unhealthy records during apply:

```powershell
.\scripts\apply-sovereign-dns-policy-cloudflare.ps1 `
  -ZoneId <ZONE_ID> `
  -ApiToken <CF_API_TOKEN> `
  -Apply `
  -DisableUnhealthy
```

## Step 3: Run Failover Drill

```powershell
.\scripts\test-sovereign-failover.ps1
```

This prints:

- PoP health state in policy order
- recommended primary for current conditions

## Notes

1. Cloudflare DNS record-level weighting is represented in comments for traceability; true load balancing behavior may require Cloudflare Load Balancer plan.
2. Keep low TTL during migration windows.
3. After migration, move authoritative DNS out of Cloudflare when ready.
