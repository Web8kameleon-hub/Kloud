#!/bin/bash

# =====================================================
# Nanogridata Gateway Docker Deployment Script
# Purpose: Build and deploy using Docker only (no Node.js required)
# =====================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
  echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
  echo -e "${YELLOW}[!]${NC} $1"
}

# =====================================================
# Step 1: Check prerequisites
# =====================================================
log_info "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
  log_error "Docker not found. Please install Docker."
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  log_error "Docker Compose not found. Please install Docker Compose."
  exit 1
fi

log_success "Docker prerequisites OK"

# =====================================================
# Step 2: Verify compiled files exist
# =====================================================
log_info "Verifying compiled gateway files..."

if [ ! -f "nanogridata_gateway.js" ]; then
  log_error "nanogridata_gateway.js not found"
  echo "Please compile TypeScript first: npx tsc nanogridata_gateway.ts"
  exit 1
fi

if [ ! -f "ocean_core_adapter.js" ]; then
  log_warning "ocean_core_adapter.js not found, skipping (optional)"
else
  log_success "ocean_core_adapter.js found"
fi

log_success "All required files present"

# =====================================================
# Step 3: Load or create environment
# =====================================================
log_info "Setting up environment..."

ENV_FILE=".env.nanogridata"

if [ ! -f "$ENV_FILE" ]; then
  log_warning "Environment file not found, creating..."
  
  # Generate secrets
  ESP32_SECRET=$(openssl rand -hex 32)
  STM32_SECRET=$(openssl rand -hex 32)
  
  cat > "$ENV_FILE" << EOF
# Nanogridata Gateway Environment
NANOGRIDATA_ESP32_SECRET=$ESP32_SECRET
NANOGRIDATA_STM32_SECRET=$STM32_SECRET
LOG_LEVEL=info
ALBA_ENDPOINT=http://alba:5555
CYCLE_ENDPOINT=http://cycle:5556
EOF
  
  log_success "Environment file created"
  echo "📝 Secrets generated in $ENV_FILE:"
  echo "   ESP32_SECRET: ${ESP32_SECRET:0:16}..."
  echo "   STM32_SECRET: ${STM32_SECRET:0:16}..."
else
  log_success "Environment file already exists"
fi

# =====================================================
# Step 4: Build Docker image
# =====================================================
log_info "Building Docker image..."

docker build \
  -f Dockerfile.nanogridata \
  -t kloud/nanogridata-gateway:latest \
  -t kloud/nanogridata-gateway:$(date +%Y%m%d-%H%M%S) \
  .

if [ $? -eq 0 ]; then
  log_success "Docker image built successfully"
else
  log_error "Docker build failed"
  exit 1
fi

# =====================================================
# Step 5: Pull updated compose file
# =====================================================
log_info "Updating from git..."

git pull origin main || log_warning "Git pull failed, continuing with local files"

# =====================================================
# Step 6: Start the gateway
# =====================================================
log_info "Starting Nanogridata Gateway container..."

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
  kloud/nanogridata-gateway:latest

if [ $? -eq 0 ]; then
  log_success "Container started successfully"
else
  log_error "Failed to start container"
  exit 1
fi

# =====================================================
# Step 7: Wait for startup and verify
# =====================================================
log_info "Waiting for gateway to start..."

sleep 3

# Check health
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5679/health || echo "000")

if [ "$HEALTH_RESPONSE" = "200" ]; then
  log_success "✅ Nanogridata Gateway is healthy!"
  log_success "🚀 Gateway is listening on:"
  echo "   - Data port: 0.0.0.0:5678 (TCP)"
  echo "   - Metrics port: 0.0.0.0:5679 (HTTP)"
else
  log_warning "Health check returned: $HEALTH_RESPONSE (may still be starting)"
  sleep 2
  
  # Try again
  HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5679/health || echo "000")
  
  if [ "$HEALTH_RESPONSE" = "200" ]; then
    log_success "✅ Gateway is now healthy!"
  else
    log_error "Gateway health check failed after startup"
    docker logs nanogridata-gateway
    exit 1
  fi
fi

# =====================================================
# Step 8: Display deployment info
# =====================================================
log_info "Deployment complete!"

echo ""
echo "==================================="
echo "📊 Deployment Information"
echo "==================================="
echo ""
echo "Service:        Nanogridata Gateway"
echo "Status:         🟢 RUNNING"
echo "Container ID:   $(docker ps --filter name=nanogridata-gateway -q | head -c 12)"
echo "Image:          kloud/nanogridata-gateway:latest"
echo ""
echo "Ports:"
echo "  - TCP Data:   0.0.0.0:5678"
echo "  - HTTP Metrics: 0.0.0.0:5679"
echo ""
echo "Endpoints:"
echo "  - Health:     http://localhost:5679/health"
echo "  - Metrics:    http://localhost:5679/metrics"
echo ""
echo "To view logs:   docker logs -f nanogridata-gateway"
echo "To stop:        docker stop nanogridata-gateway"
echo "To remove:      docker rm nanogridata-gateway"
echo ""
echo "==================================="
echo ""

# Display secrets info
log_info "Secrets configuration:"
echo "   ESP32 Secret:  $(grep NANOGRIDATA_ESP32_SECRET $ENV_FILE | cut -d= -f2 | cut -c1-16)..."
echo "   STM32 Secret:  $(grep NANOGRIDATA_STM32_SECRET $ENV_FILE | cut -d= -f2 | cut -c1-16)..."
echo ""
echo "   ⚠️  KEEP THESE SECRETS SAFE!"
echo "   Store $ENV_FILE in a secure location"
echo ""

log_success "🎉 Nanogridata Gateway deployment complete!"
log_success "Gateway is ready to receive embedded device packets on port 5678"

