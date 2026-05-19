# Kloud Deployment Checklist (1-Page Quick Reference)

**Duration:** ~5-10 minutes | **Reference:** [HOSTING_EXECUTION_BASELINE.md](HOSTING_EXECUTION_BASELINE.md)

---

## Pre-Deployment (Local)

- [ ] Code committed to `master` branch
- [ ] All changes reviewed and approved
- [ ] No uncommitted changes: `git status` shows clean
- [ ] Latest master pulled: `git pull origin master`

---

## On Server (`/opt/kloud`)

### Step 1: Sync Code Exactly

```bash
cd /opt/kloud
git fetch origin
git reset --hard origin/master
git rev-parse --short HEAD  # Record SHA for logs
```

**✓ Verify:** HEAD matches remote master SHA

---

### Step 2: Validate Environment File

```bash
[ -f .env ] || cp env .env
grep -n '^STRIPE_WEBHOOK_SECRET=' .env
grep -n '^DATABASE_URL=' .env
grep -n '^REDIS_URL=' .env
```

**✓ Verify:** All 3 critical keys present (non-empty)

---

### Step 3: Build Only Changed Services

```bash
# Example: if ocean-core and asi changed
docker compose build ocean-core asi
```

**✓ Verify:** Build logs show "Successfully tagged"

---

### Step 4: Restart Only Changed Services

```bash
# NO global docker compose down!
# Restart targeted services only

docker compose stop ocean-core asi
docker compose rm -f ocean-core asi
docker compose up -d --no-deps ocean-core asi
```

**✓ Verify:** `docker compose ps | grep -E 'ocean-core|asi'` shows (Up)

---

### Step 5: Health Checks

```bash
curl -s http://localhost:8030/health | jq .
curl -s http://localhost:9094/health | jq .
curl -s http://localhost:8000/health | jq .
```

**✓ Verify:** All 3 return HTTP 200 with healthy status

---

### Step 6: Functional Sanity Tests

```bash
# Test frontend rewrite to API
curl -s http://localhost:3001/api/health

# Test ocean-core endpoint
curl -s http://localhost:3001/api/ocean/flow

# Check logs for errors
docker compose logs ocean-core --tail 20
```

**✓ Verify:** No crash loops, errors, or reconnection attempts

---

## Rollback (If Health Check Fails)

```bash
# Revert to previous known-good state
git reset --hard <PREVIOUS_SHA>
docker compose build ocean-core asi
docker compose stop ocean-core asi
docker compose rm -f ocean-core asi
docker compose up -d --no-deps ocean-core asi
curl -s http://localhost:8030/health
```

---

## Documentation

- [ ] Record deployed SHA and timestamp
- [ ] Note any services restarted
- [ ] Update deployment log: `/opt/kloud/DEPLOYMENT_LOG.txt`

---

## If Network Error Occurs: "active endpoints"

See [HOSTING_EXECUTION_BASELINE.md § 10: Network Active Endpoints Playbook](HOSTING_EXECUTION_BASELINE.md#network-active-endpoints-playbook)

```bash
docker network inspect kloud_default --format '{{json .Containers}}'
docker compose stop <SERVICE>
docker compose rm -f <SERVICE>
docker compose up -d --no-deps <SERVICE>
```

---

**Questions?** Refer to [HOSTING_EXECUTION_BASELINE.md](HOSTING_EXECUTION_BASELINE.md) for full documentation.
