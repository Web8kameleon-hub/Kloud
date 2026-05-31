# P0 #6 - Sovereign Mode

## Qellimi

Sistemi te funksionoje ne edge edhe pa cloud/internet, me fallback automatik dhe resync te sigurt.

## Operational Modes

- normal: edge + cloud + mesh
- degraded: cloud i ngadalte/i paqendrueshem
- sovereign: cloud i padisponueshem, vetem local edge/mesh

## Garanci minimale

- local LLM aktiv ne `degraded` dhe `sovereign`
- local NodeDB source of truth ne `sovereign`
- local pipeline mode ne `sovereign`
- eventet ruhen ne WAL lokal
- resync idempotent kur cloud rikthehet

## API references

- `GET /v1/sovereign/status`
- `POST /v1/sovereign/switch`
- `POST /v1/sovereign/evaluate`
- `POST /v1/sovereign/events`
- `POST /v1/sovereign/resync`

## Fallback chain

1. cloud_slow -> mode `degraded`
2. cloud_unreachable -> mode `sovereign`
3. cloud_recovered -> mode `normal`

## Done when

- [ ] sovereign switch aktiv manual + automatik
- [ ] local LLM fallback aktiv
- [ ] local state WAL aktiv
- [ ] resync idempotent aktiv
- [ ] outage/resync tests kalojne
