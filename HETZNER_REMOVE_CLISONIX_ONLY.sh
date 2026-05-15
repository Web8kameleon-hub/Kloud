#!/bin/bash
#
# Remove Clisonix footprint from the target Hetzner node.
# This script only performs cleanup. It does not deploy Kloud.
#

set -euo pipefail

echo "========================================="
echo "REMOVE CLISONIX ONLY"
echo "========================================="

echo ""
echo "[1/6] Stopping clisonix compose stack if present..."
if [ -f /root/Clisonix-cloud/docker-compose.unified.yml ]; then
  cd /root/Clisonix-cloud
  docker compose -p clisonix -f docker-compose.unified.yml down --remove-orphans -v || true
fi

echo "[2/6] Removing clisonix containers..."
docker ps -a --format '{{.ID}} {{.Names}}' | awk '$2 ~ /^clisonix/ {print $1}' | xargs -r docker rm -f || true

echo "[3/6] Removing clisonix networks..."
docker network ls --format '{{.ID}} {{.Name}}' | awk '$2 ~ /^clisonix/ {print $1}' | xargs -r docker network rm || true

echo "[4/6] Removing clisonix volumes..."
docker volume ls --format '{{.Name}}' | awk '/^clisonix/ {print $1}' | xargs -r docker volume rm || true

echo "[5/6] Removing clisonix folders..."
rm -rf /root/Clisonix-cloud /root/Clisonix-cloud-* || true

echo "[6/6] Removing obvious clisonix nginx/systemd references if present..."
rm -f /etc/nginx/sites-enabled/clisonix.conf /etc/nginx/sites-available/clisonix.conf || true
rm -f /etc/systemd/system/clisonix.service /etc/systemd/system/clisonix-*.service || true
systemctl daemon-reload || true
systemctl reload nginx || true

echo ""
echo "========================================="
echo "CLISONIX REMOVAL COMPLETE"
echo "========================================="
echo ""
echo "Post-checks:"
echo "  docker ps -a --format '{{.Names}}' | grep -i clisonix"
echo "  docker network ls --format '{{.Name}}' | grep -i clisonix"
echo "  docker volume ls --format '{{.Name}}' | grep -i clisonix"
echo "  ls -la /root | grep -i Clisonix"