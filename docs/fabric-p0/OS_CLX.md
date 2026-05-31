# OS-CLX Layer

OS-CLX eshte sistemi operativ i inteligjences: process, channel, volume, pipeline, runtime contract.

## Primitive

1. Process

- njesi e izoluar ekzekutimi
- timeout/retry/resource limits

1. Channel

- i tipizuar, i versionuar
- tracing + backpressure

1. Volume

- session/cache/pipeline/telemetry/mesh state
- TTL + encryption + WAL

1. Pipeline

- flow deklarativ dhe i auditueshem
- edge/cloud/mesh compatible

1. Runtime Contract

- input/output schema
- timeout/retry
- security capabilities

## No fake rule

- telemetry, benchmark dhe state jane reale
- nese dependency mungon, kthehet error i qarte (jo numer i sajuar)

## Test matrix (detyrues)

- process isolation
- channel backpressure
- pipeline determinism
- volume WAL recovery
- timeout enforcement
- capability security enforcement
