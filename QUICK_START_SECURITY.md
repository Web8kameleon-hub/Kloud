# 🚀 Quick Start - Secure Deployment

## 📋 5-Minute Security Setup

### Step 1: Install Pre-commit Hook (Prevent Secret Commits)
```bash
# Copy pre-commit hook
cp scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Verify installation
.git/hooks/pre-commit --version
```

### Step 2: Scan for Exposed Secrets
```bash
# Run secret scanner
python scripts/scan-secrets.py

# Expected output:
# [SUCCESS] No exposed secrets found!
```

### Step 3: Setup Environment (Choose One)

#### Option A: Development (Local Testing)
```bash
# Use safe development credentials
cp .env.development .env
docker-compose up -d

# Access services:
# API: http://localhost:8000
# Grafana: http://localhost:3000 (admin/admin)
```

#### Option B: Production (Real Deployment)
```bash
# 1. Copy template
cp .env.production.template .env.production

# 2. Generate strong secrets
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env.production
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env.production
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env.production

# 3. Edit remaining values
nano .env.production

# 4. Deploy with secure compose
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml up -d
```

---

## 🔍 Quick Health Check

```bash
# Check all services
docker-compose ps

# Expected output (all "healthy"):
# kloud-postgres    Up (healthy)
# kloud-redis       Up (healthy)
# kloud-api         Up (healthy)

# Verify no secrets in environment
docker inspect kloud-api | grep -i "password\|secret" | wc -l
# Should be 0 or only references to _FILE variables
```

---

## 🛡️ Security Verification Checklist

Run this after deployment:

```bash
# 1. No hardcoded secrets
grep -r "password.*:" docker-compose.prod.secure.yml
# Expected: No matches

# 2. .env.production not in git
git ls-files | grep .env.production
# Expected: No output

# 3. Pre-commit hook active
git config core.hooksPath
ls -la .git/hooks/pre-commit
# Expected: Executable file exists

# 4. No secrets in logs
docker-compose logs | grep -iE "(password|secret|key)=" | wc -l
# Expected: 0

# 5. Services healthy
docker-compose ps | grep unhealthy
# Expected: No output
```

---

## 🚨 Emergency Procedures

### If You Accidentally Commit a Secret:

```bash
# 1. IMMEDIATELY rotate the exposed secret
# See SECURITY.md "Emergency Rotation"

# 2. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.production" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (coordinate with team first!)
git push origin --force --all

# 4. Run security scan
python scripts/scan-secrets.py
```

### If Production is Compromised:

```bash
# 1. Isolate (block all traffic)
sudo ufw deny from any

# 2. Rotate ALL secrets
./scripts/emergency-rotate-secrets.sh

# 3. Snapshot for forensics
docker-compose logs > breach-$(date +%Y%m%d-%H%M%S).log

# 4. Contact security team
echo "BREACH at $(date)" | mail -s "URGENT: Security Incident" security@kloud.com
```

---

## 📚 Full Documentation

| Quick Link | Purpose |
|------------|---------|
| [SECURITY.md](SECURITY.md) | Complete security policy |
| [DEPLOYMENT_SECURITY_GUIDE.md](DEPLOYMENT_SECURITY_GUIDE.md) | Step-by-step deployment |
| [SECURITY_REMEDIATION_SUMMARY.md](SECURITY_REMEDIATION_SUMMARY.md) | What was fixed |

---

## 🎯 Common Tasks

### Generate Secrets
```bash
# Database password (32 chars)
openssl rand -base64 32

# JWT secret (64 hex chars)
openssl rand -hex 32

# Random API key
uuidgen | tr -d '-'
```

### Rotate Secrets
```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# 2. Update .env.production
sed -i "s/OLD_PASSWORD=.*/OLD_PASSWORD=$NEW_SECRET/" .env.production

# 3. Restart services
docker-compose --env-file .env.production restart
```

### View Service Logs
```bash
# All services (last 50 lines)
docker-compose logs --tail=50 -f

# Specific service
docker-compose logs -f api

# Grep for errors
docker-compose logs | grep -i error
```

### Backup & Restore
```bash
# Backup database
docker exec kloud-postgres pg_dump -U kloud klouddb > backup-$(date +%Y%m%d).sql

# Restore database
docker exec -i kloud-postgres psql -U kloud klouddb < backup-20251216.sql
```

---

## 💡 Pro Tips

1. **Use `.env.development` for local dev** - Safe weak passwords
2. **Never commit `.env.production`** - Already in .gitignore
3. **Run `python scripts/scan-secrets.py` daily** - Catch leaks early
4. **Rotate secrets quarterly** - Set calendar reminder
5. **Enable GitHub Actions** - Automated scanning on every push
6. **Use strong passwords** - Minimum 32 characters for databases
7. **Enable 2FA on all services** - Grafana, GitHub, payment processors

---

## 🔗 Quick Links

- **API Health**: http://localhost:8000/health
- **Grafana**: http://localhost:3000
- **Kibana**: http://localhost:5601
- **MinIO Console**: http://localhost:9001
- **Victoria Metrics**: http://localhost:8428

---

## 📞 Support

**Security Issues**: security@kloud.com  
**General Support**: support@kloud.com  
**Documentation**: See `docs/` folder

---

**Last Updated**: December 16, 2025  
**Version**: 1.0.0

