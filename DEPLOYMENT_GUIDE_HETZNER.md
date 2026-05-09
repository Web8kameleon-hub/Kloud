# Kloud Cloud - Hetzner Deployment Guide

**Server Provider:** Hetzner Cloud (console.hetzner.com)  
**Account:** K1266374525 (amati.ledian@gmail.com)  
**Domain:** kloud.com (managed via STRATO)  
**Date:** December 11, 2025

---

## 📋 Deployment Checklist

### Phase 1: GitHub Repository (5 min)
- [ ] Push code to GitHub
- [ ] Verify all workflows pass
- [ ] Tag release v1.0.0

### Phase 2: Hetzner Server Setup (15 min)
- [ ] Create Cloud Server
- [ ] Configure SSH access
- [ ] Install Docker & dependencies

### Phase 3: DNS Configuration (10 min)
- [ ] Point kloud.com to server IP
- [ ] Configure SSL certificate
- [ ] Set up CDN (optional)

### Phase 4: Application Deployment (20 min)
- [ ] Clone repository
- [ ] Configure environment
- [ ] Deploy Docker containers
- [ ] Deploy Next.js frontend

### Phase 5: Verification (10 min)
- [ ] Test API endpoints
- [ ] Verify monitoring
- [ ] Check billing integration

**Total Time:** ~60 minutes

---

## 🚀 Step-by-Step Deployment

### STEP 1: Push to GitHub

```powershell
# From C:\kloud-cloud
git push origin main

# Tag the release
git tag -a v1.0.0 -m "Kloud Cloud v1.0 - Production Release"
git push origin v1.0.0
```

---

### STEP 2: Create Hetzner Cloud Server

**Login:** https://console.hetzner.com  
**Account:** K1266374525

#### 2.1 Server Configuration

```
Name: kloud-prod-01
Location: Falkenstein, Germany (eu-central)
Image: Ubuntu 24.04 LTS
Type: CX32 (4 vCPU, 8 GB RAM, 80 GB SSD)
Networking: IPv4 + IPv6
SSH Key: Add your public key
Firewall: Create new
```

**Monthly Cost:** ~€8.21

#### 2.2 Firewall Rules

```
Inbound:
- SSH (22) - Your IP only
- HTTP (80) - 0.0.0.0/0
- HTTPS (443) - 0.0.0.0/0
- Prometheus (9090) - Your IP only
- Grafana (3001) - Your IP only
- API (8000) - 0.0.0.0/0

Outbound:
- All traffic allowed
```

#### 2.3 Initial Server Setup

```bash
# SSH to server (get IP from Hetzner Console)
ssh root@YOUR_SERVER_IP

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Install Node.js 24.x
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs

# Install Python 3.13
add-apt-repository ppa:deadsnakes/ppa -y
apt install python3.13 python3.13-venv python3-pip -y

# Install Nginx
apt install nginx certbot python3-certbot-nginx -y

# Install Git
apt install git -y

# Create deployment user
adduser kloud --disabled-password --gecos ""
usermod -aG docker kloud
```

---

### STEP 3: Configure DNS (STRATO)

**Login:** https://www.strato.de/apps/CustomerService  
**Domain:** kloud.com

#### 3.1 DNS Records

Navigate to: **Domains → kloud.com → DNS Settings**

```
Type    Name    Value                   TTL
A       @       YOUR_HETZNER_IP         3600
A       www     YOUR_HETZNER_IP         3600
A       api     YOUR_HETZNER_IP         3600
CNAME   grafana YOUR_HETZNER_IP         3600
CNAME   prometheus YOUR_HETZNER_IP      3600
```

**Wait:** 5-30 minutes for DNS propagation

**Verify:**
```powershell
nslookup kloud.com
```

---

### STEP 4: Deploy Application

#### 4.1 Clone Repository

```bash
# As kloud user
su - kloud

# Clone repo
git clone https://github.com/LedjanAhmati/Kloud-cloud.git
cd Kloud-cloud
```

#### 4.2 Configure Environment

```bash
# Create production .env
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://kloud:SECURE_PASSWORD@localhost:5432/kloud_prod
REDIS_URL=redis://localhost:6379/0

# API
API_SECRET_KEY=GENERATE_WITH_openssl_rand_hex_32
API_ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000

# Stripe (Get from dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Frontend
NEXT_PUBLIC_API_URL=https://kloud.com/api
NEXT_PUBLIC_DOMAIN=kloud.com

# Monitoring
PROMETHEUS_RETENTION=15d
GRAFANA_ADMIN_PASSWORD=SECURE_PASSWORD

# Email (Optional - for notifications)
SMTP_HOST=smtp.strato.de
SMTP_PORT=465
SMTP_USER=info@kloud.com
SMTP_PASSWORD=YOUR_EMAIL_PASSWORD
EOF

# Generate secure keys
openssl rand -hex 32  # Use for API_SECRET_KEY
```

#### 4.3 Deploy Docker Services

```bash
# Build and start containers
docker compose up -d postgres redis prometheus grafana

# Wait 10 seconds for databases
sleep 10

# Run database migrations (if any)
# python apps/api/migrations.py

# Start backend services
docker compose up -d api alba albi jona master

# Check logs
docker compose logs -f --tail=100
```

#### 4.4 Deploy Next.js Frontend

```bash
# Install dependencies
cd apps/web
npm install

# Build production
npm run build

# Start with PM2 (process manager)
npm install -g pm2
pm2 start npm --name "kloud-web" -- start
pm2 save
pm2 startup
```

---

### STEP 5: Configure Nginx Reverse Proxy

```bash
# As root
sudo su

cat > /etc/nginx/sites-available/kloud << 'EOF'
server {
    listen 80;
    server_name kloud.com www.kloud.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Grafana
    location /grafana/ {
        proxy_pass http://localhost:3001/;
        proxy_set_header Host $host;
    }
    
    # Prometheus
    location /prometheus/ {
        proxy_pass http://localhost:9090/;
        proxy_set_header Host $host;
        auth_basic "Prometheus";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/kloud /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

### STEP 6: Configure SSL Certificate

```bash
# Install Let's Encrypt certificate
certbot --nginx -d kloud.com -d www.kloud.com

# Auto-renewal (runs twice daily)
systemctl status certbot.timer

# Test renewal
certbot renew --dry-run
```

---

### STEP 7: Verification

#### 7.1 Test Endpoints

```bash
# Frontend
curl https://kloud.com
# Should return Next.js homepage

# Backend API
curl https://kloud.com/api/health
# Should return {"status": "healthy"}

# ALBA Service
curl https://kloud.com/api/alba/status
# Should return ALBA agent status

# Swagger Docs
open https://kloud.com/api/docs
```

#### 7.2 Monitoring

```
Grafana: https://kloud.com/grafana
Prometheus: https://kloud.com/prometheus (password protected)
```

#### 7.3 SSL Check

```
https://www.ssllabs.com/ssltest/analyze.html?d=kloud.com
```

---

## 🔧 Post-Deployment

### Configure Automated Backups

```bash
# Database backup script
cat > /home/kloud/backup.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump -U kloud kloud_prod > /backups/db_$TIMESTAMP.sql
find /backups -name "db_*.sql" -mtime +7 -delete
EOF

chmod +x /home/kloud/backup.sh

# Cron: Daily at 2 AM
crontab -e
0 2 * * * /home/kloud/backup.sh
```

### Set Up Monitoring Alerts

```bash
# Configure Alertmanager
# Edit docker-compose.yml to add alertmanager service
# Configure Slack/Email notifications
```

### Enable Log Rotation

```bash
# Configure Docker log limits
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

systemctl restart docker
```

---

## 📊 Production URLs

After deployment, these URLs will be live:
```

---

## 💰 Cost Breakdown

### Hetzner Cloud

- **CX32 Server:** €8.21/month
- **Bandwidth:** 20TB included
- **Backups (optional):** +20% (+€1.64/month)

### STRATO

- **kloud.com domain:** Included
- **Email:** 4 mailboxes included

### Third-Party Services

- **Stripe:** 1.4% + €0.25 per transaction
- **Monitoring:** Free (self-hosted)

**Total Monthly Cost:** ~€10-15

---

## 🚨 Troubleshooting

### Service Won't Start

```bash
# Check Docker logs
docker compose logs [service_name]

# Restart service
docker compose restart [service_name]

# Check ports
netstat -tulpn | grep LISTEN
```

### DNS Not Resolving

```bash
# Check DNS propagation
dig kloud.com
nslookup kloud.com 8.8.8.8

# Force DNS refresh
systemctl restart systemd-resolved
```

### SSL Certificate Issues

```bash
# Check certificate
certbot certificates

# Force renewal
certbot renew --force-renewal

# Nginx config test
nginx -t
```

### Database Connection Errors

```bash
# Check PostgreSQL
docker compose exec postgres psql -U kloud -d kloud_prod

# Check Redis
docker compose exec redis redis-cli ping
```

---

## 📞 Support Contacts

**Hetzner Support:** <support@hetzner.com>  
**STRATO Support:** <https://www.strato.de/kontakt>

**Kloud SRE Team:** (your internal team contact)

---

## ✅ Deployment Complete

After completing all steps:

1. ✅ Code pushed to GitHub
2. ✅ Server provisioned on Hetzner
3. ✅ DNS configured via STRATO
4. ✅ SSL certificate installed
5. ✅ Docker services running
6. ✅ Frontend deployed
7. ✅ Monitoring active
8. ✅ Backups configured

**Platform is LIVE at:** <https://kloud.com> 🚀

---

**Deployed:** December 11, 2025  
**Version:** v1.0.0  
**Environment:** Production

