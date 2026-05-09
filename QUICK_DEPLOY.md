# 🚀 Kloud Cloud - Deployment Quick Start

**Target:** Hetzner Cloud + STRATO DNS  
**Domain:** kloud.com  
**Estimated Time:** 30 minutes  
**Last Updated:** December 12, 2025

---

## ⚡ Fast Deployment (3 Simple Steps)

### **Step 1: Create Hetzner Server (5 min)**

1. Login: https://console.hetzner.com (Account: K1266374525)
2. Create new server:
   ```
   Name: kloud-prod
   Location: Falkenstein, Germany
   Image: Ubuntu 24.04 LTS
   Type: CX32 (4 vCPU, 8GB RAM) - €8.21/month
   SSH Key: Add your public key
   ```
3. Note the server IP: `___.___.___.___ `

---

### **Step 2: Configure DNS (5 min)**

1. Login: https://www.strato.de/apps/CustomerService
2. Go to: **Domains → kloud.com → DNS Settings**
3. Add A Records:
   ```
   @ → [YOUR_HETZNER_IP]
   www → [YOUR_HETZNER_IP]
   api → [YOUR_HETZNER_IP]
   grafana → [YOUR_HETZNER_IP]
   ```
4. Save and wait 5-30 minutes for DNS propagation

---

### **Step 3: Deploy Platform (20 min)**

SSH to server and run ONE command:

```bash
curl -fsSL https://raw.githubusercontent.com/LedjanAhmati/Kloud-cloud/main/deploy-hetzner.sh | bash
```

This will:
- ✅ Install Docker & dependencies
- ✅ Clone repository
- ✅ Generate secure secrets automatically
- ✅ Create production configuration
- ✅ Set up firewall

---

## 🔐 Post-Deployment Setup

### **1. Install SSL Certificates**

After DNS propagation, run:

```bash
cd /opt/kloud

# Install certbot
apt install -y certbot

# Get certificates (do this AFTER DNS works!)
certbot certonly --standalone \
  -d kloud.com \
  -d www.kloud.com \
  -d api.kloud.com \
  --email amati.ledian@gmail.com \
  --agree-tos --non-interactive

# Certificates will be at:
# /etc/letsencrypt/live/kloud.com/fullchain.pem
# /etc/letsencrypt/live/kloud.com/privkey.pem
```

### **2. Start the Platform**

```bash
cd /opt/kloud

# Start all services
docker compose -f docker-compose.prod.yml up -d --build

# Monitor startup
docker compose -f docker-compose.prod.yml logs -f
```

### **3. View Your Credentials**

```bash
cat /opt/kloud/.credentials.txt
```

**⚠️ IMPORTANT:** Copy these credentials to your password manager, then delete the file:
```bash
rm /opt/kloud/.credentials.txt
```

---

## ✅ Verify Deployment

### **Check Services**

```bash
cd /opt/kloud

# View running containers
docker compose -f docker-compose.prod.yml ps

# Check service health
docker compose -f docker-compose.prod.yml exec api curl http://localhost:8000/health
docker compose -f docker-compose.prod.yml exec alba curl http://localhost:5555/health
docker compose -f docker-compose.prod.yml exec albi curl http://localhost:6666/health
```

### **Test Endpoints**

Once DNS and SSL are ready:

```bash
# Frontend
curl -I https://kloud.com

# API
curl https://api.kloud.com/health

# Grafana Dashboard
curl -I https://kloud.com:3001
```

---

## 📊 Access Your Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Website** | https://kloud.com | Public |
| **API** | https://api.kloud.com | API Key required |
| **Grafana** | https://kloud.com:3001 | See `.credentials.txt` |
| **Prometheus** | http://SERVER_IP:9090 | No auth (firewall protected) |
| **Kibana** | http://SERVER_IP:5601 | elastic / See credentials |

---

## 🔧 Common Commands

### **View Logs**
```bash
cd /opt/kloud

# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.prod.yml logs -f alba
docker compose -f docker-compose.prod.yml logs -f nginx
```

### **Restart Services**
```bash
# Restart everything
docker compose -f docker-compose.prod.yml restart

# Restart specific service
docker compose -f docker-compose.prod.yml restart api
```

### **Update Code**
```bash
cd /opt/kloud

# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build
```

### **Check Resource Usage**
```bash
# Container stats
docker stats

# Disk usage
df -h
docker system df
```

---

## 🛡️ Security Checklist

- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall (UFW) enabled and configured
- [ ] Strong database passwords generated
- [ ] `.credentials.txt` deleted after saving
- [ ] Grafana admin password changed
- [ ] SSH key-only authentication enabled
- [ ] Regular backups configured

---

## 🆘 Troubleshooting

### **DNS Not Working**
```bash
# Check DNS propagation
nslookup kloud.com
dig kloud.com

# Wait up to 30 minutes for global propagation
```

### **SSL Certificate Fails**
```bash
# Make sure DNS is working first!
nslookup kloud.com

# Port 80 must be open
ufw status

# Stop nginx temporarily if needed
docker compose -f docker-compose.prod.yml stop nginx
certbot certonly --standalone -d kloud.com -d www.kloud.com
docker compose -f docker-compose.prod.yml start nginx
```

### **Service Won't Start**
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs [service-name]

# Check resource usage
docker stats
df -h

# Restart Docker daemon
systemctl restart docker
```

### **Database Connection Error**
```bash
# Check if postgres is running
docker compose -f docker-compose.prod.yml ps postgres

# Check logs
docker compose -f docker-compose.prod.yml logs postgres

# Restart postgres
docker compose -f docker-compose.prod.yml restart postgres
```

---

## 📈 Next Steps

1. **Configure Stripe** - Add your Stripe keys to `.env.production`
2. **Set up Monitoring Alerts** - Configure Grafana alerting
3. **Enable Backups** - Set up automated PostgreSQL backups
4. **Custom Domain Email** - Configure SMTP for email notifications
5. **Slack Integration** - Add Slack webhook for monitoring alerts

---

## 📞 Support

- **Documentation:** Check `DEPLOYMENT_GUIDE_HETZNER.md` for detailed info
- **Logs Location:** `/opt/kloud/logs/`
- **Data Location:** `/opt/kloud/data/`

---

## 🎉 You're Live!

Your Kloud Cloud platform is now running in production on Hetzner!

**Next:** Visit https://kloud.com and start using your platform.

