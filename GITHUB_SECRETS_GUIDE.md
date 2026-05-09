# 🔐 GitHub Secrets Configuration Guide

## Kloud Cloud CI/CD Security Setup

### Required Secrets for GitHub Actions

Go to: **Repository Settings → Secrets and variables → Actions → New repository secret**

---

## 🔴 REQUIRED SECRETS

### Authentication & Security

| Secret Name      | Description         | How to Generate        |
| ---------------- | ------------------- | ---------------------- |
| `API_SECRET_KEY` | Main API secret key | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | JWT signing key     | `openssl rand -hex 64` |

### Database

| Secret Name         | Description            | Example                                        |
| ------------------- | ---------------------- | ---------------------------------------------- |
| `POSTGRES_PASSWORD` | PostgreSQL password    | Strong random password                         |
| `DATABASE_URL`      | Full connection string | `postgresql+asyncpg://user:pass@host:5432/db`  |
| `REDIS_PASSWORD`    | Redis password         | Strong random password                         |

### Stripe Payments

| Secret Name              | Description     | Source                      |
| ------------------------ | --------------- | --------------------------- |
| `STRIPE_PUBLISHABLE_KEY` | Public key      | Stripe Dashboard            |
| `STRIPE_SECRET_KEY`      | Private key     | Stripe Dashboard            |
| `STRIPE_WEBHOOK_SECRET`  | Webhook signing | Stripe Dashboard → Webhooks |

---

## 🟡 OPTIONAL SECRETS

### Monitoring

| Secret Name        | Description             |
| ------------------ | ----------------------- |
| `SENTRY_DSN`       | Sentry error tracking   |
| `GRAFANA_PASSWORD` | Grafana admin password  |

### External Services

| Secret Name              | Description         |
| ------------------------ | ------------------- |
| `SLACK_WEBHOOK_URL`      | Slack notifications |
| `KEYCLOAK_CLIENT_SECRET` | Keycloak auth       |
| `WEAVIATE_API_KEY`       | Vector DB access    |
| `INFLUXDB_TOKEN`         | InfluxDB token      |

### Aviation Weather APIs

| Secret Name        | Description            |
| ------------------ | ---------------------- |
| `CHECKWX_API_KEY`  | CheckWX METAR/TAF API  |
| `OPENSKY_USERNAME` | OpenSky Network auth   |
| `OPENSKY_PASSWORD` | OpenSky Network auth   |

---

## 🟢 ENVIRONMENT SECRETS (per environment)

### Production Environment

Create at: **Settings → Environments → production → Add secret**

```env
POSTGRES_HOST=your-production-db.example.com
REDIS_HOST=your-production-redis.example.com
APP_ENV=production
DEBUG=false
```

### Staging Environment

Create at: **Settings → Environments → staging → Add secret**

```env
POSTGRES_HOST=your-staging-db.example.com
APP_ENV=staging
DEBUG=true
```

---

## 🔒 Security Best Practices

### 1. Never Commit Secrets

- ✅ `.env` is in `.gitignore`
- ✅ Use `.env.example` as template
- ✅ Gitleaks scans for leaked secrets

### 2. Rotate Secrets Regularly

- API keys: Every 90 days
- Database passwords: Every 180 days
- JWT secrets: On security incidents

### 3. Use Least Privilege

- Create service accounts with minimal permissions
- Use read-only tokens where possible

### 4. Monitor Secret Usage

- Enable GitHub secret scanning
- Review Dependabot alerts weekly
- Check workflow logs for exposure

---

## 🚀 Quick Setup Commands

### Generate Strong Secrets (PowerShell)

```powershell
# API Secret Key
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))

# JWT Secret
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(64))

# Random Password
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 24 | % {[char]$_})
```

### Generate Strong Secrets (Bash/Linux)

```bash
# API Secret Key
openssl rand -hex 32

# JWT Secret  
openssl rand -hex 64

# Random Password
openssl rand -base64 24
```

---

## 📋 Checklist Before Deployment

- [ ] All required secrets added to GitHub
- [ ] Production environment created
- [ ] Staging environment created
- [ ] Secrets rotated from development values
- [ ] Gitleaks scan passing
- [ ] No hardcoded secrets in codebase
- [ ] `.env` file NOT committed
- [ ] Dependabot enabled

---

## 🔗 Related Files

- [.env.example](.env.example) - Template for local development
- [.gitignore](.gitignore) - Ensures .env is not committed
- [.github/workflows/ci.yml](.github/workflows/ci.yml) - CI pipeline
- [.github/workflows/ultra-security.yml](.github/workflows/ultra-security.yml) - Security scans

---

Last updated: January 2026

