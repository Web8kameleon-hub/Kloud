#!/usr/bin/env bash
set -euo pipefail

SERVER="46.224.203.89"
USER="root"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_nopwd}"

echo "[FAILOVER] Building Rust binaries..."
cargo build --release -p core_api -p ocean_core -p telemetry_collector

echo "[FAILOVER] Uploading binaries..."
scp -i "$SSH_KEY" target/release/core_api "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/ocean_core "$USER@$SERVER:/opt/kloud/"
scp -i "$SSH_KEY" target/release/telemetry_collector "$USER@$SERVER:/opt/kloud/"

echo "[FAILOVER] Uploading env + systemd units..."
scp -i "$SSH_KEY" infra/env/failover.env "$USER@$SERVER:/etc/kloud/failover.env"
scp -i "$SSH_KEY" infra/systemd/core_api.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/ocean_core_standby.service "$USER@$SERVER:/etc/systemd/system/"
scp -i "$SSH_KEY" infra/systemd/telemetry_collector.service "$USER@$SERVER:/etc/systemd/system/"

ssh -i "$SSH_KEY" "$USER@$SERVER" "mkdir -p /etc/kloud; cp /etc/kloud/failover.env /etc/kloud/core_api.env; cp /etc/kloud/failover.env /etc/kloud/ocean_core.env; cp /etc/kloud/failover.env /etc/kloud/telemetry_collector.env; systemctl daemon-reload; systemctl enable core_api ocean_core_standby telemetry_collector; systemctl restart core_api ocean_core_standby telemetry_collector"

echo "[FAILOVER] Deploy complete."
