#!/bin/bash
# 🔍 Kloud Production Server Diagnostic Script
# Author: Ledjan Ahmati - ABA GmbH
# Server: 46.225.14.83

SERVER="${1:-root@46.225.14.83}"
SSH_KEY="$HOME/.ssh/hetzner_deploy_key"

echo "════════════════════════════════════════════════"
echo "🔍 Kloud Production Server Diagnostic"
echo "   Server: $SERVER"
echo "════════════════════════════════════════════════"
echo ""

# SSH options
SSH_OPTS="-o StrictHostKeyChecking=no"
if [ -f "$SSH_KEY" ]; then
    SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
fi

# Execute diagnostic
ssh $SSH_OPTS $SERVER bash << 'ENDSSH'
echo "════════════════════════════════════════════════"
echo "🔍 KLOUD PRODUCTION DIAGNOSTIC"
echo "════════════════════════════════════════════════"
echo ""

echo "📊 1. DOCKER CONTAINERS:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ocean|ollama|NAMES"
echo ""

echo "🌊 2. OCEAN-CORE LOGS:"
docker logs kloud-ocean-core --tail 30 2>&1
echo ""

echo "🧠 3. OLLAMA MODELS:"
docker exec kloud-ollama ollama list 2>&1 || echo "❌ Ollama failed"
echo ""

echo "💾 4. RESOURCES:"
free -h | grep -E "Mem|Swap"
echo ""

echo "🔥 5. CONTAINER STATS:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "ocean|ollama|NAME"
echo ""

echo "🌐 6. HEALTH:"
curl -s http://localhost:8030/health || echo "❌ Ocean failed"
echo ""
curl -s http://localhost:11434/api/tags || echo "❌ Ollama failed"
echo ""

echo "⚠️ 7. ERRORS:"
docker logs kloud-ocean-core 2>&1 | grep -i "error\|exception" | tail -10
echo ""

echo "✅ COMPLETE"
ENDSSH


