# 3 PoP Sovereign Edge Architecture

## Purpose

This document defines the minimal sovereign edge layout for Kloud when you want an independent Cloudflare-like control surface without depending on a single external edge provider.

The goal is not to clone Cloudflare feature-for-feature. The goal is to build a small, deterministic, low-power edge fabric with:

- independent authoritative DNS
- three distributed edge points of presence (PoPs)
- health-based routing and failover
- compatibility with Resonant Core, NDB, Tide, and Stigma
- backward-compatible REST/JSON APIs

## What You Already Have

You already have the core control pieces:

- Kloud control plane
- Resonant Core contract
- Nanogrid / sovereign node runtime
- status, security, and telemetry endpoints
- edge-capable Nginx/HTTP ingress
- CRDT and sync-loop behavior

That means the missing part is not the application logic. The missing part is the independent edge topology and routing layer.

## Target Topology

### PoP 1: Primary Edge

- Location: Germany or the current main datacenter
- Role: primary ingress, default DNS target, health source of truth
- Responsibilities:
  - terminate TLS
  - proxy public traffic to Kloud services
  - expose public status and resonant APIs
  - emit edge health telemetry

### PoP 2: Secondary Edge

- Location: nearby EU region
- Role: failover and traffic overflow
- Responsibilities:
  - mirror the same public routes
  - receive traffic when PoP 1 degrades
  - participate in sync-loop and route health checks

### PoP 3: Recovery / Remote Edge

- Location: separate fault domain, preferably different provider or region
- Role: recovery path and geographic fallback
- Responsibilities:
  - remain idle under normal load
  - take over when the first two PoPs are degraded or unreachable
  - preserve service continuity under partial outage

## Functional Layers

### 1. Authoritative DNS Layer

This layer must be independent from the current CDN dependency.

Recommended options:

- PowerDNS for full control and GeoDNS support
- CoreDNS if you want a smaller control surface
- NSD + Unbound if you want a minimal authoritative/resolver split

Required capabilities:

- A/AAAA records for each PoP
- weighted or latency-based routing
- health-aware failover targets
- low TTL for fast switchover

### 2. Edge Proxy Layer

Each PoP runs the same proxy contract:

- Nginx or Envoy
- TLS termination
- request normalization
- route protection for `/api/`, `/status`, `/security/`, and resonant endpoints
- forwarding to local or remote runtime targets

### 3. Control Plane Layer

Kloud remains the control plane:

- identity issuance
- policy distribution
- route maps
- node health rollup
- tide-aware routing decisions
- failover selection

### 4. Data Plane Layer

Nanogrid remains the data plane:

- peer liveness
- mesh gossip
- replication
- replay-safe trace transport
- local recovery

## Routing Rules

Use these rules as the default routing policy:

1. Route to PoP 1 when it is healthy and latency is acceptable.
2. Route to PoP 2 when PoP 1 is degraded or latency rises beyond threshold.
3. Route to PoP 3 when the first two PoPs are down or quarantined.
4. Never route writes to a PoP that is not passing health checks.
5. Keep reads possible from the nearest healthy PoP when policy allows it.

## Health Signals

Each PoP should expose:

- `/health`
- `/status`
- `/api/v1/resonant/status`
- `/api/v1/resonant/events`
- `/api/v1/control-plane/sync-loop/status`

The routing layer should consider:

- `active_peers`
- `avg_latency_ms`
- `load`
- `tide`
- `ndb_score`
- `high_risk`
- `security_posture`
- `state_keys`

## Security Baseline

The sovereign edge should keep the following controls on all PoPs:

- TLS 1.3 everywhere
- per-node identity and trust anchor
- signed write paths
- replay protection for event writes
- rate limiting on public write endpoints
- IP and route restrictions for admin/control endpoints

## Operational Modes

### Normal Mode

- PoP 1 serves most traffic.
- PoP 2 mirrors readiness.
- PoP 3 stays on standby.

### Degraded Mode

- PoP 1 falls out of rotation.
- PoP 2 absorbs traffic.
- PoP 3 remains reserve.

### Recovery Mode

- control plane re-evaluates node health
- sync-loop stabilizes the registry
- routing is gradually restored

## What Is Missing Right Now

To reach the 3 PoP target, the remaining gaps are:

- independent authoritative DNS
- at least two additional edge hosts
- route health checks across all PoPs
- a single source of truth for failover order
- automation for TLS, routing, and telemetry

## Recommended Implementation Order

1. Stand up PoP 1 as the sovereign primary edge.
2. Add PoP 2 as a warm standby with mirrored routes.
3. Add PoP 3 as a separate fault-domain recovery node.
4. Move DNS authority out of the current external dependency.
5. Add health-based routing and low-TTL failover.
6. Wire the PoPs into the control-plane sync-loop.

## Minimal Success Criteria

- Each PoP serves `/health` and `/status`.
- DNS can switch traffic away from a dead PoP.
- Writes only go to healthy nodes.
- Resonant telemetry remains stable across failover.
- No endpoint contract changes are required for clients.

## Relation to Existing Docs

- Resonant contract: [RESONANT_CORE.md](RESONANT_CORE.md)
- Hardware and mesh requirements: [HARDWARE_MESH_BRIEF.md](HARDWARE_MESH_BRIEF.md)
- Existing Cloudflare hardening: [cloudflare_setup.md](cloudflare_setup.md)
- Current component architecture: [STIGMA_CLOUD_COMPONENT_ARCHITECTURE.md](STIGMA_CLOUD_COMPONENT_ARCHITECTURE.md)
- Practical operations guide: [SOVEREIGN_EDGE_RUNBOOK.md](SOVEREIGN_EDGE_RUNBOOK.md)
- Rollout plan: [SOVEREIGN_EDGE_7_DAY_ROLLOUT.md](SOVEREIGN_EDGE_7_DAY_ROLLOUT.md)
- Concrete topology mapping: [SOVEREIGN_EDGE_TOPOLOGY_CURRENT_KLOUD.md](SOVEREIGN_EDGE_TOPOLOGY_CURRENT_KLOUD.md)
- Day-1 baseline report: [SOVEREIGN_EDGE_DAY1_BASELINE_2026-05-11.md](SOVEREIGN_EDGE_DAY1_BASELINE_2026-05-11.md)
- DNS policy template: [templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json](templates/SOVEREIGN_DNS_POLICY_TEMPLATE.json)
- Production checklist: [SOVEREIGN_EDGE_PRODUCTION_CHECKLIST.md](SOVEREIGN_EDGE_PRODUCTION_CHECKLIST.md)
- Cloudflare DNS integration: [SOVEREIGN_DNS_CLOUDFLARE_INTEGRATION.md](SOVEREIGN_DNS_CLOUDFLARE_INTEGRATION.md)
