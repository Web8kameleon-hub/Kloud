#!/bin/bash

# Kloud Cloud - Server Deployment Script
# Deployment to production server via SSH

set -e

# Configuration
SERVER_HOST="${SERVER_HOST:-kloud.com}"
SERVER_USER="${SERVER_USER:-deploy}"
SERVER_PORT="${SERVER_PORT:-22}"
DEPLOY_DIR="/opt/kloud"
DOCKER_REGISTRY="ledjan"
DOCKER_IMAGE="kloud-public"
DOCKER_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Kloud Cloud Deployment Script${NC}"
echo -e "${YELLOW}================================${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v ssh &> /dev/null; then
    echo -e "${RED}❌ SSH not found${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Test SSH connection
echo -e "${YELLOW}🔐 Testing SSH connection to ${SERVER_USER}@${SERVER_HOST}...${NC}"
ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} "echo '✅ SSH connection successful'"

# Deploy via SSH (follows HOSTING_EXECUTION_BASELINE.md)
echo -e "${YELLOW}🚀 Deploying to server (${SERVER_USER}@${SERVER_HOST}:${DEPLOY_DIR})...${NC}"
echo -e "${YELLOW}Reference: docs/HOSTING_EXECUTION_BASELINE.md${NC}"

ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} << 'BASELINE_EOF'
set -e

DEPLOY_DIR="/opt/kloud"
echo -e "\033[1;33m=== KLOUD DEPLOYMENT (HOSTING_EXECUTION_BASELINE) ===\033[0m"

# STEP 1: Sync code exactly (no partial pulls)
echo -e "\033[1;33m[1/5] Syncing code from origin/master...\033[0m"
cd ${DEPLOY_DIR}

# Verify git repository exists
if [ ! -d .git ]; then
    echo -e "\033[0;31m❌ ERROR: .git directory not found in ${DEPLOY_DIR}\033[0m"
    echo "Run: git clone https://github.com/Web8kameleon-hub/Kloud.git ${DEPLOY_DIR}"
    exit 1
fi

# Sync exactly to remote master
git fetch origin
git reset --hard origin/master
DEPLOYED_SHA=$(git rev-parse --short HEAD)
echo -e "\033[0;32m✅ Synced to master @ ${DEPLOYED_SHA}\033[0m"

# STEP 2: Validate environment file and critical keys
echo -e "\033[1;33m[2/5] Validating environment file...\033[0m"

if [ ! -f .env ]; then
    if [ -f env ]; then
        echo "⚠️  .env missing, copying from env file"
        cp env .env
    else
        echo -e "\033[0;31m❌ ERROR: Neither .env nor env file found\033[0m"
        exit 1
    fi
fi

# Check critical keys (non-empty validation)
if ! grep -q '^STRIPE_WEBHOOK_SECRET=' .env || [ -z "$(grep '^STRIPE_WEBHOOK_SECRET=' .env | cut -d= -f2)" ]; then
    echo -e "\033[0;31m❌ ERROR: STRIPE_WEBHOOK_SECRET missing or empty\033[0m"
    exit 1
fi

if ! grep -q '^DATABASE_URL=' .env || [ -z "$(grep '^DATABASE_URL=' .env | cut -d= -f2)" ]; then
    echo -e "\033[0;31m❌ ERROR: DATABASE_URL missing or empty\033[0m"
    exit 1
fi

if ! grep -q '^REDIS_URL=' .env || [ -z "$(grep '^REDIS_URL=' .env | cut -d= -f2)" ]; then
    echo -e "\033[0;31m❌ ERROR: REDIS_URL missing or empty\033[0m"
    exit 1
fi

echo -e "\033[0;32m✅ Environment file validated (3 critical keys present)\033[0m"

# STEP 3: Build only changed services (accepts service list as argument)
echo -e "\033[1;33m[3/5] Building services...\033[0m"

SERVICES_TO_BUILD="${SERVICES_TO_BUILD:-api ocean-core}"

for SERVICE in $SERVICES_TO_BUILD; do
    echo "  Building: $SERVICE"
    docker compose build $SERVICE || {
        echo -e "\033[0;31m❌ Build failed for $SERVICE\033[0m"
        exit 1
    }
done

echo -e "\033[0;32m✅ Services built: $SERVICES_TO_BUILD\033[0m"

# STEP 4: Restart ONLY changed services (Golden Rule: NO global docker compose down)
echo -e "\033[1;33m[4/5] Restarting services (targeted, no global down)...\033[0m"

for SERVICE in $SERVICES_TO_BUILD; do
    echo "  Stopping: $SERVICE"
    docker compose stop $SERVICE 2>/dev/null || true
    
    echo "  Removing: $SERVICE"
    docker compose rm -f $SERVICE 2>/dev/null || true
    
    echo "  Starting: $SERVICE"
    docker compose up -d --no-deps $SERVICE || {
        echo -e "\033[0;31m❌ Start failed for $SERVICE\033[0m"
        exit 1
    }
done

sleep 2
echo -e "\033[0;32m✅ Services restarted\033[0m"

# STEP 5: Verify runtime and health
echo -e "\033[1;33m[5/5] Verifying health checks...\033[0m"

# Show container status
echo ""
docker compose ps | grep -E 'api|ocean-core|web' || echo "⚠️  No matching services found"

# Health check for API
echo ""
echo "  Testing: API health (port 8000)"
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "\033[0;32m  ✅ API healthy\033[0m"
else
    echo -e "\033[1;33m  ⚠️  API not responding yet (may be starting)\033[0m"
fi

# Health check for Ocean-Core
echo ""
echo "  Testing: Ocean-Core health (port 8030)"
if curl -sf http://localhost:8030/health > /dev/null 2>&1; then
    echo -e "\033[0;32m  ✅ Ocean-Core healthy\033[0m"
else
    echo -e "\033[1;33m  ⚠️  Ocean-Core not responding yet (may be starting)\033[0m"
fi

# Frontend rewrite sanity test
echo ""
echo "  Testing: Frontend rewrite path (/api/health)"
if curl -sf http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "\033[0;32m  ✅ Frontend rewrite working\033[0m"
else
    echo -e "\033[1;33m  ⚠️  Frontend rewrite not responding yet\033[0m"
fi

# Log summary
echo ""
echo -e "\033[0;32m✅ Deployment Flow Complete\033[0m"
echo "  Deployed SHA: ${DEPLOYED_SHA}"
echo "  Services restarted: $SERVICES_TO_BUILD"
echo "  Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "See docs/HOSTING_EXECUTION_BASELINE.md for full reference."

BASELINE_EOF

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo -e "${YELLOW}================================${NC}"
    echo -e "📍 Reference: docs/HOSTING_EXECUTION_BASELINE.md"
    echo -e "📍 Checklist: docs/DEPLOYMENT_CHECKLIST.md"
    echo -e "📍 Server: ${SERVER_USER}@${SERVER_HOST}:${DEPLOY_DIR}"
    echo -e "${YELLOW}================================${NC}"
else
    echo -e "${RED}❌ Deployment failed (exit code: $EXIT_CODE)${NC}"
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "  1. Check HOSTING_EXECUTION_BASELINE.md § 10 (Network Playbook)"
    echo -e "  2. Verify .env file: grep STRIPE_WEBHOOK_SECRET /opt/kloud/.env"
    echo -e "  3. Check service logs: ssh ${SERVER_USER}@${SERVER_HOST} 'cd /opt/kloud && docker compose logs --tail 50'"
    exit $EXIT_CODE
fi

