#!/usr/bin/env bash
set -euo pipefail

SERVER="91.98.47.131"
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

echo "[COMPUTE] Ensuring remote directories..."
ssh -i "$SSH_KEY" "$USER@$SERVER" "mkdir -p /opt/kloud /etc/kloud"

echo "[COMPUTE] Building Rust binaries..."
cargo build --release -p asi_trinity -p worker_compute -p telemetry_agent

echo "[COMPUTE] Uploading binaries..."
scp -i "$SSH_KEY" target/release/asi_trinity "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/worker_compute "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/telemetry_agent "$USER@$SERVER:/opt/kloud/"

echo "[COMPUTE] Uploading env + systemd units..."
scp -i "$SSH_KEY" infra/env/compute.env "$USER@$SERVER:/etc/kloud/compute.env"
scp -i "$SSH_KEY" infra/systemd/asi_trinity_heavy.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/worker_compute.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/telemetry_agent.service "$USER@$SERVER:/etc/systemd/system/"

ssh -i "$SSH_KEY" "$USER@$SERVER" "mkdir -p /etc/kloud; cp /etc/kloud/compute.env /etc/kloud/asi_trinity.env; cp /etc/kloud/compute.env /etc/kloud/worker_compute.env; cp /etc/kloud/compute.env /etc/kloud/telemetry_agent.env; systemctl daemon-reload; systemctl enable asi_trinity_heavy worker_compute telemetry_agent; systemctl restart asi_trinity_heavy worker_compute telemetry_agent"

echo "[COMPUTE] Deploy complete."
