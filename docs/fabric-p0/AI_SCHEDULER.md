# P0 #4 - AI-Native Scheduler

## Qellimi

Vendosje e auditueshme e runtime/model/node per cdo kerkesë.

## Inputs

- latency_budget_ms
- privacy_level
- cost_sensitivity
- compute_intensity
- task_type
- required_capabilities
- policy mode

## Objective Function

score =

- w_latency * latency_cost
- w_privacy * privacy_cost
- w_cost * monetary_cost
- w_load * load_cost
- w_trust * trust_cost
- w_capability * capability_penalty

Node me score me te ulet fiton.

## API

`POST /v1/scheduler/decide-auto`

## Auditability

Cdo vendim ruhet me:

- trace_id
`decide-auto` nuk pret listë kandidatësh nga klienti. Kandidatët zbulohen direkt nga NodeDB (`/v1/nodes`) dhe filtrohen sipas:

- `required_capabilities`
- `required_runtime`
- `data_classification`
- `Sovereign Mode` status

Për çdo vendim ruhet edhe `candidate_source: "nodedb"` që audit trail të tregojë qartë nëse kandidatura erdhi nga control-plane real apo nga payload i klientit.
- reason
- score_breakdown
- ranked_candidates
- policy_mode
- sovereign_mode

## Done when

- [ ] Objective function aktive
- [ ] Decision object i standardizuar
- [ ] Audit log aktiv
- [ ] Privacy + sovereign constraints enforced
