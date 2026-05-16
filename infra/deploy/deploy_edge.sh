#!/usr/bin/env bash
set -euo pipefail

USER="root"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_nopwd}"

deploy_one() {
  local server="$1"
  local env_file="$2"

  echo "[EDGE] Building edge_gateway binary..."
  cargo build --release -p edge_gateway -p telemetry_agent

  echo "[EDGE] Uploading binary to ${server}..."
  scp -i "$SSH_KEY" target/release/edge_gateway "$USER@$server:/opt/kloud/"
  scp -i "$SSH_KEY" target/release/telemetry_agent "$USER@$server:/opt/kloud/"

  echo "[EDGE] Uploading env + systemd unit to ${server}..."
  scp -i "$SSH_KEY" "$env_file" "$USER@$server:/etc/kloud/edge.env"
  scp -i "$SSH_KEY" infra/systemd/edge_gateway.service "$USER@$server:/etc/systemd/system/"
  scp -i "$SSH_KEY" infra/systemd/telemetry_agent.service "$USER@$server:/etc/systemd/system/"

  ssh -i "$SSH_KEY" "$USER@$server" "mkdir -p /etc/kloud; cp /etc/kloud/edge.env /etc/kloud/edge_gateway.env; cp /etc/kloud/edge.env /etc/kloud/telemetry_agent.env; systemctl daemon-reload; systemctl enable edge_gateway telemetry_agent; systemctl restart edge_gateway telemetry_agent"

  echo "[EDGE] ${server} deploy complete."
}

deploy_one "37.27.216.254" "infra/env/edge_hel.env"
deploy_one "5.161.114.189" "infra/env/edge_us.env"
deploy_one "5.223.75.178" "infra/env/edge_sg.env"
