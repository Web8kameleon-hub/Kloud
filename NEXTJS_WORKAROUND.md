# 🚨 Next.js Monorepo Issues - Workaround

## Problem
Next.js 15.5.4 (and 14.2.x) has critical bugs with npm workspaces in monorepos:
- Missing manifest files (middleware-manifest.json, routes-manifest.json)
- `ENOWORKSPACES` error when patching lockfiles
- `outputFileTracingRoot` causes build failures

## Quick Solution: Use Backend Standalone

### Start FastAPI Backend Only
```bash
cd apps/api
python -m uvicorn main:app --reload --port 8000
```

### Access Built-in Dashboards
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/api/system-status
- **ASI Trinity Status**: http://localhost:8000/asi/status
- **Metrics**: http://localhost:8000/metrics

### Backend Has Everything:
✅ FastAPI with auto-generated OpenAPI docs  
✅ Real-time metrics (Prometheus format)  
✅ Health checks for all services  
✅ ALBA/ALBI/JONA AI engine endpoints  
✅ Payment integration endpoints  
✅ Industrial monitoring endpoints  

---

## Fix Frontend Later (Optional)

### Option 1: Move Frontend Outside Monorepo
```bash
# Create standalone Next.js app
npx create-next-app@latest kloud-frontend
cd kloud-frontend
cp -r ../Kloud-cloud/apps/web/app ./app
cp -r ../Kloud-cloud/apps/web/components ./components
npm install
npm run dev
```

### Option 2: Use Next.js 13 (Stable with Workspaces)
```bash
cd apps/web
npm install next@13.5.6 react@18 react-dom@18
rm -rf .next node_modules/.cache
npm run dev
```

### Option 3: Wait for Next.js Fix
Track issues:
- https://github.com/vercel/next.js/issues/71714 (ENOWORKSPACES)
- https://github.com/vercel/next.js/issues/71459 (manifest files)

---

## Current Status

### ✅ Working
- **FastAPI Backend** (`apps/api/main.py`) - 3200+ lines, fully functional
- **All API Endpoints** - /health, /status, /asi/status, /metrics
- **AI Engines** - ALBA, ALBI, JONA routes loaded
- **Prometheus Metrics** - Real-time monitoring
- **Payment Integration** - Stripe, PayPal, SEPA
- **Database** - PostgreSQL with asyncpg
- **Cache** - Redis integration
- **Monitoring** - Grafana dashboards, VictoriaMetrics

### ❌ Not Working
- **Next.js Frontend** (`apps/web`) - npm workspace bugs
- **Frontend Dev Server** - Manifest file errors
- **Monorepo Build** - outputFileTracingRoot issues

---

## Recommended Workflow

### For API Development
```bash
# Terminal 1: Backend
cd apps/api
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/asi/status
```

### For Full-Stack Development
Wait for Next.js workspace fix, or use Option 1 (standalone frontend).

---

## Environment Setup

### Backend Requires
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or use the launcher
python start_server.py
```

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/Kloud

# Redis
REDIS_URL=redis://localhost:6379

# See .env.development for full list
```

---

## References
- [Next.js Workspace Issue #71714](https://github.com/vercel/next.js/issues/71714)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Monorepo Best Practices](https://turbo.build/repo/docs)

---

**Last Updated**: December 16, 2025  
**Status**: Backend functional, frontend blocked by Next.js bugs

