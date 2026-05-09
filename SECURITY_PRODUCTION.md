# 🔐 Kloud Cloud - Production Security Guide

**Last Updated:** December 12, 2025  
**Environment:** Hetzner Cloud Production

---

## ✅ Security Improvements Implemented

### **1. Nginx Reverse Proxy**
- ✅ SSL/TLS termination with Let's Encrypt
- ✅ Rate limiting (API: 10 req/s, Web: 30 req/s)
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Gzip compression
- ✅ HTTP → HTTPS redirect

### **2. Secure Environment Variables**
- ✅ Auto-generated secrets using `openssl rand`
- ✅ No hardcoded passwords in code
- ✅ `.env.production.template` for safe sharing
- ✅ Credentials saved in protected file (chmod 600)

### **3. Docker Security**
- ✅ Health checks on all critical services
- ✅ Container restart policies
- ✅ Network isolation (`kloud-network`)
- ✅ Volume permissions
- ✅ Non-root users where possible

### **4. Database Security**
- ✅ Strong auto-generated passwords
- ✅ Internal network-only access
- ✅ Connection pooling limits
- ✅ SSL connections (configurable)

### **5. Firewall Configuration**
- ✅ UFW enabled
- ✅ Only necessary ports open:
  - 22 (SSH - key only)
  - 80, 443 (HTTP/HTTPS)
  - 8000 (API - internal only via nginx)
  - 9090, 3001 (Monitoring - IP restricted)

---

## 🛡️ Additional Security Recommendations

### **1. SSH Hardening**

```bash
# Disable password authentication
nano /etc/ssh/sshd_config

# Set these values:
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin prohibit-password
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Restart SSH
systemctl restart sshd
```

### **2. Fail2Ban Setup**

```bash
# Install fail2ban
apt install -y fail2ban

# Create SSH jail
cat > /etc/fail2ban/jail.local <<EOF
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 600
EOF

# Start fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### **3. SSL Auto-Renewal**

```bash
# Test renewal
certbot renew --dry-run

# Auto-renewal is enabled by default via cron
# Check with:
systemctl status certbot.timer

# Manual renewal if needed:
certbot renew
docker compose -f /opt/kloud/docker-compose.prod.yml restart nginx
```

### **4. Database Backups**

```bash
# Create backup script
cat > /opt/kloud/backup-db.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/kloud/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose -f /opt/kloud/docker-compose.prod.yml exec -T postgres \
  pg_dump -U kloud_prod klouddb | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
EOF

chmod +x /opt/kloud/backup-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/kloud/backup-db.sh") | crontab -
```

### **5. Docker Security Audit**

```bash
# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image kloud-api:latest

# Check container resource limits
docker stats --no-stream

# Review security settings
docker inspect kloud-api | grep -A 20 SecurityOpt
```

### **6. Monitoring & Alerts**

Enable alerts in Grafana:
1. Go to https://kloud.com:3001
2. Navigate to **Alerting → Alert Rules**
3. Create alerts for:
   - High CPU/Memory usage (>80%)
   - Database connection errors
   - API response time (>5s)
   - Disk space (>90%)
   - Service downtime

### **7. Rate Limiting Enhancement**

Already configured in `nginx.conf`:
- API: 10 requests/second (burst: 10)
- Web: 30 requests/second (burst: 20)

To modify, edit `/opt/kloud/nginx/nginx.conf` and restart nginx.

### **8. Secret Rotation Schedule**

Rotate these every 90 days:
- Database passwords
- JWT secrets
- API keys
- Grafana admin password

```bash
# Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# Update .env.production
nano /opt/kloud/.env.production

# Restart services
cd /opt/kloud
docker compose -f docker-compose.prod.yml restart
```

---

## 🚨 Security Incident Response

### **If Credentials Leaked:**

1. **Immediate Actions:**
   ```bash
   # Rotate all secrets
   cd /opt/kloud
   
   # Generate new secrets
   openssl rand -hex 32  # Use for SECRET_KEY
   openssl rand -hex 32  # Use for JWT_SECRET_KEY
   openssl rand -hex 16  # Use for API_KEY
   
   # Update .env.production
   nano .env.production
   
   # Restart all services
   docker compose -f docker-compose.prod.yml restart
   ```

2. **Check for unauthorized access:**
   ```bash
   # Review nginx access logs
   tail -n 1000 /var/log/nginx/access.log | grep -v "200\|301\|304"
   
   # Check database connections
   docker compose exec postgres psql -U kloud_prod -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Notify users** if data breach suspected

### **If Server Compromised:**

1. **Isolate server** (block all traffic except your IP)
2. **Take snapshot** of server for forensics
3. **Deploy fresh server** from clean backup
4. **Rotate ALL credentials**
5. **Review security logs**

---

## 📋 Security Checklist (Monthly)

```bash
# Run this monthly security check
cat > /opt/kloud/security-check.sh <<'EOF'
#!/bin/bash
echo "════════════════════════════════════════════════════════════"
echo "KLOUD CLOUD - MONTHLY SECURITY CHECK"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "[1/8] Checking system updates..."
apt list --upgradable

echo ""
echo "[2/8] SSL certificate expiry..."
certbot certificates

echo ""
echo "[3/8] Checking open ports..."
ss -tuln | grep LISTEN

echo ""
echo "[4/8] Failed login attempts..."
grep "Failed password" /var/log/auth.log | tail -n 20

echo ""
echo "[5/8] Docker container health..."
docker compose -f /opt/kloud/docker-compose.prod.yml ps

echo ""
echo "[6/8] Disk usage..."
df -h

echo ""
echo "[7/8] Database size..."
docker compose -f /opt/kloud/docker-compose.prod.yml exec postgres \
  psql -U kloud_prod -c "SELECT pg_size_pretty(pg_database_size('klouddb'));"

echo ""
echo "[8/8] Recent backup status..."
ls -lht /opt/kloud/backups/ | head -n 5

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Security check completed: $(date)"
echo "════════════════════════════════════════════════════════════"
EOF

chmod +x /opt/kloud/security-check.sh
```

Run monthly: `/opt/kloud/security-check.sh`

---

## 🔍 Audit Logging

Enable comprehensive logging:

```bash
# API request logging (already enabled in nginx)
tail -f /var/log/nginx/access.log

# Application logs
docker compose -f /opt/kloud/docker-compose.prod.yml logs -f api

# Database audit logging (optional)
docker compose -f /opt/kloud/docker-compose.prod.yml exec postgres \
  psql -U kloud_prod -c "ALTER SYSTEM SET log_statement = 'all';"
```

---

## 📞 Security Contacts

- **Hetzner Support:** https://www.hetzner.com/support
- **STRATO Support:** https://www.strato.de/support
- **Let's Encrypt Status:** https://letsencrypt.status.io/

---

## ✅ Compliance Notes

- **GDPR:** Ensure data retention policies are configured
- **PCI-DSS:** If handling payments, ensure Stripe handles all card data
- **ISO 27001:** Regular security audits recommended
- **Data Location:** Germany (GDPR-compliant)

---

**Remember:** Security is an ongoing process, not a one-time setup!

