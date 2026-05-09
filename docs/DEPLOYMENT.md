# 🚀 Kloud Cloud - Deployment Guide

## Environments

| Environment | Server | URL |
|-------------|--------|-----|
| Development | Local | `http://localhost:*` |
| Staging | Docker Compose | `https://staging.kloud.cloud` |
| Production | Hetzner Cloud | `https://kloud.cloud` |

---

## Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- Node.js 20 LTS
- Python 3.11+
- Git

---

## Quick Deployment

### Development (Local)

```bash
# Clone and setup
git clone https://github.com/LedjanAhmati/Kloud-cloud.git
cd Kloud-cloud

# Copy environment file
cp .env.example .env

# Start all services
docker compose up -d

# Check status
docker compose ps
```

### Production (Hetzner)

```bash
# SSH to server
ssh hetzner-new

# Navigate to project
cd /root/Kloud-cloud

# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Check logs
docker compose logs -f --tail=100
```

---

## Infrastructure

### Servers

| Server | IP | Role | Specs |
|--------|-----|------|-------|
| hetzner-new | 46.225.14.83 | Primary | 8 vCPU, 16GB RAM |

### Ports

| Service | Port | Protocol |
|---------|------|----------|
| Nginx (Frontend) | 80, 443 | HTTP/HTTPS |
| FastAPI (API) | 8000 | HTTP |
| Curiosity Ocean | 8030 | HTTP |
| PostgreSQL | 5432 | TCP |
| Redis | 6379 | TCP |
| Prometheus | 9090 | HTTP |
| Grafana | 3000 | HTTP |
| Ollama | 11434 | HTTP |

---

## Docker Compose Services

### Core Services

```yaml
services:
  # Frontend
  web:
    image: kloud/web:latest
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api

  # Backend API
  api:
    image: kloud/api:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  # Curiosity Ocean AI
  ocean:
    image: kloud/ocean-core:latest
    ports:
      - "8030:8030"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    depends_on:
      - ollama
```

### Database Services

```yaml
  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=klouddb
      - POSTGRES_USER=kloud
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
```

### AI Services

```yaml
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

---

## Deployment Steps

### 1. Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SSL certificates valid
- [ ] Backups completed

### 2. Database Migration

```bash
# Run migrations
docker compose exec api alembic upgrade head

# Verify
docker compose exec postgres psql -U kloud -d klouddb -c "\dt"
```

### 3. Deploy Application

```bash
# Build images
docker compose build --no-cache

# Deploy with zero downtime
docker compose up -d --remove-orphans

# Verify deployment
curl -s https://api.kloud.cloud/health | jq
```

### 4. Post-Deployment Verification

```bash
# Check all services are running
docker compose ps

# Check logs for errors
docker compose logs --tail=50 | grep -i error

# Run smoke tests
./scripts/smoke-test.sh
```

---

## Rollback Procedure

### Immediate Rollback

```bash
# Stop current deployment
docker compose down

# Checkout previous version
git checkout HEAD~1

# Redeploy
docker compose up -d
```

### Database Rollback

```bash
# Rollback last migration
docker compose exec api alembic downgrade -1

# Or rollback to specific revision
docker compose exec api alembic downgrade abc123
```

---

## SSL/TLS Configuration

### Let's Encrypt (Certbot)

```bash
# Initial setup
certbot certonly --webroot -w /var/www/certbot \
  -d kloud.cloud \
  -d api.kloud.cloud

# Auto-renewal (cron)
0 3 * * * certbot renew --quiet
```

### Nginx SSL Config

```nginx
server {
    listen 443 ssl http2;
    server_name api.kloud.cloud;
    
    ssl_certificate /etc/letsencrypt/live/kloud.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kloud.cloud/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring

### Health Checks

```bash
# API Health
curl https://api.kloud.cloud/health

# Ocean Health
curl http://localhost:8030/health

# Database Health
docker compose exec postgres pg_isready
```

### Grafana Dashboards

Access: `https://grafana.kloud.cloud`

Available dashboards:
- API Performance
- Database Metrics
- Ocean AI Stats
- System Resources

### Alerts

Configured in Prometheus/Alertmanager:
- High Error Rate (>1%)
- Slow Response Time (>2s p95)
- Service Down
- Disk Space Low (<10%)
- Memory Usage High (>85%)

---

## Backup & Recovery

### Automated Backups

```bash
# Database backup (runs daily via cron)
0 2 * * * docker compose exec postgres pg_dump -U kloud klouddb | gzip > /backups/db-$(date +%Y%m%d).sql.gz

# Retain 30 days
find /backups -name "db-*.sql.gz" -mtime +30 -delete
```

### Manual Backup

```bash
# Full database backup
docker compose exec postgres pg_dump -U kloud -Fc klouddb > backup.dump

# Restore
docker compose exec -T postgres pg_restore -U kloud -d klouddb < backup.dump
```

---

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker compose logs service-name

# Check resource usage
docker stats

# Restart specific service
docker compose restart service-name
```

#### Database Connection Failed
```bash
# Test connection
docker compose exec postgres psql -U kloud -d klouddb

# Check network
docker network ls
docker network inspect kloud-cloud_default
```

#### High Memory Usage
```bash
# Find culprit
docker stats --no-stream

# Restart with limits
docker compose up -d --scale api=2
```

---

## Security Checklist

- [ ] All secrets in environment variables (not code)
- [ ] Database not exposed to public internet
- [ ] HTTPS enforced everywhere
- [ ] Rate limiting enabled
- [ ] CORS configured correctly
- [ ] Firewall rules in place (UFW)
- [ ] SSH key authentication only
- [ ] Regular security updates

---

*Last Updated: February 2026 | Version 2.0.0*

