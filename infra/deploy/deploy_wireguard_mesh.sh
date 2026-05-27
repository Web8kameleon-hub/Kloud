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

# Ensure WireGuard exists first on the target node.
for server in 46.62.210.251; do
  echo "[WG] Installing WireGuard on ${server}"
  ssh -i "$SSH_KEY" "$USER@$server" "apt-get update -y && apt-get install -y wireguard"
done

copy_and_enable "46.62.210.251" "infra/wireguard/configs/hq.wg0.conf"

echo "[WG] Mesh rollout complete."
