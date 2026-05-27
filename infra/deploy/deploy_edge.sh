#!/usr/bin/env bash
set -euo pipefail

USER="root"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_nopwd}"

# Resolve SSH key path for Git Bash on Windows when HOME points outside user profile.
if [ ! -f "$SSH_KEY" ] && [ -n "${USERPROFILE:-}" ] && command -v cygpath >/dev/null 2>&1; then
  WIN_KEY="$(cygpath -u "$USERPROFILE")/.ssh/id_ed25519_nopwd"
  if [ -f "$WIN_KEY" ]; then
    SSH_KEY="$WIN_KEY"
  fi
fi

# Ensure cargo is available when running from Git Bash.
if ! command -v cargo >/dev/null 2>&1; then
  export PATH="$PATH:$HOME/.cargo/bin:/c/Users/Admin/.cargo/bin:/mnt/c/Users/Admin/.cargo/bin"
fi

deploy_one() {
  local server="$1"
  local env_file="$2"

  echo "[EDGE] Ensuring remote directories on ${server}..."
  ssh -i "$SSH_KEY" "$USER@$server" "mkdir -p /opt/kloud /etc/kloud"

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

deploy_one "46.62.210.251" "infra/env/edge_hel.env"
