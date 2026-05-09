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

# Build Docker image
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
docker build -f Dockerfile.public -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG} .

# Push to Docker Hub
echo -e "${YELLOW}📤 Pushing image to Docker Hub...${NC}"
docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${DOCKER_TAG}

# Deploy via SSH
echo -e "${YELLOW}🚀 Deploying to server...${NC}"

ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} << 'EOF'
set -e

echo "📂 Creating deployment directory..."
sudo mkdir -p /opt/kloud
cd /opt/kloud

echo "📥 Pulling latest code from GitHub..."
if [ -d .git ]; then
    git pull origin main
else
    git clone https://github.com/LedjanAhmati/Kloud-cloud.git .
fi

echo "🐳 Stopping old containers..."
sudo docker-compose -f docker-compose.public.yml down || true

echo "🔄 Pulling latest Docker image..."
sudo docker pull ledjan/kloud-public:latest

echo "🚀 Starting new containers..."
sudo docker-compose -f docker-compose.public.yml up -d

echo "⏳ Waiting for health checks..."
sleep 10

echo "✅ Checking container status..."
sudo docker-compose -f docker-compose.public.yml ps

echo "🧪 Testing application..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Application is responsive"
else
    echo "⚠️  Application not responding yet, checking logs..."
    sudo docker-compose -f docker-compose.public.yml logs --tail=50
fi
EOF

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${YELLOW}================================${NC}"
echo -e "📍 Application URL: https://${SERVER_HOST}"
echo -e "📊 Dashboard: https://${SERVER_HOST}/dashboard"
echo -e "📝 API: https://${SERVER_HOST}/api"
echo -e "${YELLOW}================================${NC}"

