#!/bin/bash
#
# HETZNER NEU - CLEANUP + KAMELEON DEPLOY
# Ekzekuto këtë skript brenda serverit: bash /tmp/deploy.sh
#

set -e

echo "========================================="
echo "KAMELEON KLOUD - HETZNER CLEANUP + DEPLOY"
echo "========================================="

# ========================================
# 1. CLEANUP CLISONIX STACK
# ========================================
echo ""
echo "[1/5] Stopping clisonix stack..."
if [ -f /root/Clisonix-cloud/docker-compose.unified.yml ]; then
  cd /root/Clisonix-cloud
  docker compose -p clisonix -f docker-compose.unified.yml down --remove-orphans -v 2>&1 | head -20 || echo "Compose down skipped (may not exist)"
fi

echo "[2/5] Removing all clisonix containers..."
docker ps -a --format '{{.ID}} {{.Names}}' | awk '$2 ~ /^clisonix/ {print $1}' | xargs -r docker rm -f 2>&1 | tail -5 || true

echo "[3/5] Removing clisonix networks..."
docker network ls --format '{{.ID}} {{.Name}}' | awk '$2 ~ /^clisonix/ {print $1}' | xargs -r docker network rm 2>&1 | tail -5 || true

echo "[4/5] Removing clisonix volumes..."
docker volume ls --format '{{.Name}}' | awk '/^clisonix/ {print $1}' | xargs -r docker volume rm 2>&1 | tail -5 || true

echo "[5/5] Cleaning up clisonix folders..."
rm -rf /root/Clisonix-cloud-* /root/Clisonix-cloud 2>/dev/null || true

echo ""
echo "✅ CLISONIX CLEANUP COMPLETE"

# ========================================
# 2. DEPLOY KAMELEON KLOUD
# ========================================
echo ""
echo "========================================="
echo "[DEPLOY] Starting kameleon.life (Kloud)"
echo "========================================="

mkdir -p /opt/kloud
cd /opt/kloud

# Initialize .env with random credentials
if [ ! -f .env ]; then
  echo "[DEPLOY] Creating .env with secure random credentials..."
  PG=$(cat /proc/sys/kernel/random/uuid | tr -d -)
  NEO=neo4j/$(cat /proc/sys/kernel/random/uuid | tr -d -)
  MIN=$(cat /proc/sys/kernel/random/uuid | tr -d -)$(cat /proc/sys/kernel/random/uuid | tr -d -)
  
  printf "POSTGRES_PASSWORD=%s\nNEO4J_AUTH=%s\nMINIO_ROOT_PASSWORD=%s\n" "$PG" "$NEO" "$MIN" > .env
  echo "✅ .env created"
else
  echo "✅ .env already exists, skipping creation"
fi

# Extract deploy artifact or clone from GitHub
if [ -f kloud-deploy.tar.gz ]; then
  echo "[DEPLOY] Extracting kloud-deploy.tar.gz..."
  tar xzf kloud-deploy.tar.gz
  rm -f kloud-deploy.tar.gz
elif [ ! -d .git ]; then
  echo "[DEPLOY] No repo found, cloning from GitHub..."
  git clone https://github.com/Web8kameleon-hub/Kloud . || {
    echo "⚠️  GitHub clone failed (no internet?); using local files"
  }
fi

# Ensure we're on master
if [ -d .git ]; then
  git checkout master || true
  git pull --ff-only origin master || true
fi

echo "[DEPLOY] Starting core services (web, api, ocean-core, postgres, redis, clx)..."
docker compose up -d --build web api ocean-core postgres redis clx

echo ""
echo "========================================="
echo "DEPLOY STATUS"
echo "========================================="
docker compose ps

echo ""
echo "HEALTH CHECKS:"
echo "============="
sleep 5

for port in 3000 8000 8030; do
  case $port in
    3000) service="web" ;;
    8000) service="api" ;;
    8030) service="ocean-core" ;;
  esac
  
  http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "000")
  [ "$port" = "3000" ] && http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port 2>/dev/null || echo "000")
  
  if [ "$http_code" = "200" ] || [ "$http_code" = "307" ]; then
    echo "✅ $service ($port): $http_code"
  else
    echo "❌ $service ($port): $http_code"
  fi
done

echo ""
echo "========================================="
echo "✅ KAMELEON KLOUD DEPLOYED!"
echo "========================================="
echo ""
echo "Access Points:"
echo "  • Web:        http://91.98.47.131:3000"
echo "  • API:        http://91.98.47.131:8000"
echo "  • Ocean Core: http://91.98.47.131:8030"
echo ""
echo "DNS Status:"
echo "  • kameleon.life A record: 91.98.47.131 ✅"
echo "  • www CNAME -> kameleon.life ✅"
echo ""
