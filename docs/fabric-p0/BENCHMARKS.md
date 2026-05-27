# P0 #5 - Benchmark Suite (Ultra-Fast Messaging)

## Qellimi

Matje reale p50/p95/p99 me target URL reale (pa data fake).

## API

- `POST /v1/benchmarks/run`
- `GET /v1/benchmarks/targets`
- `POST /v1/benchmarks/evaluate`

## Skenare

- intra_node
- cross_node
- edge_cloud
- burst
- sustained
- chaos

`evaluate` aplikon threshold policy mbi një rezultat benchmark dhe kthen:

```json
{
 "evaluation": {
  "passed": true,
  "failures": []
 }
}
```

Threshold-et fillestare:

- `p50_ms_max`
- `p95_ms_max`
- `p99_ms_max`
- `error_count_max`
- `throughput_min`

Për CI përdoret skripti [scripts/ci/run_benchmark_gate.py](scripts/ci/run_benchmark_gate.py), i cili:

- thërret `/v1/benchmarks/run`
- thërret `/v1/benchmarks/evaluate`
- shkruan raport JSON opsional
- del me exit code `1` nëse threshold-et dështojnë
- mbështet preset-e standarde: `intra_node`, `cross_node`, `edge_cloud`

Kjo e bën benchmark-un një gate real për pipeline dhe jo vetëm raport observability.

## Output JSON standard

- test_name
- messages
- p50_ms
- p95_ms
- p99_ms
- throughput_msg_sec
- errors
- timestamp

## Rregull

Nese endpoint-i target nuk eshte reachable, benchmark raporton errors; nuk fabricon rezultate.

## Done when

- [ ] Percentile metrics prodhohen nga matje reale
- [ ] Throughput dhe error-rate raportohen
- [ ] Chaos scenario i kontrolluar aktiv
- [ ] CI gate standard ekzekuton benchmark + threshold fail policy

## Komanda CI lokale

Nga root i repo-s `kloud`:

```powershell
py -3.13 scripts/ci/run_benchmark_gate.py --base-url http://127.0.0.1:8000 --preset intra_node
```

Task-et lokale në VS Code:

- `benchmark:gate:intra_node`
- `benchmark:gate:cross_node`
- `benchmark:gate:edge_cloud`
- `benchmark:gate:all`

Artefaktet ruhen te:

- `reports/benchmark-intra_node.json`
- `reports/benchmark-cross_node.json`
- `reports/benchmark-edge_cloud.json`

## GitHub Actions

Workflow-i [benchmark-gate.yml](.github/workflows/benchmark-gate.yml) e nis API-n lokal me `uvicorn`, pret derisa `/health` të bëhet reachable, dhe ekzekuton gate-in si matrix për tre preset-et. Nëse një preset dështon threshold-et, job dështon dhe raporti JSON ngarkohet si artifact.
