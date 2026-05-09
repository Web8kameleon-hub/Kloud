#!/bin/bash

# =====================================================
# Nanogridata Gateway - Server-side Deployment
# Purpose: Deploy pre-built Docker image on production
# No Node.js required - image already compiled
# =====================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

# =====================================================
# Step 1: Check prerequisites
# =====================================================
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
  log_error "Docker not found"
  exit 1
fi

log_success "Docker available"

# =====================================================
# Step 2: Create environment file
# =====================================================
log_info "Setting up environment..."

ENV_FILE=".env.nanogridata"

if [ ! -f "$ENV_FILE" ]; then
  log_info "Creating environment file..."
  
  ESP32_SECRET=$(openssl rand -hex 32)
  STM32_SECRET=$(openssl rand -hex 32)
  
  cat > "$ENV_FILE" << EOF
NANOGRIDATA_ESP32_SECRET=$ESP32_SECRET
NANOGRIDATA_STM32_SECRET=$STM32_SECRET
LOG_LEVEL=info
ALBA_ENDPOINT=http://alba:5555
CYCLE_ENDPOINT=http://cycle:5556
EOF
  
  log_success "Environment file created"
else
  log_success "Environment file exists"
fi

# =====================================================
# Step 3: Pull latest code
# =====================================================
log_info "Pulling latest code from GitHub..."

git pull origin main

log_success "Code updated"

# =====================================================
# Step 4: Create network if needed
# =====================================================
log_info "Checking Docker network..."

if ! docker network ls | grep -q kloud; then
  log_info "Creating kloud network..."
  docker network create kloud
fi

log_success "Network ready"

# =====================================================
# Step 5: Start the gateway container
# =====================================================
log_info "Starting Nanogridata Gateway..."

# Stop old container if exists
docker stop nanogridata-gateway 2>/dev/null || true
docker rm nanogridata-gateway 2>/dev/null || true

# Load environment
set -a
source "$ENV_FILE"
set +a

# Start container
docker run -d \
  --name nanogridata-gateway \
  --restart unless-stopped \
  --env-file "$ENV_FILE" \
  -p 5678:5678 \
  -p 5679:5679 \
  --network kloud \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  kloud/nanogridata-gateway:latest

log_success "Container started"

# =====================================================
# Step 6: Verify deployment
# =====================================================
log_info "Verifying deployment..."

sleep 2

HEALTH=$(curl -s http://localhost:5679/health 2>/dev/null || echo '{}')

if echo "$HEALTH" | grep -q "ok"; then
  log_success "✅ Gateway is healthy!"
else
  log_warning "Gateway still initializing..."
  sleep 2
  HEALTH=$(curl -s http://localhost:5679/health 2>/dev/null || echo '{}')
fi

# =====================================================
# Step 7: Display status
# =====================================================
echo ""
echo "=========================================="
echo "🚀 Nanogridata Gateway Deployed"
echo "=========================================="
echo ""
docker ps --filter name=nanogridata-gateway --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
log_success "Gateway listening on:"
echo "   TCP:   0.0.0.0:5678 (data)"
echo "   HTTP:  0.0.0.0:5679 (metrics)"
echo ""
log_info "Test the gateway:"
echo "   curl http://localhost:5679/health"
echo ""
log_info "View logs:"
echo "   docker logs -f nanogridata-gateway"
echo ""
echo "=========================================="

