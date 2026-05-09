#!/bin/bash
# Kloud Lazy Services Manager
# For 16GB/4vCPU server - keeps essential services, starts others on-demand

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Essential services (always running)
CORE_SERVICES=(
    "kloud-01-postgres"
    "kloud-02-redis"
    "kloud-06-ollama"
    "kloud-07-ollama-multi"
    "kloud-08-ocean-core"
    "kloud-64-api"
    "kloud-65-web"
    "kloud-66-traefik"
)

# Monitoring services
MONITORING_SERVICES=(
    "kloud-67-prometheus"
    "kloud-68-grafana"
    "kloud-69-loki"
    "kloud-70-jaeger"
    "kloud-71-tempo"
    "kloud-75-health-monitor"
)

# AI/Agent services
AI_SERVICES=(
    "kloud-09-alba"
    "kloud-10-albi"
    "kloud-11-jona"
    "kloud-12-asi"
    "kloud-13-alphabet-layers"
    "kloud-14-liam"
    "kloud-15-alda"
    "kloud-16-alba-idle"
    "kloud-17-blerina"
    "kloud-73-cognitive"
)

# Business services
BUSINESS_SERVICES=(
    "kloud-18-cycle-engine"
    "kloud-19-saas-orchestrator"
    "kloud-20-personas"
    "kloud-21-agiem"
    "kloud-53-saas-api"
    "kloud-54-marketplace"
    "kloud-55-economy"
    "kloud-56-reporting"
    "kloud-57-excel"
    "kloud-58-behavioral"
    "kloud-59-analytics"
)

# Specialty services
SPECIALTY_SERVICES=(
    "kloud-60-neurosonix"
    "kloud-61-aviation"
    "kloud-62-multi-tenant"
    "kloud-63-quantum"
    "kloud-72-agent-telemetry"
    "kloud-74-adaptive-router"
)

# Database services
DATABASE_SERVICES=(
    "kloud-03-neo4j"
    "kloud-04-victoriametrics"
    "kloud-05-minio"
)

# Lab services (development only)
LAB_PREFIX="lab-"
DATASOURCE_PREFIX="ds-"

start_group() {
    local group_name=$1
    shift
    local services=("$@")
    
    echo -e "${BLUE}Starting $group_name...${NC}"
    for svc in "${services[@]}"; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${svc}$"; then
            docker start "$svc" 2>/dev/null && echo -e "${GREEN}  ✓ $svc${NC}" || echo -e "${YELLOW}  ~ $svc (already running or not found)${NC}"
        fi
    done
}

stop_group() {
    local group_name=$1
    shift
    local services=("$@")
    
    echo -e "${YELLOW}Stopping $group_name...${NC}"
    for svc in "${services[@]}"; do
        docker stop "$svc" 2>/dev/null && echo -e "${RED}  ✗ $svc${NC}" || true
    done
}

show_status() {
    echo -e "\n${BLUE}=== Kloud Service Status ===${NC}\n"
    
    running=$(docker ps -q | wc -l)
    total=$(docker ps -aq | wc -l)
    
    echo -e "Running: ${GREEN}$running${NC} / Total: $total"
    echo ""
    
    # Load average
    load=$(uptime | awk -F'load average:' '{print $2}')
    echo -e "Load Average:${load}"
    echo ""
    
    # Top CPU consumers
    echo -e "${YELLOW}Top CPU Consumers:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -10
}

show_help() {
    echo -e "${BLUE}Kloud Lazy Services Manager${NC}"
    echo ""
    echo "Usage: $0 <command> [group]"
    echo ""
    echo "Commands:"
    echo "  status              Show current status"
    echo "  minimal             Keep only core services (8 containers)"
    echo "  standard            Core + Monitoring + AI (24 containers)"
    echo "  full                All services except LAB (~44 containers)"
    echo ""
    echo "  start <group>       Start a service group"
    echo "  stop <group>        Stop a service group"
    echo ""
    echo "Groups:"
    echo "  core                Essential services (postgres, redis, api, web)"
    echo "  monitoring          Prometheus, Grafana, Loki, Jaeger"
    echo "  ai                  AI/Agent services (Alba, Albi, Jona, etc.)"
    echo "  business            Business services (SaaS, Economy, Reporting)"
    echo "  specialty           Specialty services (Quantum, Aviation, etc.)"
    echo "  database            Extra databases (Neo4j, Minio, VictoriaMetrics)"
    echo "  lab                 Lab services (development only)"
    echo ""
    echo "Examples:"
    echo "  $0 minimal          Run only essential 8 services"
    echo "  $0 start ai         Start AI services on-demand"
    echo "  $0 stop specialty   Stop specialty services to save resources"
}

case "$1" in
    status)
        show_status
        ;;
    
    minimal)
        echo -e "${YELLOW}Switching to MINIMAL mode (8 core services)...${NC}"
        # Stop everything except core
        docker ps --format '{{.Names}}' | while read name; do
            is_core=false
            for core in "${CORE_SERVICES[@]}"; do
                if [[ "$name" == "$core" ]]; then
                    is_core=true
                    break
                fi
            done
            if [[ "$is_core" == false ]]; then
                docker stop "$name" 2>/dev/null || true
            fi
        done
        show_status
        ;;
    
    standard)
        echo -e "${BLUE}Switching to STANDARD mode (Core + Monitoring + AI)...${NC}"
        start_group "Core" "${CORE_SERVICES[@]}"
        start_group "Monitoring" "${MONITORING_SERVICES[@]}"
        start_group "AI" "${AI_SERVICES[@]}"
        show_status
        ;;
    
    full)
        echo -e "${GREEN}Switching to FULL mode (all except LAB)...${NC}"
        start_group "Core" "${CORE_SERVICES[@]}"
        start_group "Database" "${DATABASE_SERVICES[@]}"
        start_group "Monitoring" "${MONITORING_SERVICES[@]}"
        start_group "AI" "${AI_SERVICES[@]}"
        start_group "Business" "${BUSINESS_SERVICES[@]}"
        start_group "Specialty" "${SPECIALTY_SERVICES[@]}"
        show_status
        ;;
    
    start)
        case "$2" in
            core) start_group "Core" "${CORE_SERVICES[@]}" ;;
            monitoring) start_group "Monitoring" "${MONITORING_SERVICES[@]}" ;;
            ai) start_group "AI" "${AI_SERVICES[@]}" ;;
            business) start_group "Business" "${BUSINESS_SERVICES[@]}" ;;
            specialty) start_group "Specialty" "${SPECIALTY_SERVICES[@]}" ;;
            database) start_group "Database" "${DATABASE_SERVICES[@]}" ;;
            lab)
                echo -e "${YELLOW}Starting LAB services...${NC}"
                docker start $(docker ps -a --filter "name=lab-" --format '{{.Names}}') 2>/dev/null || true
                ;;
            *) echo "Unknown group: $2. Use: core, monitoring, ai, business, specialty, database, lab" ;;
        esac
        ;;
    
    stop)
        case "$2" in
            core) stop_group "Core" "${CORE_SERVICES[@]}" ;;
            monitoring) stop_group "Monitoring" "${MONITORING_SERVICES[@]}" ;;
            ai) stop_group "AI" "${AI_SERVICES[@]}" ;;
            business) stop_group "Business" "${BUSINESS_SERVICES[@]}" ;;
            specialty) stop_group "Specialty" "${SPECIALTY_SERVICES[@]}" ;;
            database) stop_group "Database" "${DATABASE_SERVICES[@]}" ;;
            lab)
                echo -e "${YELLOW}Stopping LAB services...${NC}"
                docker stop $(docker ps --filter "name=lab-" -q) 2>/dev/null || true
                docker stop $(docker ps --filter "name=ds-" -q) 2>/dev/null || true
                ;;
            *) echo "Unknown group: $2. Use: core, monitoring, ai, business, specialty, database, lab" ;;
        esac
        ;;
    
    *)
        show_help
        ;;
esac

