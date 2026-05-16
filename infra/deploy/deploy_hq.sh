#!/usr/bin/env bash
set -euo pipefail

SERVER="178.105.52.245"
USER="root"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519_nopwd}"

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
