# Kloud Cloud - Docker Build Guide

## Public Dashboard Container

### Build Docker Image

```bash
# Build public container
docker build -f Dockerfile.public -t kloud-public:latest .

# Tag for registry
docker tag kloud-public:latest ledjan/kloud-public:latest
```

### Run with Docker Compose

```bash
# Production environment (public dashboard only)
docker-compose -f docker-compose.public.yml up -d

# Development environment
docker-compose up -d
```

### Run Standalone

```bash
# Simple run
docker run -p 3000:3000 \
  -e NODE_ENV=production \
  -e NEXT_PUBLIC_API_URL=https://api.kloud.com \
  --name kloud-public \
  kloud-public:latest

# With Nginx reverse proxy
docker run -p 80:80 -p 443:443 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v $(pwd)/certs:/etc/nginx/certs:ro \
  --name kloud-nginx \
  --link kloud-public:backend \
  nginx:alpine
```

## Container Details

### Image Specifications

- **Base**: node:20-alpine (production build)
- **Size**: ~300-400MB (multi-stage optimized)
- **Port**: 3000 (default Next.js)
- **Health Check**: Every 30s via HTTP GET

### Environment Variables

```bash
NODE_ENV=production                    # Must be 'production'
NEXT_PUBLIC_API_URL=https://api.kloud.com
NEXT_PUBLIC_ANALYTICS=true
```

### Volumes (Optional)

```bash
# For logs
-v kloud-logs:/app/.next

# For SSL certificates (with Nginx)
-v ./certs:/etc/nginx/certs:ro
```

## Deployment

### Push to Docker Hub

```bash
docker login
docker push ledjan/kloud-public:latest
docker push ledjan/kloud-public:$(date +%Y.%m.%d)
```

### Deploy to Production

```bash
# Pull latest image
docker pull ledjan/kloud-public:latest

# Stop and remove old container
docker stop kloud-public
docker rm kloud-public

# Run new container
docker run -d \
  -p 3000:3000 \
  --name kloud-public \
  --restart always \
  ledjan/kloud-public:latest
```

## Kubernetes Deployment (Optional)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kloud-public
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kloud-public
  template:
    metadata:
      labels:
        app: kloud-public
    spec:
      containers:
      - name: kloud-public
        image: ledjan/kloud-public:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.kloud.com"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: kloud-public-service
spec:
  selector:
    app: kloud-public
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs kloud-public

# Check health
docker ps | grep kloud-public
```

### High memory usage

```bash
# Increase Node.js memory
docker run -e NODE_OPTIONS="--max_old_space_size=2048" ...
```

### Port already in use

```bash
# Find and stop container using port 3000
lsof -i :3000
kill -9 <PID>

# Or use different port
docker run -p 8000:3000 ...
```

## Production Checklist

- [ ] Build multi-stage Dockerfile ✓
- [ ] Test Docker image locally ✓
- [ ] Set NODE_ENV=production ✓
- [ ] Configure health checks ✓
- [ ] Add Nginx reverse proxy ✓
- [ ] Setup SSL certificates ✓
- [ ] Configure rate limiting ✓
- [ ] Enable gzip compression ✓
- [ ] Set security headers ✓
- [ ] Document environment variables ✓
- [ ] Create docker-compose.yml ✓
- [ ] Push to Docker Hub ✓
- [ ] Setup CI/CD pipeline
- [ ] Monitor container performance
- [ ] Setup log aggregation

## Quick Start

```bash
# One command to deploy everything
docker-compose -f docker-compose.public.yml up -d --build

# Access application
open http://localhost:3000

# View logs
docker-compose -f docker-compose.public.yml logs -f

# Stop everything
docker-compose -f docker-compose.public.yml down
```

---

**Last Updated**: January 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready 🚀

