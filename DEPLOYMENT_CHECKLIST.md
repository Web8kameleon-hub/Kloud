# Kloud Cloud - Production Deployment Checklist

**Target:** Hetzner + STRATO  
**Domain:** kloud.com  
**Date:** December 11, 2025

---

## ✅ PRE-DEPLOYMENT CHECKLIST

### Local Preparation

- [x] Code committed to GitHub
- [ ] Docker images tested locally
- [ ] Environment variables prepared
- [ ] SSL strategy confirmed
- [ ] Backup strategy defined

### Hetzner Account

- [x] Account created (K1266374525)
- [ ] Payment method added
- [ ] SSH key prepared
- [ ] Project created ("Kloud Cloud")

### STRATO Account

- [x] Domain registered (kloud.com)
- [x] Account accessible
- [ ] DNS management enabled
- [ ] Email forwarding configured (optional)

---

## 🚀 DEPLOYMENT STEPS (30 minutes)

### Phase 1: Create Hetzner Server (5 min)

1. [ ] Login to <https://console.hetzner.com>
2. [ ] Create new project: "Kloud Cloud"
3. [ ] Create server:
   - Location: **Falkenstein (FSN1)**
   - Image: **Ubuntu 22.04 LTS**
   - Type: **CX22** (4 vCPU, 8GB RAM, 80GB SSD)
   - SSH Key: **Add yours**
4. [ ] Note server IP: `___.___.___.___`
5. [ ] Wait for server ready (~1 min)

**Cost:** ~€5.83/month

---

### Phase 2: Configure DNS at STRATO (10 min)

1. [ ] Login to <https://www.strato.de/apps/CustomerService>
2. [ ] Go to Domains → kloud.com → DNS Settings
3. [ ] Add A Records:

   ```
   @ → [HETZNER_IP]
   www → [HETZNER_IP]
   api → [HETZNER_IP]
   grafana → [HETZNER_IP] (optional)
   ```

4. [ ] Delete old STRATO hosting records
5. [ ] Save changes
6. [ ] Verify with: `nslookup kloud.com`

**Wait time:** 5-30 minutes for DNS propagation

---

### Phase 3: Deploy Platform (10 min)

1. [ ] SSH into server: `ssh root@[HETZNER_IP]`
2. [ ] Run deployment script:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/LedjanAhmati/Kloud-cloud/main/deploy-hetzner.sh | bash
   ```

3. [ ] Wait for installation (~5 min)
4. [ ] Verify Docker: `docker --version`
5. [ ] Check services: `cd /opt/kloud && ls -la`

---

### Phase 4: Install SSL Certificates (5 min)

**After DNS propagation:**

1. [ ] Stop nginx temporarily:

   ```bash
   cd /opt/kloud
   docker compose -f docker-compose.production.yml stop nginx
   ```

2. [ ] Install certbot:

   ```bash
   apt install -y certbot
   ```

3. [ ] Get certificates:

   ```bash
   certbot certonly --standalone -d kloud.com -d www.kloud.com \
     --email amati.ledian@gmail.com --agree-tos --non-interactive
   
   certbot certonly --standalone -d api.kloud.com \
     --email amati.ledian@gmail.com --agree-tos --non-interactive
   ```

4. [ ] Verify certificates:

   ```bash
   ls -la /etc/letsencrypt/live/kloud.com/
   ls -la /etc/letsencrypt/live/api.kloud.com/
   ```

5. [ ] Start all services:

   ```bash
   cd /opt/kloud
   docker compose -f docker-compose.production.yml up -d --build
   ```

---

### Phase 5: Verify Deployment (5 min)

1. [ ] Check running containers:

   ```bash
   docker ps
   ```

   Expected: 7 containers (api, web, nginx, postgres, redis, prometheus, grafana)

2. [ ] Check logs:

   ```bash
   docker compose logs -f --tail=50
   ```

3. [ ] Test endpoints:
   - [ ] <https://kloud.com> (Frontend)
   - [ ] <https://www.kloud.com> (Frontend)
   - [ ] <https://api.kloud.com/health> (API health)
   - [ ] <https://api.kloud.com/docs> (API documentation)

4. [ ] Test SSL:

   ```bash
   curl -I https://kloud.com
   curl -I https://api.kloud.com/health
   ```

5. [ ] Check monitoring:
   - [ ] http://[HETZNER_IP]:9090 (Prometheus)
   - [ ] http://[HETZNER_IP]:3001 (Grafana)

---

## 🔐 POST-DEPLOYMENT SECURITY

### Immediate Actions

- [ ] Change default Grafana password:

  ```bash
  docker exec -it kloud_grafana grafana-cli admin reset-admin-password NEW_PASSWORD
  ```

- [ ] Configure PostgreSQL password:

  ```bash
  # Edit .env.production
  nano /opt/kloud/.env.production
  # Set: DATABASE_PASSWORD=SECURE_PASSWORD
  docker compose -f docker-compose.production.yml restart postgres
  ```

- [ ] Add Stripe production keys:

  ```bash
  nano /opt/kloud/.env.production
  # Add: STRIPE_SECRET_KEY=sk_live_...
  # Add: STRIPE_PUBLISHABLE_KEY=pk_live_...
  docker compose -f docker-compose.production.yml restart api
  ```

- [ ] Disable root SSH login:

  ```bash
  # Create non-root user
  adduser kloud
  usermod -aG sudo kloud
  
  # Disable root SSH
  nano /etc/ssh/sshd_config
  # Set: PermitRootLogin no
  systemctl restart sshd
  ```

### Within 24 Hours

- [ ] Set up automated backups (PostgreSQL + Redis)
- [ ] Configure log rotation
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure Cloudflare (optional - CDN + DDoS protection)
- [ ] Set up error tracking (Sentry)
- [ ] Configure email notifications (alerts)

---

## 📊 MONITORING DASHBOARD

### Grafana Setup

1. [ ] Access: http://[HETZNER_IP]:3001
2. [ ] Login: admin / [configured password]
3. [ ] Add Prometheus data source:
   - URL: `http://prometheus:9090`
4. [ ] Import dashboards:
   - Node Exporter (ID: 1860)
   - Docker (ID: 893)
   - FastAPI (custom)

### Prometheus Targets

Verify all targets are UP:

- http://[HETZNER_IP]:9090/targets

Expected targets:

- API metrics: `http://api:8000/metrics`
- Node exporter: `http://node-exporter:9100/metrics`

---

## 🧪 TESTING CHECKLIST

### Frontend Tests

- [ ] Homepage loads
- [ ] Navigation works
- [ ] Forms submit
- [ ] API calls succeed
- [ ] Assets load (images, CSS, JS)
- [ ] Mobile responsive

### API Tests

- [ ] Health endpoint: `/health`
- [ ] OpenAPI docs: `/docs`
- [ ] Authentication works
- [ ] Database queries execute
- [ ] Redis caching works
- [ ] Stripe webhooks receive events

### Performance Tests

- [ ] Page load time < 2s
- [ ] API response time < 500ms
- [ ] WebSockets connect
- [ ] No memory leaks
- [ ] CPU usage < 50%

---

## 🆘 ROLLBACK PLAN

If deployment fails:

1. **Stop all containers:**

   ```bash
   cd /opt/kloud
   docker compose -f docker-compose.production.yml down
   ```

2. **Restore previous version:**

   ```bash
   git checkout [PREVIOUS_COMMIT]
   docker compose -f docker-compose.production.yml up -d --build
   ```

3. **Point DNS back to STRATO:**
   - Remove A records
   - Add CNAME: `kloud.com → 570523285.swh.strato-hosting.eu`

4. **Investigate logs:**

   ```bash
   docker compose logs > deployment-error.log
   ```

---

## 📞 SUPPORT CONTACTS

**Hetzner Support:**

- Web: <https://console.hetzner.com>
- Email: <support@hetzner.com>
- Phone: +49 (0)9831 505-0

**STRATO Support:**

- Web: <https://www.strato.de/faq>
- Phone: 030 300 146 000

**DNS Check Tools:**

- <https://www.whatsmydns.net>
- <https://dnschecker.org>
- <https://mxtoolbox.com>

---

## ✅ COMPLETION CRITERIA

Deployment is successful when:

- ✅ All 7 containers running
- ✅ HTTPS works on all domains
- ✅ Frontend loads correctly
- ✅ API responds to requests
- ✅ Database accepts connections
- ✅ Monitoring shows green metrics
- ✅ No error logs in last 5 minutes
- ✅ SSL certificates valid for 90 days
- ✅ DNS propagated globally
- ✅ Backup system configured

---

**Status:** 🟡 Ready to Deploy  
**Next Action:** Create Hetzner server and note IP address  
**Estimated Total Time:** 30-60 minutes  
**Est. Monthly Cost:** €5.83 (CX22 server) + €1.40 (domain)
