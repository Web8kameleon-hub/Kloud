# Kubernetes Deployment Guide - Kloud Cloud

## Overview

This guide provides complete instructions for deploying Kloud Cloud to Kubernetes (K8s) in production environments.

**Architecture:**
- Multi-node Kubernetes cluster (3+ nodes recommended)
- PostgreSQL StatefulSet for data persistence
- Redis StatefulSet for caching
- FastAPI Deployment with 3+ replicas
- Next.js frontend
- Nginx Ingress controller
- Prometheus & Grafana for monitoring
- Jaeger for distributed tracing
- Elasticsearch & Kibana for logging

## Prerequisites

### Required Tools

```bash
# Kubernetes client
kubectl version --client

# Helm (optional but recommended)
helm version

# Docker for building images
docker version

# Container registry (Docker Hub, ECR, GCR, etc.)
# Account and credentials configured
```

### Kubernetes Cluster Requirements

```
Minimum:
- 3 nodes (1 control-plane, 2 workers)
- 2 CPU per node
- 4GB RAM per node
- 20GB disk per node

Recommended:
- 5+ nodes
- 4 CPU per node
- 8GB RAM per node
- 50GB disk per node

Cluster version: Kubernetes 1.20+
```

### Cluster Setup

```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Expected output: 3+ nodes in Ready state

# Install metrics-server (if not present)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify metrics-server
kubectl get deployment metrics-server -n kube-system
```

## Step 1: Prepare Container Images

### Build and Push Images

```bash
# Set your container registry
REGISTRY=your-docker-hub-username
# or
REGISTRY=your-ecr-registry.dkr.ecr.us-east-1.amazonaws.com

# Build API image
docker build -f Dockerfile -t $REGISTRY/kloud-api:1.0.0 .
docker push $REGISTRY/kloud-api:1.0.0

# Build frontend image
docker build -f Dockerfile.frontend -t $REGISTRY/kloud-frontend:1.0.0 .
docker push $REGISTRY/kloud-frontend:1.0.0

# Tag as latest
docker tag $REGISTRY/kloud-api:1.0.0 $REGISTRY/kloud-api:latest
docker tag $REGISTRY/kloud-frontend:1.0.0 $REGISTRY/kloud-frontend:latest
docker push $REGISTRY/kloud-api:latest
docker push $REGISTRY/kloud-frontend:latest
```

### Create Image Pull Secret (if using private registry)

```bash
# Create secret
kubectl create secret docker-registry regcred \
  --docker-server=$REGISTRY \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email@example.com \
  -n kloud

# Verify
kubectl get secret regcred -n kloud
```

## Step 2: Install Prerequisites

### Install Nginx Ingress Controller

```bash
# Using Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Verify
kubectl get svc -n ingress-nginx
```

### Install Cert-Manager (for automatic SSL)

```bash
# Using Helm
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Verify
kubectl get crd | grep cert-manager
```

### Install Prometheus Operator (optional but recommended)

```bash
# Using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Verify
kubectl get all -n monitoring
```

## Step 3: Deploy Kloud Cloud

### Create Namespace

```bash
# Create namespace
kubectl create namespace kloud

# Label namespace
kubectl label namespace kloud app=kloud environment=production
```

### Update Configuration

```bash
# Edit .env values
# Update: JWT_SECRET_KEY, API_KEY_SECRET, database passwords, etc.
nano .env

# Or pass as environment variables
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export API_KEY_SECRET=$(openssl rand -base64 32)
```

### Deploy Manifests

```bash
# Apply in order
kubectl apply -f k8s/01-namespace-config.yaml
kubectl apply -f k8s/02-api-deployment.yaml
kubectl apply -f k8s/03-database-statefulset.yaml
kubectl apply -f k8s/04-ingress-tls.yaml
kubectl apply -f k8s/05-monitoring.yaml

# Verify deployments
kubectl get all -n kloud
```

### Wait for Deployments

```bash
# Watch rollout progress
kubectl rollout status deployment/kloud-api -n kloud --timeout=300s
kubectl rollout status deployment/kloud-frontend -n kloud --timeout=300s

# Check pod status
kubectl get pods -n kloud

# Expected: All pods in Running state
```

## Step 4: Verify Deployment

### Health Checks

```bash
# Check pod logs
kubectl logs -n kloud deployment/kloud-api -f

# Check database connection
kubectl exec -it -n kloud postgres-0 -- psql -U kloud -d kloud_db -c "SELECT version();"

# Check Redis connection
kubectl exec -it -n kloud redis-0 -- redis-cli ping

# Check API health
kubectl port-forward -n kloud svc/kloud-api-service 8000:8000
curl http://localhost:8000/health
```

### Access Application

```bash
# Get Ingress IP/hostname
kubectl get ingress -n kloud

# Add to /etc/hosts if using hostname
echo "YOUR_IP_ADDRESS kloud.com api.kloud.com app.kloud.com" | sudo tee -a /etc/hosts

# Access via browser
# http://kloud.com
# http://api.kloud.com/docs (Swagger UI)
# http://app.kloud.com
```

### Access Monitoring

```bash
# Prometheus
kubectl port-forward -n kloud svc/prometheus-service 9090:9090
# Open: http://localhost:9090

# Grafana
kubectl port-forward -n kloud svc/grafana-service 3000:3000
# Open: http://localhost:3000
# Default credentials: admin / change-me-in-production

# Jaeger
kubectl port-forward -n kloud svc/jaeger-service 16686:16686
# Open: http://localhost:16686
```

## Step 5: Configure Custom Domain

### DNS Configuration

```bash
# Get Ingress IP
kubectl get ingress -n kloud -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}'

# Add DNS records
# kloud.com        A  <IP>
# *.kloud.com      A  <IP>
# api.kloud.com    A  <IP>
# app.kloud.com    A  <IP>
```

### SSL Certificate

```bash
# Check certificate status
kubectl get certificate -n kloud

# View certificate details
kubectl describe certificate kloud-cert -n kloud

# Verify SSL
curl -v https://api.kloud.com/health

# Expected: HTTP/2 200 with valid SSL certificate
```

## Step 6: Backup & Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it -n kloud postgres-0 -- pg_dump -U kloud kloud_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore from backup
gunzip < backup.sql.gz | kubectl exec -i -n kloud postgres-0 -- psql -U kloud kloud_db
```

### PersistentVolume Backup

```bash
# Backup all PVCs
for pvc in $(kubectl get pvc -n kloud -o jsonpath='{.items[*].metadata.name}'); do
  echo "Backing up $pvc..."
  kubectl get pvc $pvc -n kloud -o yaml > pvc_$pvc.yaml
done

# Backup PV data (requires direct access to cluster nodes)
```

## Step 7: Scaling & Performance

### Scale Deployments

```bash
# Scale API
kubectl scale deployment kloud-api -n kloud --replicas=5

# Watch scaling
kubectl get deployment -n kloud -w

# Scale with HPA (automatic)
kubectl apply -f k8s/hpa.yaml
kubectl get hpa -n kloud
```

### Resource Management

```bash
# View resource usage
kubectl top nodes
kubectl top pods -n kloud

# Edit resource limits
kubectl edit deployment kloud-api -n kloud

# Example limits:
# requests:
#   cpu: 100m
#   memory: 256Mi
# limits:
#   cpu: 500m
#   memory: 1Gi
```

### Database Optimization

```bash
# Connect to PostgreSQL
kubectl exec -it -n kloud postgres-0 -- psql -U kloud -d kloud_db

# Analyze tables
ANALYZE;

# View slow queries
SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

# Vacuum
VACUUM ANALYZE;
```

## Step 8: Monitoring & Alerts

### View Metrics

```bash
# Prometheus queries
# CPU usage: rate(container_cpu_usage_seconds_total{namespace="kloud"}[5m])
# Memory usage: container_memory_usage_bytes{namespace="kloud"}
# HTTP requests: rate(http_requests_total{namespace="kloud"}[1m])

# View in Prometheus UI
kubectl port-forward -n kloud svc/prometheus-service 9090:9090
# Open: http://localhost:9090
```

### Configure Alerts

```bash
# Edit AlertManager config
kubectl edit configmap alertmanager -n kloud

# Add notification channels (Slack, PagerDuty, etc.)
# Example:
# route:
#   receiver: 'slack'
# receivers:
#   - name: 'slack'
#     slack_configs:
#       - api_url: 'YOUR_SLACK_WEBHOOK'
#         channel: '#kloud-alerts'
```

### Log Aggregation

```bash
# Access Kibana for logs
kubectl port-forward -n kloud svc/elasticsearch-service 9200:9200
kubectl port-forward -n kloud svc/kibana-service 5601:5601
# Open: http://localhost:5601
```

## Step 9: Troubleshooting

### Common Issues

```bash
# Pods not starting
kubectl describe pod <pod-name> -n kloud
kubectl logs <pod-name> -n kloud

# ImagePullBackOff error
# - Check image name and registry
# - Verify image pull secret
# - Ensure docker credentials are correct

# CrashLoopBackOff
# - Check pod logs
# - Verify environment variables
# - Check resource limits
# - Verify database connectivity

# Ingress not working
kubectl describe ingress kloud-ingress -n kloud
kubectl get ingress -n kloud -o yaml

# Check Nginx logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Debugging

```bash
# Get detailed events
kubectl get events -n kloud --sort-by='.lastTimestamp'

# Describe resources
kubectl describe node
kubectl describe pvc -n kloud
kubectl describe pv

# Execute commands in pod
kubectl exec -it <pod> -n kloud -- /bin/bash

# Port forward to local
kubectl port-forward pod/<pod> 8000:8000 -n kloud
```

## Step 10: Updates & Rollouts

### Rolling Update

```bash
# Update image
kubectl set image deployment/kloud-api kloud-api=$REGISTRY/kloud-api:2.0.0 -n kloud

# Watch rollout
kubectl rollout status deployment/kloud-api -n kloud

# Rollback if needed
kubectl rollout undo deployment/kloud-api -n kloud
kubectl rollout undo deployment/kloud-api -n kloud --to-revision=1
```

### View Deployment History

```bash
# History
kubectl rollout history deployment/kloud-api -n kloud

# Details of specific revision
kubectl rollout history deployment/kloud-api -n kloud --revision=2
```

## Production Checklist

- [ ] Update all secrets (JWT_SECRET_KEY, database passwords, etc.)
- [ ] Configure custom domain and DNS
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Enable monitoring (Prometheus, Grafana)
- [ ] Configure alerts (Slack, PagerDuty)
- [ ] Set up backups (automated daily)
- [ ] Enable logging (Elasticsearch, Kibana)
- [ ] Configure rate limiting
- [ ] Set resource requests/limits
- [ ] Enable network policies
- [ ] Set up RBAC properly
- [ ] Test failover scenarios
- [ ] Document runbooks
- [ ] Train team members

## Maintenance

### Regular Tasks

```bash
# Check pod status daily
kubectl get pods -n kloud -w

# Monitor resource usage
kubectl top pods -n kloud

# Check certificate expiration
kubectl get certificate -n kloud

# Review logs
kubectl logs -n kloud --all-containers=true -l app=kloud-api --tail=100
```

### Cleanup

```bash
# Remove old pods
kubectl delete pod <pod-name> -n kloud

# Prune old images
docker image prune -a

# Clean up old deployments
kubectl delete deployment <old-deployment> -n kloud
```

## Advanced Topics

### StatefulSet Scaling

```bash
# Scale PostgreSQL with replication
kubectl edit statefulset postgres -n kloud
# Change replicas from 1 to 3
# Automatic replication will be configured
```

### Network Policies

```bash
# View applied policies
kubectl get networkpolicies -n kloud

# Create custom policy
kubectl create networkpolicy allow-api \
  --selector=app=kloud-api \
  --ingress-namespace=ingress-nginx
```

### Custom Metrics

```bash
# Define custom metrics for HPA
kubectl apply -f - << EOF
apiVersion: autoscaling.custom.metrics.k8s.io/v1beta1
kind: ExternalMetric
metadata:
  name: requests_per_second
  namespace: kloud
spec:
  selector:
    matchLabels:
      metric: rps
EOF
```

---

## Support & Resources

- Kubernetes Docs: https://kubernetes.io/docs/
- Helm Docs: https://helm.sh/docs/
- Kubectl Cheatsheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

## Contact

For deployment issues, contact: devops@kloud.com

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintainer**: Kloud DevOps Team

