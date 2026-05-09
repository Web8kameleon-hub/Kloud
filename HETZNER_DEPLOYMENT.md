# 🚀 Kloud Cloud - Hetzner Deployment Guide

## Overview
Deployment architecture për Kloud Cloud në Hetzner Cloud Infrastructure

## Infrastructure Requirements

### Server Specifications
- **Type**: CX51 (8 vCPU, 32 GB RAM, 360 GB SSD)
- **OS**: Ubuntu 22.04 LTS
- **Location**: EU region (Frankfurt)
- **Network**: Private network + floating IP

### Services to Deploy
1. **Backend API** (Port 8000)
   - FastAPI with 65 endpoints
   - Ocean-Core integration
   - Data processing

2. **Ocean-Core** (Port 8030)
   - 14 Specialist Personas
   - 23 Advanced Labs
   - Knowledge Engine

3. **Frontend** (Port 3000)
   - Next.js application
   - Real-time chat interface
   - Connected to Ocean-Core

4. **Monitoring Stack**
   - Prometheus (Port 9090)
   - Grafana (Port 3000)
   - ELK Stack for logs

## Deployment Steps

### 1. Server Setup
```bash
# SSH into Hetzner server
ssh root@<hetzner_ip>

# Update system
apt update && apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Node.js & Python
apt install -y nodejs npm python3 python3-pip python3-venv

# Clone repository
git clone https://github.com/LedjanAhmati/Kloud-cloud.git
cd Kloud-cloud
```

### 2. Environment Configuration
```bash
# Create .env file
cat > .env << EOF
NODE_ENV=production
OCEAN_CORE_URL=http://localhost:8030
BACKEND_API_URL=http://localhost:8000
DATABASE_URL=postgresql://user:pass@localhost:5432/kloud
REDIS_URL=redis://localhost:6379
HETZNER_API_TOKEN=${HETZNER_TOKEN}
EOF

# Create docker-compose.yml for production
cp docker-compose.prod.yml docker-compose.yml
```

### 3. Docker Build & Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Verify services
docker-compose ps
docker-compose logs -f
```

### 4. SSL/TLS Configuration
```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Generate certificate
certbot certonly --standalone -d kloud.cloud

# Configure Nginx with SSL
cp nginx.conf.ssl /etc/nginx/sites-available/kloud
ln -s /etc/nginx/sites-available/kloud /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### 5. Monitoring Setup
```bash
# Start Prometheus & Grafana
docker-compose -f monitoring/docker-compose.yml up -d

# Access Grafana
# URL: https://kloud.cloud:3000
# User: admin / Password: admin
```

## Docker Compose Configuration

### Production Stack
- **Backend**: FastAPI + Gunicorn
- **Ocean-Core**: FastAPI + Uvicorn
- **Frontend**: Next.js + PM2
- **Database**: PostgreSQL
- **Cache**: Redis
- **Monitoring**: Prometheus + Grafana
- **Reverse Proxy**: Nginx

## Hetzner-Specific Configuration

### Cloud Console Setup
1. Create server in Hetzner Cloud Console
2. Add SSH keys for authentication
3. Create private network for inter-service communication
4. Configure firewall rules:
   - Port 22 (SSH) - Restricted to your IP
   - Port 80 (HTTP) - Public
   - Port 443 (HTTPS) - Public
   - Port 8000 (Backend) - Private
   - Port 8030 (Ocean-Core) - Private

### Floating IP Configuration
```bash
# Assign floating IP
hcloud floating-ip create --type ipv4 --name kloud-ip --server <server_id>

# Setup DNS
# A Record: kloud.cloud → <floating_ip>
```

### Backup Strategy
```bash
# Create volume snapshots
hcloud volume create --server <server_id> --size 100 --name kloud-backup

# Automated daily backup script
# Location: /usr/local/bin/backup-kloud.sh
```

## Performance Tuning

### System Optimization
```bash
# Increase file descriptors
ulimit -n 65535

# Optimize TCP stack
sysctl -w net.core.somaxconn=65535
sysctl -w net.ipv4.tcp_max_syn_backlog=65535

# Configure Nginx for high concurrency
worker_processes auto;
worker_connections 4096;
```

### Database Optimization
```sql
-- Create indexes for frequent queries
CREATE INDEX idx_queries_user ON queries(user_id, created_at);
CREATE INDEX idx_personas_domain ON personas(domain);

-- Enable query caching
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET work_mem = '16MB';
```

## Monitoring & Logging

### Prometheus Metrics
- Backend API response time
- Ocean-Core query processing time
- Docker container stats
- Nginx request rates

### Grafana Dashboards
1. **System Overview**: CPU, Memory, Disk usage
2. **API Performance**: Request latency, throughput
3. **Ocean-Core**: Query processing, confidence scores
4. **Container Stats**: Per-service resource usage

### Log Aggregation
```bash
# ELK Stack configuration
docker-compose -f elk/docker-compose.yml up -d

# Access Kibana
# URL: http://localhost:5601
```

## Troubleshooting

### Check Services Status
```bash
docker-compose ps
docker-compose logs backend
docker-compose logs ocean-core
docker-compose logs frontend
```

### Restart Services
```bash
# Restart specific service
docker-compose restart backend

# Full restart
docker-compose down
docker-compose up -d
```

### Debug Networking
```bash
# Test connectivity
curl http://localhost:8000/api/status
curl http://localhost:8030/api/status

# Check network
docker network ls
docker network inspect kloud_default
```

## Deployment Checklist

- [ ] Server created in Hetzner
- [ ] SSH keys configured
- [ ] Docker & dependencies installed
- [ ] Repository cloned
- [ ] Environment variables set
- [ ] Docker images built
- [ ] Services running
- [ ] SSL/TLS configured
- [ ] Monitoring stack running
- [ ] Backups configured
- [ ] DNS records updated
- [ ] Tests passing

## Rollback Procedure

```bash
# Get previous image tag
docker images | grep kloud

# Rollback to previous version
docker-compose down
docker-compose up -d --scale backend=1

# Verify services
docker-compose logs -f
```

## Performance Metrics (Expected)

- **Backend API**: <200ms response time (p95)
- **Ocean-Core**: 2-10s query processing
- **Frontend**: <1s page load time
- **System**: <30% CPU utilization (normal load)
- **Memory**: <70% utilization at peak

## Support & Issues

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review Grafana dashboards
3. Contact Hetzner support for infrastructure issues
4. File GitHub issues for application problems

---

**Last Updated**: January 18, 2026
**Deployment Version**: 1.0.0

