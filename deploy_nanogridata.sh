#!/bin/bash
# Nanogridata Gateway Deployment Script
# Zero-downtime deployment, minimal system impact

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/nanogridata_deploy.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

log() {
  echo "[$TIMESTAMP] $@" | tee -a "$LOG_FILE"
}

success() {
  echo "✅ $@" | tee -a "$LOG_FILE"
}

error() {
  echo "❌ $@" | tee -a "$LOG_FILE"
  exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# PRE-DEPLOYMENT CHECKS
# ═══════════════════════════════════════════════════════════════════════════

log "Starting Nanogridata Gateway deployment..."

# Check Node.js
if ! command -v node &> /dev/null; then
  error "Node.js not found. Please install Node.js 18+"
fi
NODE_VERSION=$(node -v)
log "Node.js version: $NODE_VERSION"

# Check Docker
if ! command -v docker &> /dev/null; then
  error "Docker not found. Please install Docker"
fi
DOCKER_VERSION=$(docker --version)
log "Docker version: $DOCKER_VERSION"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
  error "Docker Compose not found. Please install Docker Compose"
fi
DOCKER_COMPOSE_VERSION=$(docker-compose --version)
log "Docker Compose version: $DOCKER_COMPOSE_VERSION"

# ═══════════════════════════════════════════════════════════════════════════
# BUILD PHASE
# ═══════════════════════════════════════════════════════════════════════════

log "Building TypeScript files..."

# Compile TypeScript
npx tsc nanogridata_gateway.ts \
  --target ES2020 \
  --module commonjs \
  --lib es2020 \
  --declaration false \
  --outDir . \
  --skipLibCheck true \
  --strict true \
  --esModuleInterop true \
  2>&1 | tee -a "$LOG_FILE"

success "TypeScript compilation complete"

# ═══════════════════════════════════════════════════════════════════════════
# ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════════

log "Setting up environment..."

# Create .env file if not exists
if [ ! -f "$PROJECT_DIR/.env.nanogridata" ]; then
  log "Creating .env.nanogridata file..."
  cat > "$PROJECT_DIR/.env.nanogridata" << 'EOF'
# Nanogridata Gateway Configuration

# Device secrets (hex format, 32 bytes minimum)
NANOGRIDATA_ESP32_SECRET=aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899
NANOGRIDATA_STM32_SECRET=aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899

# Service endpoints (internal Docker network)
ALBA_ENDPOINT=http://alba:5555
CYCLE_ENDPOINT=http://cycle:5556
INFLUXDB_ENDPOINT=http://influxdb:8086

# Logging
LOG_LEVEL=info
EOF
  log "Created .env.nanogridata (⚠️  UPDATE SECRETS BEFORE PRODUCTION)"
else
  log "Using existing .env.nanogridata"
fi

# ═══════════════════════════════════════════════════════════════════════════
# DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════════════

log "Deploying Nanogridata Gateway..."

# Check if ALBA service is running
if ! docker ps --filter "name=alba" --filter "status=running" | grep -q alba; then
  error "ALBA service not running. Start the main system first: docker-compose up -d alba"
fi

log "ALBA service verified"

# Deploy gateway (separate from main compose)
cd "$PROJECT_DIR"

log "Starting Nanogridata Gateway container..."
docker-compose -f docker-compose.nanogridata.yml up -d --build nanogridata-gateway 2>&1 | tee -a "$LOG_FILE"

# Wait for gateway to be ready
log "Waiting for gateway to be ready..."
sleep 3

for i in {1..30}; do
  if curl -s http://localhost:5679/health > /dev/null 2>&1; then
    success "Nanogridata Gateway is ready!"
    break
  fi
  
  if [ $i -eq 30 ]; then
    error "Gateway failed to start. Check logs: docker-compose -f docker-compose.nanogridata.yml logs nanogridata-gateway"
  fi
  
  echo -n "."
  sleep 1
done

# ═══════════════════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

log "Verifying deployment..."

# Check container status
CONTAINER_STATUS=$(docker ps -f "name=nanogridata-gateway" --format "{{.Status}}")
log "Container status: $CONTAINER_STATUS"

# Get gateway stats
STATS=$(curl -s http://localhost:5679/stats)
log "Gateway stats: $STATS"

# Test connectivity
log "Testing TCP connectivity on port 5678..."
if timeout 2 bash -c 'echo -n "" > /dev/tcp/localhost/5678' 2>/dev/null; then
  success "TCP port 5678 is open and listening"
else
  error "TCP port 5678 is not accessible"
fi

# ═══════════════════════════════════════════════════════════════════════════
# POST-DEPLOYMENT
# ═══════════════════════════════════════════════════════════════════════════

log "Post-deployment checks..."

# List running containers
log "Running containers:"
docker ps --filter "label=project=kloud" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | tee -a "$LOG_FILE"

# Show resource usage
log "Gateway resource usage:"
docker stats --no-stream nanogridata-gateway 2>/dev/null | tail -1 | tee -a "$LOG_FILE"

# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

success "Nanogridata Gateway deployment complete!"

cat << 'EOF'

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NANOGRIDATA GATEWAY - DEPLOYMENT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Service: nanogridata-gateway
✅ Status: Running
✅ TCP Port: 5678 (embedded device connections)
✅ Metrics Port: 5679 (monitoring)
✅ Memory: 256MB limit, 64MB reserved
✅ CPU: 0.5 limit, 0.1 reserved

📊 MONITORING ENDPOINTS
  - Health Check: http://localhost:5679/health
  - Statistics: http://localhost:5679/stats
  - Metrics: http://localhost:5679/metrics (Prometheus format)

🔧 NEXT STEPS
  1. Update NANOGRIDATA_ESP32_SECRET and NANOGRIDATA_STM32_SECRET in .env.nanogridata
  2. Configure embedded devices to connect to port 5678
  3. Monitor gateway logs: docker-compose -f docker-compose.nanogridata.yml logs -f
  4. Check packet flow in ALBA: http://localhost:5555/docs

📡 EMBEDDED DEVICE CONFIG
  Server: <your-server-ip>
  Port: 5678
  Protocol: Nanogridata v1.0 (TCP)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

log "Deployment log saved to: $LOG_FILE"

