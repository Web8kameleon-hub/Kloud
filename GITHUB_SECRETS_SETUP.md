# 🔐 GITHUB SECRETS SETUP GUIDE

## 🎯 Why This Is Required

The CI pipeline checks for CRITICAL environment variables:
- DB_HOST
- DB_USER  
- DB_PASSWORD
- JWT_SECRET

These are injected by GitHub Secrets (not in .env file, which is local-only).

---

## 📋 STEP 1: Go to GitHub Settings

1. Open: https://github.com/LedjanAhmati/Kloud-cloud
2. Click **Settings** (top-right)
3. Left sidebar → **Secrets and variables** → **Actions**
4. Click **New repository secret**

---

## 🔑 STEP 2: Add CRITICAL Secrets

Add these EXACT names (case-sensitive):

### 1. DB_HOST
```
Name: DB_HOST
Value: (your database host - e.g., localhost or IP)
```

### 2. DB_USER
```
Name: DB_USER
Value: (your database username - e.g., kloud)
```

### 3. DB_PASSWORD
```
Name: DB_PASSWORD
Value: (your database password - KEEP SAFE!)
```

### 4. JWT_SECRET
```
Name: JWT_SECRET
Value: (any random string ≥32 chars - e.g., $(openssl rand -base64 48))
```

---

## ➕ STEP 3: Add OPTIONAL Secrets (for features)

### 5. STRIPE_API_KEY (optional)
```
Name: STRIPE_API_KEY
Value: sk_test_... (or leave empty, feature disabled)
```

### 6. SENTRY_DSN (optional)
```
Name: SENTRY_DSN
Value: https://... (or leave empty, feature disabled)
```

---

## ✅ VERIFY SETUP

After adding secrets:

1. Refresh Settings → Secrets
2. You should see 4-6 masked secrets
3. Make a test push to trigger CI
4. Check GitHub Actions tab for green checkmark

---

## 🚀 FOR HETZNER PRODUCTION

When deploying to Hetzner:

1. Create `.env.production` locally with SAME values:
   ```
   DB_HOST=hetzner-ip
   DB_USER=kloud
   DB_PASSWORD=your-password
   JWT_SECRET=same-as-github-secret
   ```

2. Copy to Hetzner server:
   ```bash
   scp .env.production root@server-ip:/home/kloud/
   ```

3. Load in docker-compose:
   ```bash
   source .env.production
   docker-compose -f docker-compose.prod.secure.yml up -d
   ```

---

## 🔒 SECURITY NOTES

- GitHub Secrets are encrypted
- Only visible to repository admins
- NOT logged in workflow output
- Safe to use in CI/CD pipeline
- Different from local .env (which stays on your machine)


