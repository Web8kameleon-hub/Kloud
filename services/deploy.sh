#!/bin/bash
# =============================================================================
# KLOUD MICROSERVICES DEPLOYMENT SCRIPT
# =============================================================================
# Përdorimi: ./deploy.sh [all|core|reporting|excel]
# =============================================================================

set -e

SERVICE=${1:-all}
NETWORK="kloud-services"

echo "🚀 Kloud Microservices Deployment"
echo "======================================"

# Krijo network nëse nuk ekziston
docker network create $NETWORK 2>/dev/null || true

deploy_core() {
    echo "📦 Deploying Core API..."
    cd core
    docker build -t kloud-core:latest .
    docker stop kloud-core 2>/dev/null || true
    docker rm kloud-core 2>/dev/null || true
    docker run -d \
        --name kloud-core \
        --network $NETWORK \
        --network root_kloud \
        -p 8000:8000 \
        --restart unless-stopped \
        kloud-core:latest
    cd ..
    echo "✅ Core API deployed on port 8000"
}

deploy_reporting() {
    echo "📊 Deploying Reporting Service..."
    cd reporting
    docker build -t kloud-reporting:latest .
    docker stop kloud-reporting 2>/dev/null || true
    docker rm kloud-reporting 2>/dev/null || true
    docker run -d \
        --name kloud-reporting \
        --network $NETWORK \
        --network root_kloud \
        -p 8001:8001 \
        -e CORE_API_URL=http://kloud-core:8000 \
        --restart unless-stopped \
        kloud-reporting:latest
    cd ..
    echo "✅ Reporting Service deployed on port 8001"
}

deploy_excel() {
    echo "📗 Deploying Excel Service..."
    cd excel
    docker build -t kloud-excel:latest .
    docker stop kloud-excel 2>/dev/null || true
    docker rm kloud-excel 2>/dev/null || true
    docker run -d \
        --name kloud-excel \
        --network $NETWORK \
        --network root_kloud \
        -p 8002:8002 \
        -e CORE_API_URL=http://kloud-core:8000 \
        --restart unless-stopped \
        kloud-excel:latest
    cd ..
    echo "✅ Excel Service deployed on port 8002"
}

case $SERVICE in
    core)
        deploy_core
        ;;
    reporting)
        deploy_reporting
        ;;
    excel)
        deploy_excel
        ;;
    all)
        deploy_core
        sleep 3
        deploy_reporting
        deploy_excel
        ;;
    *)
        echo "Usage: ./deploy.sh [all|core|reporting|excel]"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Services Status:"
docker ps --filter "name=kloud-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

