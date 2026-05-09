# 🔐 Environment Setup Guide

## Development Environment

1. **Copy development template:**
   ```bash
   cp .env.development .env
   ```

2. **Edit .env with your local settings** (optional)

3. **Start services:**
   ```bash
   ./start-all.ps1 dev
   ```

## Production Environment

1. **Copy production template:**
   ```bash
   cp .env.example .env.production
   ```

2. **Fill in REAL production values:**
   - DB_HOST, DB_USER, DB_PASSWORD
   - JWT_SECRET (generate with: `openssl rand -hex 32`)
   - STRIPE_API_KEY, SENTRY_DSN (if using)

3. **Add to GitHub Secrets:**
   - Go to: `https://github.com/LedjanAhmati/Kloud-cloud/settings/secrets/actions`
   - Add each secret individually

## Required Secrets for Production

| Secret | Description | Required |
|--------|-------------|----------|
| `DB_HOST` | Database hostname | ✅ Yes |
| `DB_USER` | Database username | ✅ Yes |
| `DB_PASSWORD` | Database password | ✅ Yes |
| `JWT_SECRET` | JWT signing key | ✅ Yes |
| `STRIPE_API_KEY` | Stripe payments | ⚠️  Optional |
| `SENTRY_DSN` | Error tracking | ⚠️  Optional |

## GitHub Actions Behavior

- **Development Mode:** No secrets configured → CI passes with warnings
- **Production Mode:** Secrets configured → CI requires all critical vars


