# 🔐 Secure Deployment Guide

## ⚠️ Pre-Deployment Security Checklist

Before deploying to production, complete ALL items:

- [ ] All secrets removed from git history
- [ ] `.secrets` and `.env.production` added to `.gitignore`
- [ ] Pre-commit hook installed (`cp scripts/pre-commit.sh .git/hooks/pre-commit`)
- [ ] Secret scanner executed successfully (`python scripts/scan-secrets.py`)
- [ ] Strong passwords generated (min 32 chars for databases)
- [ ] JWT secret key generated (`openssl rand -hex 32`)
- [ ] Stripe keys configured (live mode)
- [ ] PayPal credentials configured (production mode)
- [ ] SEPA IBAN validated
- [ ] TLS/SSL certificates obtained
- [ ] Firewall rules configured
- [ ] Backup strategy implemented

---

## 🚀 Deployment Options

### Option 1: Environment Variables (Recommended for Cloud Providers)

**Best for:** AWS, Azure, GCP, Hetzner Cloud

```bash
# 1. Create .env.production from template
cp .env.production.template .env.production

# 2. Edit with secure values
nano .env.production

# 3. Deploy with environment file
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml up -d
```

**Security Features:**

- ✅ No secrets in docker-compose files
- ✅ Environment variables loaded at runtime
- ✅ Easy rotation via environment updates
- ✅ Compatible with CI/CD pipelines

**Cloud Provider Integration:**

- **AWS**: Use Secrets Manager + ECS task definitions
- **Azure**: Use Key Vault + Container Instances
- **GCP**: Use Secret Manager + Cloud Run
- **Hetzner**: Use Cloud-init + environment files

---

### Option 2: Docker Secrets (Recommended for Docker Swarm)

**Best for:** Docker Swarm, production clusters

```bash
# 1. Create secrets directory
./scripts/setup-secrets.sh  # Linux/Mac
# or
.\scripts\setup-secrets.ps1  # Windows

# 2. Deploy with secrets
docker stack deploy -c docker-compose.secrets.yml kloud
```

**Security Features:**

- ✅ Secrets stored in encrypted Swarm Raft log
- ✅ Only mounted to authorized services
- ✅ Automatic secret rotation support
- ✅ No secrets in environment variables

---

### Option 3: HashiCorp Vault (Enterprise)

**Best for:** Multi-cluster, enterprise deployments

```bash
# 1. Install Vault
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install vault

# 2. Configure Vault
vault server -dev  # Dev mode (use proper config for prod)

# 3. Store secrets
vault kv put secret/kloud/postgres password="$(openssl rand -hex 32)"
vault kv put secret/kloud/redis password="$(openssl rand -hex 32)"
vault kv put secret/kloud/jwt secret="$(openssl rand -hex 32)"

# 4. Deploy with Vault integration
# Configure services to read from Vault API
```

**Security Features:**

- ✅ Centralized secret management
- ✅ Audit logging
- ✅ Dynamic secrets
- ✅ Automatic rotation
- ✅ Fine-grained access control

---

## 🔑 Secret Generation

### Generate Strong Passwords

```bash
# Database passwords (32+ chars)
openssl rand -base64 32

# API keys (64 chars hex)
openssl rand -hex 32

# JWT secret (64 chars hex)
openssl rand -hex 32

# UUID-based secrets
uuidgen | tr -d '-'
```

### Validate Secrets

```bash
# Check entropy (should be high)
echo "your-secret" | ent

# Check password strength
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🛡️ Environment-Specific Configuration

### Development Environment

```bash
# Use .env.development (weak credentials OK for local dev)
cp .env.development .env
docker-compose up -d
```

**Characteristics:**

- 🔓 Weak passwords (dev123, admin)
- 🔓 Debug mode enabled
- 🔓 CORS permissive
- 🔓 Rate limiting disabled

### Staging Environment

```bash
# Use .env.staging (production-like but isolated)
cp .env.production.template .env.staging
# Edit with staging-specific values
docker-compose --env-file .env.staging -f docker-compose.prod.secure.yml up -d
```

**Characteristics:**

- 🔐 Strong passwords (production-grade)
- 🔍 Debug mode enabled (for testing)
- 🔒 CORS restricted to staging domain
- ⏱️ Rate limiting enabled
- 💳 Stripe test mode
- 📧 PayPal sandbox

### Production Environment

```bash
# Use .env.production (maximum security)
cp .env.production.template .env.production
# Fill with production secrets
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml up -d
```

**Characteristics:**

- 🔐 Strong passwords (32+ chars)
- 🔒 Debug mode disabled
- 🔒 CORS restricted to production domains
- ⏱️ Rate limiting strict
- 💳 Stripe live mode
- 📧 PayPal production
- 🔔 Monitoring & alerting enabled
- 📦 Backup enabled

---

## 📋 Deployment Steps (Production)

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### 2. Clone Repository

```bash
git clone https://github.com/Kameleonlife/Kloud-cloud.git
cd Kloud-cloud

# Switch to production branch (if exists)
git checkout production
```

### 3. Configure Secrets

```bash
# Copy template
cp .env.production.template .env.production

# Generate secrets
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)

# Edit .env.production with generated values
nano .env.production
```

### 4. Verify Configuration

```bash
# Scan for exposed secrets
python scripts/scan-secrets.py

# Validate docker-compose
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml config

# Check environment variables are loaded
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml config | grep PASSWORD
# Should show: ${POSTGRES_PASSWORD} or loaded values (not hardcoded)
```

### 5. Deploy Services

```bash
# Pull images
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml pull

# Build custom images
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml build

# Start services
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml up -d

# Check health
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml ps
```

### 6. Verify Deployment

```bash
# Check service health
curl http://localhost:8000/health

# Check database connection
docker exec kloud-postgres pg_isready -U kloud

# Check Redis
docker exec kloud-redis redis-cli ping

# View logs
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml logs -f --tail=50
```

---

## 🔄 Secret Rotation

### Quarterly Rotation (Recommended)

```bash
# 1. Generate new secrets
NEW_POSTGRES_PASSWORD=$(openssl rand -base64 32)
NEW_JWT_SECRET=$(openssl rand -hex 32)

# 2. Update database password
docker exec kloud-postgres psql -U kloud -c "ALTER USER kloud PASSWORD '$NEW_POSTGRES_PASSWORD';"

# 3. Update .env.production
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_POSTGRES_PASSWORD/" .env.production

# 4. Restart services (zero-downtime)
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml up -d --no-deps postgres
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml restart api alba albi jona worker
```

### Emergency Rotation (Breach Suspected)

```bash
# 1. Rotate ALL secrets immediately
./scripts/emergency-rotate-secrets.sh

# 2. Restart all services
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml restart

# 3. Notify team
echo "SECURITY BREACH: All secrets rotated at $(date)" | mail -s "URGENT: Secret Rotation" security@kloud.com

# 4. Audit logs
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml logs --since 24h > breach-audit.log
```

---

## 🚨 Incident Response

### If Secrets are Exposed in Git

```bash
# 1. Rotate exposed secrets IMMEDIATELY
# See "Emergency Rotation" above

# 2. Remove from git history (WARNING: Rewrites history)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env.production" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (coordinate with team)
git push origin --force --all

# 4. Notify GitHub to clear cache
# Go to: https://github.com/Kameleonlife/Kloud-cloud/settings
# Click "Permanently delete this repository"
# Then re-upload without secrets

# 5. Run security audit
python scripts/scan-secrets.py > post-cleanup-audit.txt
```

### If Production is Compromised

1. **Immediate Actions** (0-1 hour)
   - Isolate affected services
   - Rotate all credentials
   - Enable firewall rules (deny all)
   - Snapshot current state for forensics

2. **Investigation** (1-24 hours)
   - Review access logs
   - Identify attack vector
   - Assess data exposure
   - Contact authorities (if required by GDPR)

3. **Recovery** (24-48 hours)
   - Deploy clean instances
   - Restore from trusted backups
   - Update security policies
   - Implement additional controls

4. **Post-Incident** (1 week)
   - Complete incident report
   - Team training
   - Update runbooks
   - External security audit

---

## 📊 Monitoring Secret Usage

### Audit Secret Access

```bash
# Check which services have access to secrets
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml config | grep -A5 "environment:"

# Monitor environment variable usage
docker inspect kloud-api | jq '.[0].Config.Env'

# Check for secrets in logs (should be none!)
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml logs | grep -i "password\|secret\|key" | wc -l
```

### Set Up Alerts

```bash
# Monitor failed authentication attempts
docker-compose --env-file .env.production -f docker-compose.prod.secure.yml logs api | grep "401 Unauthorized" | wc -l

# Alert if secrets appear in logs
if docker-compose logs | grep -qE "(password|secret|key)="; then
  echo "WARNING: Secrets detected in logs!" | mail -s "Security Alert" security@kloud.com
fi
```

---

## ✅ Post-Deployment Validation

```bash
# Security checklist
echo "=== SECURITY VALIDATION ==="

# 1. No hardcoded secrets in compose files
echo "[1/7] Checking docker-compose files..."
grep -r "password.*:" docker-compose.prod.secure.yml && echo "❌ FAIL" || echo "✅ PASS"

# 2. .env.production not in git
echo "[2/7] Checking .gitignore..."
git ls-files | grep -q ".env.production" && echo "❌ FAIL: .env.production in git!" || echo "✅ PASS"

# 3. Pre-commit hook installed
echo "[3/7] Checking pre-commit hook..."
[ -f .git/hooks/pre-commit ] && echo "✅ PASS" || echo "❌ FAIL: Install pre-commit hook"

# 4. No secrets in current files
echo "[4/7] Running secret scanner..."
python scripts/scan-secrets.py | grep -q "No exposed secrets" && echo "✅ PASS" || echo "❌ FAIL: Secrets detected!"

# 5. Services are healthy
echo "[5/7] Checking service health..."
docker-compose --env-file .env.production ps | grep -q "unhealthy" && echo "❌ FAIL" || echo "✅ PASS"

# 6. TLS enabled (if applicable)
echo "[6/7] Checking HTTPS..."
curl -I https://api.kloud.com 2>/dev/null | grep -q "HTTP/2 200" && echo "✅ PASS" || echo "⚠️  WARNING: HTTPS not configured"

# 7. Firewall configured
echo "[7/7] Checking firewall..."
sudo ufw status | grep -q "active" && echo "✅ PASS" || echo "❌ FAIL: Enable firewall"

echo "=== VALIDATION COMPLETE ==="
```

---

## 📚 References

- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [OWASP Secret Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [HashiCorp Vault Best Practices](https://learn.hashicorp.com/tutorials/vault/production-hardening)
- [NIST SP 800-57: Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)

---

**Last Updated**: December 16, 2025  
**Version**: 1.0.0  
**Maintained by**: Kloud Security Team

