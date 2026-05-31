# P0 #1 - Standard unik Event Schema + Trace Propagation

## Qellimi

Te standardizohet event envelope ne te gjitha repos: Clisonix-cloud, kloud, wwwmmm, ultrawebthinking, Server Kameleon.

## Specifikim minimal detyrues

- `event_id` (UUID v4)
- `event_type` (p.sh. `clx.llm.request`, `clx.node.health`)
- `timestamp` (ISO8601 UTC)
- `trace.trace_id`, `trace.span_id`, `trace.parent_span_id`, `trace.correlation_id`
- `delivery.retry_count`, `delivery.max_retries`, `delivery.ttl_ms`, `delivery.delivery_mode`
- `payload_version`, `payload_schema`, `payload`
- `metadata.source_service`, `metadata.target_service`, `metadata.priority`, `metadata.auth_context`

## Artefakte

- JSON Schema: `docs/fabric-p0/contracts/clx-event-v1.schema.json`
- OpenAPI fragment: `docs/fabric-p0/contracts/openapi-events-fragment.yaml`

## Integrim i detyrueshem

- Python services: validim ne ingress per cdo event.
- .NET services: validim para publish/consume.
- CI gate: deshtim i build nese schema breakon kompatibilitetin.

## Teste detyruese

1. Trace continuity test (5 hop): trace_id i njejte, span_id unik per hop.
2. Retry behavior test: retry_count rritet, max_retries respektohet, DLQ trigger.
3. Schema validation test: event i pavlefshem refuzohet me 400/422.
4. Perf test: serialization/deserialization p99 < 1ms, event size target < 32KB.

## Done when

- [ ] Te gjitha repos konsumojne `CLX Event v1`.
- [ ] Event validator aktiv ne ingress.
- [ ] CI bllokon schema regressions.
- [ ] Testet e mesiperme kalojne.
- [ ] Dokumenti `EVENTS.md` ekziston ne secilen repo.
