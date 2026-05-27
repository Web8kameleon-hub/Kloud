# No Fake Rule

## Parimi

`No fake ever` do të thotë: runtime API, control-plane, benchmark, dashboard, reporting dhe telemetry nuk duhet të sajojnë vlera kur burimi real mungon.

## Sjellja e detyrueshme

- nëse burimi real ekziston, kthe të dhëna reale
- nëse burimi real mungon, kthe `4xx/5xx` me `error` të qartë
- mos përdor `mock`, `demo`, `simulated`, `placeholder`, `estimated` për output runtime
- mos gjenero histori sintetike për observability ose reporting

## Burime të lejuara

- sensore reale: `modbus`, `opcua`, `mqtt`, `serial`, `vendor_sdk`
- observability reale: `prometheus`, `victoriametrics`, `alertmanager`, `timeseries_storage`
- container/runtime state: `docker_cli`, `container_runtime_api`

## Kur lejohet data artificiale

- vetëm në testet unit/integration
- vetëm në fixture files jashtë runtime paths
- vetëm në dokumentim shembujsh, jo në endpoint-e aktive

## CI Gate

Skripti [check_no_fake.py](scripts/ci/check_no_fake.py) skanon `apps/api` dhe dështon kur gjen pattern-e si:

- `_get_mock_*`
- `mock data`
- `simulated data`
- `demo data`
- `Replace with`

## Rregull operativ

Nëse një endpoint nuk ka burim real ende, zgjidhja e saktë është:

1. kthe `503 Service Unavailable`
2. shpjego `error` dhe `required_sources`
3. mos kthe asnjë fushë të sajuar
