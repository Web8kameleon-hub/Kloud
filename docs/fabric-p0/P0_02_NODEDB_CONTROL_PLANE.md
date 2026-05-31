# P0 #2 - NodeDB Fluid si Control-Plane

## Qellimi

NodeDB te behet source of truth per topology, state, leases, elections dhe routing vendim-marres.

## Data model minimal

### nodes

- `node_id` (unik)
- `role` (edge, gateway, scheduler, storage, mixed)
- `capabilities` (list)
- `status` (healthy, degraded, offline, draining)
- `last_heartbeat_at`
- `latency_ms`
- `zone`
- `version`

### leases

- `lease_id`
- `holder_node_id`
- `acquired_at`
- `expires_at`
- `renew_interval_ms`
- `fencing_token`

### topology_events

- join/leave/role-change/failover timeline

## API minimale

- `GET /v1/nodes`
- `POST /v1/nodes/heartbeat`
- `POST /v1/leases/acquire`
- `POST /v1/leases/renew`
- `GET /v1/leases/{id}`
- `GET /v1/topology/events`

## Sjellja detyruese

- heartbeat cdo 2-5 sekonda
- timeout -> `degraded`, pastaj `offline`
- leader election me lease + fencing_token
- orchestrator ben vendimmarrje vetem nga NodeDB

## Teste detyruese

1. Heartbeat expiry test
2. Lease contention test
3. Leader failover test
4. Partition and recovery test

## Done when

- [ ] Nodes, leases, topology_events aktive.
- [ ] Leader election funksionale.
- [ ] Fencing token kontrollon split-brain.
- [ ] Orchestrator perdor NodeDB per routing.
- [ ] Te gjitha testet kalojne ne CI.
