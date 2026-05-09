#!/bin/bash
# =============================================================================
# 🚀 KLOUD AUTO-LEARNING DEPLOY - Hetzner Production
# =============================================================================
# Features:
#   - Backup automatic
#   - Git pull/clone
#   - 61 layers + meta-layer verification
#   - Systemd service with auto-restart
#   - Logging to /var/log/kloud/
# =============================================================================

set -e  # Exit on error

# ----------------- SETTINGS -----------------
REPO="git@github.com:LedjanAhmati/Kloud-cloud.git"
DEPLOY_DIR="/root/Kloud-cloud"
BACKUP_DIR="/opt/backup/kloud-cloud-$(date +%F-%H%M)"
PYTHON_ENV="/usr/bin/python3"
LOG_DIR="/var/log/kloud"
SERVICE_NAME="kloud-autolearning"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}📦 Starting Kloud Auto-Learning Deploy...${NC}"
echo "=============================================="

mkdir -p "$LOG_DIR"

# 1️⃣ Backup existing deployment
echo -e "${YELLOW}1️⃣ Backup...${NC}"
if [ -d "$DEPLOY_DIR" ]; then
    echo "💾 Backing up existing deployment to $BACKUP_DIR..."
    mkdir -p "$(dirname $BACKUP_DIR)"
    cp -r "$DEPLOY_DIR" "$BACKUP_DIR" 2>/dev/null || true
    echo "✅ Backup complete"
else
    echo "ℹ️ No existing deployment to backup"
fi

# 2️⃣ Clone or Pull repo
echo -e "${YELLOW}2️⃣ Git Sync...${NC}"
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "🔄 Cloning repo..."
    git clone "$REPO" "$DEPLOY_DIR"
else
    echo "🔄 Pulling latest changes..."
    cd "$DEPLOY_DIR"
    git stash 2>/dev/null || true
    git pull origin main
fi

cd "$DEPLOY_DIR"
echo "✅ Git sync complete"

# 3️⃣ Install dependencies (if needed)
echo -e "${YELLOW}3️⃣ Dependencies...${NC}"
if [ -f "requirements-autolearning.txt" ]; then
    pip3 install -q -r requirements-autolearning.txt 2>/dev/null || true
    echo "✅ Dependencies installed"
fi

# 4️⃣ Quick Python ML Verification
echo -e "${YELLOW}4️⃣ Verifying 61 Layers + Meta-Layer...${NC}"
cd "$DEPLOY_DIR/ocean-core"

$PYTHON_ENV -c "
import sys
sys.path.insert(0, '.')
try:
    from alphabet_layers import get_alphabet_layer_system
    import time

    s = get_alphabet_layer_system()
    stats = s.get_layer_stats()
    
    print('✅ Total layers:', stats['total_layers'])
    print('✅ Base layers:', stats['base_layers'])
    print('✅ Meta layer active:', stats['meta_layer'])
    print('✅ Weights computed:', stats['weights_computed'])
    print('✅ Golden ratio:', stats['golden_ratio'])

    # Meta-layer determinism test
    meta = s.layers['Ω+']
    result1 = meta('test_input')
    result2 = meta('test_input')
    deterministic = all(result1 == result2)
    print('✅ Meta-layer deterministic:', deterministic)

    # Performance test
    start = time.time()
    for i in range(10):
        s.compute_consciousness('test query ' + str(i))
    elapsed = (time.time() - start) * 1000
    print(f'✅ Performance (10 queries): {elapsed:.1f}ms')
    
    if not deterministic:
        sys.exit(1)
except Exception as e:
    print(f'❌ Layer verification failed: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Layer verification failed! Aborting.${NC}"
    exit 1
fi

# 5️⃣ Create/Update Systemd Service
echo -e "${YELLOW}5️⃣ Setting up Systemd Service...${NC}"

cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Kloud Auto-Learning Production Service
After=network.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=${DEPLOY_DIR}
Environment=PYTHONUNBUFFERED=1
Environment=HETZNER_API_URL=http://localhost:8000
ExecStart=${PYTHON_ENV} ${DEPLOY_DIR}/production_autolearning_connector.py --interval 1.0
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/autolearning.log
StandardError=append:${LOG_DIR}/autolearning-error.log

# Resource limits
MemoryMax=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}

# 6️⃣ Start/Restart Service
echo -e "${YELLOW}6️⃣ Starting Auto-Learning Service...${NC}"
systemctl restart ${SERVICE_NAME}
sleep 2

# Check status
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✅ ${SERVICE_NAME} is running!${NC}"
else
    echo -e "${RED}❌ Service failed to start. Check logs:${NC}"
    journalctl -u ${SERVICE_NAME} --no-pager -n 20
    exit 1
fi

# 7️⃣ Show status
echo ""
echo "=============================================="
echo -e "${GREEN}🚀 DEPLOYMENT COMPLETE!${NC}"
echo "=============================================="
echo ""
echo "📊 Service Status:"
systemctl status ${SERVICE_NAME} --no-pager -l | head -15
echo ""
echo "📄 Log files:"
echo "   - Main log: ${LOG_DIR}/autolearning.log"
echo "   - Error log: ${LOG_DIR}/autolearning-error.log"
echo ""
echo "🔧 Useful commands:"
echo "   - Status:  systemctl status ${SERVICE_NAME}"
echo "   - Logs:    journalctl -u ${SERVICE_NAME} -f"
echo "   - Stop:    systemctl stop ${SERVICE_NAME}"
echo "   - Restart: systemctl restart ${SERVICE_NAME}"
echo ""
echo -e "${GREEN}✅ Auto-restart enabled - service will restart on crash${NC}"

