# Sovereign Edge Production Checklist

## Pre-Production

- [ ] control-plane health is stable
- [ ] sync-loop running with expected interval
- [ ] scan-print count clean and deduplicated
- [ ] PoP 1, PoP 2, PoP 3 reachable
- [ ] TLS valid on all public ingress points
- [ ] resonant status endpoint healthy on each PoP

## Security

- [ ] write endpoints protected by policy and rate limit
- [ ] replay protection enabled
- [ ] key rotation procedure verified
- [ ] admin endpoints restricted

## Data Integrity

- [ ] adaptive write accepted on primary PoP
- [ ] state key growth verified
- [ ] chain integrity failures equal zero
- [ ] replay rejection metrics monitored

## Routing and DNS

- [ ] authoritative DNS policy prepared
- [ ] low TTL configured for rollout window
- [ ] weighted or latency routing enabled
- [ ] failover order tested

## Failure Drills

- [ ] PoP 1 outage drill passed
- [ ] PoP 2 outage drill passed
- [ ] PoP 3 recovery drill passed
- [ ] rollback to primary-only mode tested

## Promotion Gate

- [ ] p95 latency acceptable
- [ ] write error rate below threshold
- [ ] no unresolved incidents in last 24h
- [ ] operations handoff completed
