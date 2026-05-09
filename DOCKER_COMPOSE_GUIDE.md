# Docker Compose Setup Guide - Kloud Cloud

## Overview

This docker-compose configuration provides a complete local development and production-ready stack for Kloud Cloud including:

- **API Server** (FastAPI on port 8000)
- **Frontend** (Next.js on port 3000)
- **PostgreSQL Database** (port 5432)
- **Redis Cache** (port 6379)
- **MinIO Object Storage** (ports 9000, 9001)
- **Elasticsearch** (port 9200)
- **Kibana** (port 5601)
- **Nginx Reverse Proxy** (ports 80, 443)

## Quick Start

### Prerequisites

```bash
# Verify Docker and Docker Compose installed
docker --version
docker-compose --version

# Ensure ports are available
# Required: 80, 443, 3000, 5432, 5601, 6379, 8000, 9000, 9001, 9200
```

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values (especially secrets)
# REQUIRED changes:
# - JWT_SECRET_KEY
# - API_KEY_SECRET
# - STRIPE keys (if using)
# - SLACK_WEBHOOK_URL (if using)

nano .env  # or your preferred editor
```

### 2. Create Required Directories

```powershell
# PowerShell
New-Item -ItemType Directory -Path "logs" -Force
New-Item -ItemType Directory -Path "uploads" -Force
New-Item -ItemType Directory -Path "nginx\ssl" -Force
New-Item -ItemType Directory -Path "db\migrations" -Force

# Create self-signed SSL certificates for local development
openssl req -x509 -newkey rsa:2048 -keyout nginx\ssl\kloud.key -out nginx\ssl\kloud.crt -days 365 -nodes \
  -subj "/CN=localhost/O=Kloud/C=US"
```

### 3. Start Services

```bash
# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Watch specific service
docker-compose logs -f api
docker-compose logs -f postgres
```

### 4. Verify Services

```bash
# Check all containers running
docker-compose ps

# Test API
curl http://localhost:8000/docs  # Swagger UI
curl http://localhost:8000/health

# Test Frontend
curl http://localhost:3000

# Test Database
docker-compose exec postgres psql -U kloud -d kloud_db -c "SELECT version();"

# Test Redis
docker-compose exec redis redis-cli ping

# Test MinIO
curl http://localhost:9000/minio/health/live

# Test Elasticsearch
curl http://localhost:9200

# Access Kibana
# Open: http://localhost:5601
```

## Service Details

### API Server (FastAPI)

```bash
# Access Swagger UI (interactive API docs)
# http://localhost:8000/docs

# Access ReDoc (API documentation)
# http://localhost:8000/redoc

# Health check
curl http://localhost:8000/health

# View logs
docker-compose logs -f api

# Restart API
docker-compose restart api
```

### Frontend (Next.js)

```bash
# Access application
# http://localhost:3000

# View logs
docker-compose logs -f frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### PostgreSQL Database

```bash
# Connect to database
docker-compose exec postgres psql -U kloud -d kloud_db

# Useful queries
SELECT version();
SELECT * FROM users LIMIT 5;
SELECT * FROM audio_files LIMIT 5;

# Backup database
docker-compose exec postgres pg_dump -U kloud kloud_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec postgres psql -U kloud kloud_db < backup.sql

# Connect from host (if psql installed)
psql -h localhost -U kloud -d kloud_db
```

### Redis Cache

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check memory usage
docker-compose exec redis redis-cli INFO memory

# Clear all cache
docker-compose exec redis redis-cli FLUSHALL

# Monitor Redis commands
docker-compose exec redis redis-cli MONITOR
```

### MinIO S3 Storage

```bash
# Access MinIO Console
# http://localhost:9001
# Credentials: minioadmin / minioadmin

# Upload test file using MinIO CLI
mc alias set minio http://localhost:9000 minioadmin minioadmin
mc cp test.wav minio/kloud-audio/

# List buckets
mc ls minio/

# View object
mc cat minio/kloud-audio/test.wav
```

### Elasticsearch & Kibana

```bash
# Access Kibana
# http://localhost:5601

# Health check
curl http://localhost:9200/_cluster/health

# View indices
curl http://localhost:9200/_cat/indices

# Create index
curl -X PUT http://localhost:9200/logs-kloud

# Insert test document
curl -X POST http://localhost:9200/logs-kloud/_doc \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2024-01-01T00:00:00Z","message":"test"}'

# View documents
curl http://localhost:9200/logs-kloud/_search
```

## Common Tasks

### Development Workflow

```bash
# 1. Make code changes
# 2. Rebuild changed service
docker-compose build api
docker-compose up -d api

# 3. View logs
docker-compose logs -f api

# 4. Test changes
curl http://localhost:8000/health
```

### Database Management

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Add new table"

# Downgrade migration
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history
```

### Scale Services

```bash
# Scale API servers (behind Nginx load balancer)
docker-compose up -d --scale api=3

# This creates api_1, api_2, api_3
# Nginx automatically routes traffic via least_conn
```

### Performance Tuning

```bash
# Check resource usage
docker stats

# Monitor in real-time
docker stats --no-stream=false

# Adjust limits in docker-compose.yml if needed
# Example: Add to api service
# deploy:
#   resources:
#     limits:
#       cpus: '2'
#       memory: 2G
```

### Troubleshooting

```bash
# Service won't start? Check logs
docker-compose logs postgres

# Port already in use?
# Find what's using port
netstat -tulpn | grep 8000

# Clean restart (removes volumes - WARNING: loses data)
docker-compose down -v
docker-compose up -d

# Rebuild everything
docker-compose build --no-cache
docker-compose up -d

# Check service health
docker-compose ps

# Inspect service
docker inspect kloud-api
```

## Production Considerations

### Before Deploying to Production

1. **Change ALL secrets in .env**
   ```bash
   # Generate strong keys
   openssl rand -base64 32  # JWT_SECRET_KEY
   openssl rand -base64 32  # API_KEY_SECRET
   ```

2. **Update Database Credentials**
   ```
   DB_USER=prod_user
   DB_PASSWORD=<very_secure_password>
   ```

3. **Configure SSL Certificates**
   ```bash
   # Use real certificates (Let's Encrypt recommended)
   # Copy to nginx/ssl/
   cp /path/to/cert.crt nginx/ssl/kloud.crt
   cp /path/to/key.key nginx/ssl/kloud.key
   ```

4. **Enable Database Backups**
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup.sh
   ```

5. **Configure Monitoring**
   ```bash
   # Set SLACK_WEBHOOK_URL in .env
   # Configure Sentry for error tracking
   # Enable Elasticsearch for logs
   ```

6. **Set Resource Limits**
   ```yaml
   # In docker-compose.yml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

### Production Deployment

```bash
# Pull latest changes
git pull

# Build with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify
docker-compose ps
curl https://your-domain.com/health
```

## Health Checks

All services have health checks configured:

```bash
# View health status
docker-compose ps

# Manual health check
docker-compose exec api curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000
docker-compose exec postgres pg_isready -U kloud

# Restart unhealthy services automatically
docker update --health-cmd='curl -f http://localhost:8000/health' \
  --health-interval=30s kloud-api
```

## Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service
docker-compose logs -f api

# View last N lines
docker-compose logs --tail=50

# Export logs
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt

# Stream to Elasticsearch (automatic via docker-compose.yml)
# Logs appear in Kibana at http://localhost:5601
```

## Backup & Recovery

```bash
# Backup all data
docker-compose exec postgres pg_dump -U kloud kloud_db | gzip > backup.sql.gz
docker-compose exec redis redis-cli BGSAVE
docker cp kloud-minio:/minio_data minio_backup

# Restore database
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U kloud kloud_db

# Verify restore
docker-compose exec postgres psql -U kloud kloud_db -c "SELECT COUNT(*) FROM users;"
```

## Cleanup

```bash
# Stop all services (keep volumes)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove everything including volumes (WARNING: deletes all data!)
docker-compose down -v

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

## Advanced

### Custom Networks

Already configured in docker-compose.yml:

```bash
# List networks
docker network ls

# Inspect network
docker network inspect kloud-network

# Services can communicate via service name
# Example: API can connect to postgres:5432
```

### Custom Volumes

Data persistence:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect kloud_postgres_data

# Backup volume
docker run --rm -v kloud_postgres_data:/data -v $(pwd):/backup \
  alpine tar -czf /backup/postgres_backup.tar.gz /data
```

### Environment Variables in Running Containers

```bash
# Update .env file
nano .env

# Restart services to apply changes
docker-compose down
docker-compose up -d
```

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintainer**: Kloud Team

