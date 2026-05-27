#!/usr/bin/env bash
set -euo pipefail

SERVER="46.62.210.251"
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

echo "[HQ] Ensuring remote directories..."
ssh -i "$SSH_KEY" "$USER@$SERVER" "mkdir -p /opt/kloud /etc/kloud"

echo "[HQ] Building Rust binaries..."
cargo build --release -p core_api -p ocean_core -p asi_trinity -p telemetry_collector

echo "[HQ] Uploading binaries..."
scp -i "$SSH_KEY" target/release/core_api "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/ocean_core "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/asi_trinity "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/telemetry_collector "$USER@$SERVER:/opt/kloud/"

echo "[HQ] Uploading env + systemd units..."
scp -i "$SSH_KEY" infra/env/hq.env "$USER@$SERVER:/etc/kloud/hq.env"
scp -i "$SSH_KEY" infra/systemd/core_api.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/ocean_core.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/asi_trinity.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/telemetry_collector.service "$USER@$SERVER:/etc/systemd/system/"

ssh -i "$SSH_KEY" "$USER@$SERVER" "mkdir -p /etc/kloud; cp /etc/kloud/hq.env /etc/kloud/core_api.env; cp /etc/kloud/hq.env /etc/kloud/ocean_core.env; cp /etc/kloud/hq.env /etc/kloud/asi_trinity.env; cp /etc/kloud/hq.env /etc/kloud/telemetry_collector.env; systemctl daemon-reload; systemctl enable core_api ocean_core asi_trinity telemetry_collector; systemctl restart core_api ocean_core asi_trinity telemetry_collector"

echo "[HQ] Deploy complete."
