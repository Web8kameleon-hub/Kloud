# 🚀 KLOUD CLOUD - HETZNER DEPLOYMENT GUIDE

**Status**: Production Ready
**Target Server**: 157.90.234.158
**Domain**: kloud.com
**SSL**: Let's Encrypt

---

## ✅ PRE-DEPLOYMENT CHECKLIST

- [x] Code pushed to GitHub (main branch)
- [x] Docker images tested locally
- [x] PostgreSQL verified (5432)
- [x] Redis verified (6379)
- [x] DNS configured (A: 157.90.234.158)
- [x] DNSSEC enabled
- [x] Domain Guard enabled
- [x] All subdomains configured (www, api)

---

## 📋 DEPLOYMENT STEPS

### STEP 1: Connect to Hetzner Server
\\\ash
ssh root@157.90.234.158
\\\

### STEP 2: Install Dependencies
\\\ash
apt update && apt upgrade -y
apt install -y docker.io docker-compose git curl wget nginx certbot python3-certbot-nginx
\\\

### STEP 3: Clone Repository
\\\ash
cd /opt && git clone https://github.com/LedjanAhmati/Kloud-cloud.git kloud && cd kloud
\\\

### STEP 4: Create Production Environment
\\\ash
cat > .env << 'ENVEOF'
POSTGRES_USER=kloud
POSTGRES_PASSWORD=<GENERATE_SECURE_32_CHAR_PASSWORD>
POSTGRES_DB=klouddb
REDIS_PASSWORD=<GENERATE_SECURE_32_CHAR_PASSWORD>
API_ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
STRIPE_SECRET_KEY=<YOUR_STRIPE_SECRET_KEY>
STRIPE_PUBLISHABLE_KEY=<YOUR_STRIPE_PUBLISHABLE_KEY>
NEXT_PUBLIC_API_URL=https://api.kloud.com
GRAFANA_ADMIN_PASSWORD=<GENERATE_SECURE_32_CHAR_PASSWORD>
ENVEOF
\\\

### STEP 5: Start Docker Services
\\\ash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
\\\

### STEP 6: Setup SSL Certificate
\\\ash
certbot certonly --standalone -d kloud.com -d www.kloud.com -d api.kloud.com
\\\

### STEP 7: Configure Nginx
\\\ash
# Create nginx config with HTTP->HTTPS redirect and proxy rules
# Frontend proxy to 3000, API proxy to 8000, Grafana to 3001
\\\

### STEP 8: Test Endpoints
\\\ash
curl https://kloud.com
curl https://api.kloud.com/health
\\\

---

## 🎯 LIVE SYSTEM ACCESS

| Service | URL |
|---------|-----|
| Frontend | https://kloud.com |
| API Docs | https://api.kloud.com/docs |
| Grafana | https://kloud.com/grafana |
| Prometheus | https://kloud.com/prometheus |

---

## ✅ DEPLOYMENT SUCCESS CHECKLIST

- [ ] SSH connection successful
- [ ] Dependencies installed
- [ ] Repository cloned to /opt/kloud
- [ ] .env file created with secure passwords
- [ ] Docker containers running (18 services)
- [ ] PostgreSQL healthy
- [ ] Redis responsive
- [ ] SSL certificates generated
- [ ] Nginx reverse proxy configured
- [ ] HTTPS endpoints responding 200 OK
- [ ] Frontend loads at https://kloud.com
- [ ] Chat feature working
- [ ] Grafana accessible
- [ ] Prometheus metrics collected

---

**Kloud Cloud in Production!**
**Hetzner Deployment: Ready to Launch**

