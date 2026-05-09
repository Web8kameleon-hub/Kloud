#!/bin/bash
# deploy-node.sh — run as root on any Hetzner node
# Usage: NODE_ID=2 PEERS="1:46.224.203.89:8080,3:62.238.21.125:8080,4:37.27.216.254:8080" bash deploy-node.sh

set -e

NODE_ID="${NODE_ID:-2}"
LISTEN_PORT="${LISTEN_PORT:-8080}"
PEERS="${PEERS:-1:46.224.203.89:8080}"

echo "=== Kloud Node Deploy ==="
echo "NODE_ID=$NODE_ID  LISTEN_PORT=$LISTEN_PORT"
echo "PEERS=$PEERS"

# 1. Install deps
apt-get update -qq
apt-get install -y -qq curl git build-essential pkg-config libssl-dev

# 2. Install Rust if missing
if ! command -v cargo &>/dev/null; then
  curl https://sh.rustup.rs -sSf | sh -s -- -y --default-toolchain stable
fi
source "$HOME/.cargo/env"

# 3. Clone or update repo
if [ -d /opt/kloud ]; then
  cd /opt/kloud
  git fetch origin master
  git reset --hard origin/master
else
  git clone https://github.com/Web8kameleon-hub/Kloud.git /opt/kloud
  cd /opt/kloud
fi

# 4. Build
cargo build --release -p node

# 5. Write systemd service
cat > /etc/systemd/system/kloud-node.service <<EOF
[Unit]
Description=Kloud Node Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/kloud
Environment=NODE_ID=${NODE_ID}
Environment=LISTEN_PORT=${LISTEN_PORT}
Environment=PEERS=${PEERS}
ExecStart=/opt/kloud/target/release/node
Restart=always
RestartSec=3
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
EOF

# 6. Enable & start
systemctl daemon-reload
systemctl enable kloud-node
systemctl restart kloud-node
sleep 3

systemctl is-active kloud-node && echo "OK: kloud-node active" || echo "FAIL: check journalctl -u kloud-node"
curl -s "http://localhost:9080/status?stigma_level=2" | head -c 200
echo ""
echo "=== Mesh topology ==="
curl -s "http://localhost:9080/mesh/topology"
