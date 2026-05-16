# Kloud Systemd Deployment Map (Hapi 4)

Kjo dosje permban unit files systemd te ndara sipas servereve reale.

## Server mapping

- `cpx62-hq/` (178.105.52.245): `core_api`, `ocean_core`, `asi_trinity (controller)`, `telemetry_collector`
- `ccx33-compute/` (91.98.47.131): `worker_compute`, `asi_trinity_heavy_(alba|albi|jona)`, `telemetry_agent`
- `cx43-failover/` (46.224.203.89): `core_api_mirror`, `ocean_core_standby`, `telemetry_collector_replica`
- `edge-nodes/` (37.27.216.254 / 5.161.114.189 / 5.223.75.178): `edge_gateway_(hel|ash|sin)`, `telemetry_agent_edge`

## Install commands

Vendos service file ne host-in perkates:

```bash
sudo cp <service>.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable <service>
sudo systemctl start <service>
sudo systemctl status <service> --no-pager
```

## Recommended runtime paths

- Binaries: `/opt/kloud/<binary_name>`
- Configs: `/etc/kloud/*.toml`
- Optional env overrides: `/etc/kloud/*.env`

## Example: CPX62 core_api

```bash
sudo cp infra/systemd/cpx62-hq/core_api.service /etc/systemd/system/core_api.service
sudo systemctl daemon-reload
sudo systemctl enable core_api
sudo systemctl start core_api
```

## Note

`cargo check` ne kete workstation deshtoi nga mungesa e linker runtime (`msvcrt.lib`) ne mjedisin lokal Windows, jo nga kodi i crates. Skeleton-et e crates jane krijuar ne workspace dhe te gatshme per build ne host Linux/CI.
