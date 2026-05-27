# P0 #3 - Self-Healing Nodes

## Qellimi
Self-healing i plote: detection -> diagnosis -> remediation -> verification -> incident log.

## Detection
- heartbeat + metrics: cpu, mem, battery, signal_strength, queue_depth
- status transitions: healthy -> degraded -> offline

## Diagnosis (deterministe)
- network_unreachable
- battery_low
- cpu_throttling
- mesh_partition
- llm_local_failure
- job_stuck
- queue_overflow
- heartbeat_timeout

## Remediation actions
- `node.soft_reset()`
- `node.hard_reset()`
- `node.rejoin_mesh()`
- `node.sync_state()`
- `node.drain()`
- `node.resume()`
- `node.switch_llm(mode)`
- `node.rebalance_jobs()`

## Verification
- kerkon 2-3 heartbeat te shendetshme pas remediation
- nese deshton, aktivizo fallback policy

## Incident logging
- `incident_id`
- `node_id`
- `diagnosis`
- `actions_taken`
- `duration_ms`
- `resolved`

## Teste detyruese
1. heartbeat timeout -> reroute + incident
2. mesh partition -> rejoin + sync
3. queue overflow -> rebalance
4. local LLM failure -> switch local/cloud
5. fallback chain soft->hard reset

## Done when
- [ ] Detection, diagnosis, remediation, verification aktive.
- [ ] Policy engine i dokumentuar dhe i testuar.
- [ ] Incident logs queryable.
- [ ] 5 testet e detyruara kalojne.
