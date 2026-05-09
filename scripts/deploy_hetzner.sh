#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/deploy_hetzner.sh"
  exit 1
fi

DOMAIN="${DOMAIN:-kloud.aiagi.io}"
APP_DIR="${APP_DIR:-/opt/kloud}"

echo "[1/7] Installing base packages"
apt-get update -y
apt-get install -y --no-install-recommends \
  build-essential pkg-config libssl-dev curl git ca-certificates \
  nginx certbot python3-certbot-nginx

if ! command -v cargo >/dev/null 2>&1; then
  echo "[2/7] Installing Rust toolchain"
  su -c "curl https://sh.rustup.rs -sSf | sh -s -- -y" www-data
fi

echo "[3/7] Preparing app directory"
mkdir -p "${APP_DIR}"
if [[ ! -d "${APP_DIR}/.git" ]]; then
  echo "Clone your repository into ${APP_DIR} before running this script."
  exit 1
fi

echo "[4/7] Building node release binary"
cd "${APP_DIR}"
su -s /bin/bash -c "source ~/.cargo/env && cargo build -p node --release" www-data

echo "[5/7] Installing systemd service"
install -m 0644 deploy/systemd/kloud-node.service /etc/systemd/system/kloud-node.service
systemctl daemon-reload
systemctl enable kloud-node
systemctl restart kloud-node

echo "[6/7] Installing nginx site config"
cp deploy/nginx/kloud.aiagi.io.conf /etc/nginx/sites-available/kloud.aiagi.io.conf
sed -i "s/kloud.aiagi.io/${DOMAIN}/g" /etc/nginx/sites-available/kloud.aiagi.io.conf
ln -sf /etc/nginx/sites-available/kloud.aiagi.io.conf /etc/nginx/sites-enabled/kloud.aiagi.io.conf
nginx -t
systemctl reload nginx

echo "[7/7] Issuing TLS certificate"
certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos -m "admin@${DOMAIN}" --redirect

echo
echo "Deployment complete."
echo "Service status: systemctl status kloud-node --no-pager"
echo "Smoke test: curl -s https://${DOMAIN}/status?stigma_level=2"
