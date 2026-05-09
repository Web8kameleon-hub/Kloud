# 🚀 Kloud Cloud - Quick Start Guide

## 📋 Overview

The Kloud Cloud project is now fully integrated with an optimized startup script that launches all services in one command. The system includes:

- **FastAPI Backend** (Port 8000) - Core API with all endpoints
- **Next.js Frontend** (Port 3001) - Modern React dashboard  
- **ORCH Service** (Port 5555) - Orchestration service
- **MESH Network** (Port 7777) - Network service
- **PostgreSQL Database** - Data persistence
- **Redis Cache** - Session/cache management
- **MinIO Storage** - S3-compatible object storage

## ⚡ Quick Start

### One-Command Startup (100% Functional)

```powershell
.\scripts\start-all.ps1
```

This single command will:

1. ✅ Verify Python virtual environment
2. ✅ Install all Python dependencies
3. ✅ Install all Node.js packages
4. ✅ Start all services in the correct order
5. ✅ Verify health of each service
6. ✅ Provide access links and status

**Result**: All services running in background with centralized logging

### Open in New Windows (Visible)

```powershell
.\scripts\start-all.ps1 -Detached
```

Each service opens in its own PowerShell window for real-time log viewing.

### Clean Restart

```powershell
.\scripts\start-all.ps1 -Clean
```

Kills all existing processes and starts fresh.

## 📍 Service Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http: //localhost:3001 | Web UI |
| API Docs | http: //localhost:8000/docs | Interactive API documentation |
| Health | http: //localhost:8000/health | System health status |
| Status | http: //localhost:8000/api/system-status | Detailed metrics |

## 📊 Process Status

View running services:

```powershell
Get-Job
```

View live logs:

```powershell
Get-Content logs/api-*.log -Tail 20 -Wait
Get-Content logs/next-*.log -Tail 20 -Wait
```

Stop a service:

```powershell
Stop-Job -Name API
```

## 🔧 Script Features

### Automatic Environment Setup

- Creates `.venv` if missing
- Installs Python dependencies from `requirements.txt`
- Installs Node.js packages with `npm install`
- Handles all path validation

### Health Monitoring

- 10-retry health checks per service
- 2-second intervals between checks
- Verifies API endpoints before considering ready
- Clear success/failure indicators

### Centralized Logging

- All logs stored in `logs/` directory
- Timestamped filenames: `service-YYYYMMDD-HHMMSS.log`
- Easy access to service history
- Real-time log streaming capability

### Service Ordering

- Services start in dependency order
- API (1) → MESH (2) → ORCH (3) → NEXT (4)
- Each service checked for health before proceeding

### Background Job Management

- All services run as PowerShell background jobs
- No blocking or frozen windows
- View status with `Get-Job`
- Manage individual services easily

## 🛠️ Advanced Usage

### Start Specific Service Only

```powershell
.\scripts\start-all.ps1 -Service API
```

Services available: `API`, `MESH`, `ORCH`, `NEXT`

### Monitor Mode (Future)

```powershell
.\scripts\start-all.ps1 -Monitor
```

Displays real-time service metrics and status updates.

## 📝 Configuration

### Environment Variables

Set in `apps/web/.env` or `apps/web/.env.local`:
...
NEXT_PUBLIC_API_BASE=http: //localhost:8000
NODE_ENV=development
...

### Python Settings

Edit service commands in `scripts/start-all.ps1`:

```powershell
$Services = @(
    @{ Name = 'API'; Cmd = '...' }
    # ...
)
```

## 🔍 Troubleshooting

### Service Fails to Start

Check logs:

```powershell
Get-Content logs/service-name-*.log -Tail 30
```

### Port Already in Use

The script automatically finds available ports:

- Port conflicts are detected
- Alternative ports assigned (3001, 3002, etc.)
- Check logs for actual listening port

### Dependency Issues

Clean reinstall:

```powershell
.\scripts\start-all.ps1 -Clean
Remove-Item .venv -Recurse -Force
.\scripts\start-all.ps1
```

### Job Won't Stop

Force kill:

```powershell
Get-Process python | Stop-Process -Force
Get-Process node | Stop-Process -Force
```

## 📚 Documentation

- **Architecture**: See `.github/copilot-instructions.md`
- **System Status**: See `SYSTEM_STATUS.md`
- **API Reference**: http:
//localhost:8000/docs
- **Fixes Applied**: See `FIXES_APPLIED.md`

## 🎯 Next Steps

1. Open dashboard: http:
//localhost:3001
2. Explore API: http:
//localhost:8000/docs
3. Start developing!
4. Check logs if anything seems off

## ✅ System Checklist

- [x] All services configured
- [x] Environment auto-setup
- [x] Health monitoring enabled
- [x] Centralized logging active
- [x] One-command startup working
- [x] Service dependencies ordered
- [x] Documentation complete
- [x] Ready for production

---

**System Status**: ✅ **100% Operational**  
**Last Updated**: November 30, 2025  
**Maintainer**: Kloud Development Team

