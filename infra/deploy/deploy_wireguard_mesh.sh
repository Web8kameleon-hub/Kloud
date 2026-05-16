#!/usr/bin/env bash
set -euo pipefail

SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_nopwd}"
USER="root"

copy_and_enable() {
  local server_ip="$1"
  local conf_path="$2"

  echo "[WG] Applying ${conf_path} -> ${server_ip}"
  scp -i "$SSH_KEY" "$conf_path" "$USER@$server_ip:/etc/wireguard/wg0.conf"
  ssh -i "$SSH_KEY" "$USER@$server_ip" "chmod 600 /etc/wireguard/wg0.conf; systemctl enable wg-quick@wg0; systemctl restart wg-quick@wg0; wg show"
}

# Ensure WireGuard exists first on all nodes.
for server in 178.105.52.245 91.98.47.131 46.224.203.89 37.27.216.254 5.161.114.189 5.223.75.178; do
  echo "[WG] Installing WireGuard on ${server}"
  ssh -i "$SSH_KEY" "$USER@$server" "apt-get update -y && apt-get install -y wireguard"
done

copy_and_enable "178.105.52.245" "infra/wireguard/configs/hq.wg0.conf"
copy_and_enable "91.98.47.131" "infra/wireguard/configs/compute.wg0.conf"
copy_and_enable "46.224.203.89" "infra/wireguard/configs/failover.wg0.conf"
copy_and_enable "37.27.216.254" "infra/wireguard/configs/edge_hel.wg0.conf"
copy_and_enable "5.161.114.189" "infra/wireguard/configs/edge_us.wg0.conf"
copy_and_enable "5.223.75.178" "infra/wireguard/configs/edge_sg.wg0.conf"

echo "[WG] Mesh rollout complete."
