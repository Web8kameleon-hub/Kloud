# WireGuard Mesh (Hapi 7)

This folder defines a private 6-node WireGuard fabric on `10.10.0.0/24`.

## Node Map

- HQ: `178.105.52.245` -> `10.10.0.1`
- Compute: `91.98.47.131` -> `10.10.0.2`
- Failover: `46.224.203.89` -> `10.10.0.3`
- Edge Helsinki: `37.27.216.254` -> `10.10.0.4`
- Edge USA: `5.161.114.189` -> `10.10.0.5`
- Edge Singapore: `5.223.75.178` -> `10.10.0.6`

## Safety

- Never commit private keys.
- Keep private keys only on servers in `/etc/wireguard/wg0.conf`.
- Place only example/public references in `infra/wireguard/keys`.

## Key Generation (per server)

```bash
wg genkey | tee privatekey | wg pubkey > publickey
```

## Rollout

1. Replace placeholders in `infra/wireguard/configs/*.wg0.conf`.
2. From repo root run:

```bash
bash infra/deploy/deploy_wireguard_mesh.sh
```

3. Validate from each node:

```bash
ping -c 3 10.10.0.1
wg show
```
