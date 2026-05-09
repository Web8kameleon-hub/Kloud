# 🚀 KLOUD CLOUD - MASTER LAUNCHER GUIDE

## Complete System Orchestration - Two Scripts for All Needs

---

## 📋 SCRIPTS OVERVIEW

### 1. **MASTER-LAUNCH.ps1** (7 Operational Modes)
Modular script with multiple execution modes for different use cases.

**Location:** `c:\kloud-cloud\MASTER-LAUNCH.ps1`

**Modes:**
```
dev          - Development (API + Frontend as background jobs)
prod         - Production (Detached windows with isolated processes)
full         - Full stack (All services with health checks)
docker       - Docker Compose (12-service containerized stack)
saas         - SaaS microservices only (ALBA, ALBI, JONA, Orchestrator)
monitor      - Continuous monitoring (Health checks every 30 sec)
diagnostics  - System health scan (Port check, service probes)
```

**Usage:**
```powershell
.\MASTER-LAUNCH.ps1 -Mode full                    # Full stack startup
.\MASTER-LAUNCH.ps1 -Mode dev -Monitor            # Dev mode with monitoring
.\MASTER-LAUNCH.ps1 -Mode diagnostics             # System health check
.\MASTER-LAUNCH.ps1 -Mode full -Clean -Monitor    # Full with cleanup & monitor
```

**Flags:**
- `-Clean` — Kill existing processes before startup
- `-DryRun` — Preview without launching
- `-Monitor` — Continuous health monitoring
- `-Rebuild` — Rebuild Docker images (docker mode only)
- `-Help` — Show help documentation

---

### 2. **MASTER-LAUNCH-FULL.ps1** (Complete Orchestration)
Ultimate launcher that starts ALL 11 services in separate PowerShell windows.

**Location:** `c:\kloud-cloud\MASTER-LAUNCH-FULL.ps1`

**Services Launched (11 Total):**

```
┌─ INFRASTRUCTURE (Docker)
│  ├─ PostgreSQL (5432)   - Database
│  ├─ Redis (6379)        - Cache
│  └─ MinIO (9000/9001)   - Object Storage
│
├─ MICROSERVICES (Python)
│  ├─ ALBA (5555)         - Network Telemetry
│  ├─ ALBI (6666)         - Neural Processing
│  ├─ JONA (7777)         - Data Synthesis
│  └─ Mesh (9999)         - Service Orchestration
│
├─ CORE SERVICES
│  ├─ API Backend (8000)  - FastAPI
│  └─ Frontend (3000)     - React Dashboard
│
└─ MONITORING (Docker)
   ├─ Prometheus (9090)   - Metrics Collection
   └─ Grafana (3001)      - Visualization
```

**Usage:**
```powershell
.\MASTER-LAUNCH-FULL.ps1                        # Launch all services
.\MASTER-LAUNCH-FULL.ps1 -Clean                 # Clean & launch all
.\MASTER-LAUNCH-FULL.ps1 -Monitor               # Launch + continuous monitoring
.\MASTER-LAUNCH-FULL.ps1 -DryRun                # Preview without launching
.\MASTER-LAUNCH-FULL.ps1 -Docker -Monitor       # Docker + monitoring
```

**Flags:**
- `-Clean` — Kill existing processes
- `-Docker` — Use Docker Compose for infrastructure
- `-DryRun` — Preview only
- `-Monitor` — Enable continuous health checking (30-sec intervals)
- `-Help` — Show help documentation

---

## 🎯 QUICK START GUIDE

### For Investor Demo (Best Choice)
```powershell
.\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor
```
✅ All services in separate windows
✅ Continuous health monitoring
✅ Dashboard shows all endpoints
✅ Real-time status tracking

### For Development
```powershell
.\MASTER-LAUNCH.ps1 -Mode dev
```
✅ Fast startup (API + Frontend only)
✅ Background jobs (easy to manage)
✅ Use `Get-Job` and `Stop-Job` for control

### For Production Testing
```powershell
.\MASTER-LAUNCH.ps1 -Mode full -Monitor
```
✅ Full stack simulation
✅ Health checks every 30 seconds
✅ Real production-like setup

### For Complete Docker Stack
```powershell
.\MASTER-LAUNCH-FULL.ps1 -Docker -Monitor
```
✅ 11 services in containers
✅ Database persistence
✅ Complete observability

---

## 📊 AVAILABLE ENDPOINTS

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Frontend** | http://localhost:3000 | — | React Dashboard |
| **API Docs** | http://localhost:8000/docs | — | Swagger API Docs |
| **API Health** | http://localhost:8000/health | — | System Status |
| **Grafana** | http://localhost:3001 | admin/admin | Dashboards |
| **Prometheus** | http://localhost:9090 | — | Metrics |
| **MinIO** | http://localhost:9001 | minioadmin/minioadmin | Storage |
| **Fitness Dashboard** | http://localhost:3000/modules/fitness-dashboard | — | AI Training |
| **ALBA** | http://localhost:5555 | — | Telemetry |
| **ALBI** | http://localhost:6666 | — | Neural |
| **JONA** | http://localhost:7777 | — | Synthesis |
| **Orchestrator** | http://localhost:9999 | — | Service Registry |
| **PostgreSQL** | localhost:5432 | postgres/postgres | Database |
| **Redis** | localhost:6379 | — | Cache |

---

## 🔧 WINDOW MANAGEMENT

When using **MASTER-LAUNCH-FULL.ps1**, each service runs in its own PowerShell window:

```
Ctrl+Tab       → Switch between windows (Windows 10/11)
Alt+Tab        → Cycle through all open windows
Ctrl+C         → Stop service in active window (graceful)
Close Window   → Stop that service (clean shutdown)
```

### Terminal Shortcuts
```powershell
Get-Job                    # List background jobs
Stop-Job -Name API         # Stop API service
Get-Job | Stop-Job         # Stop all jobs
Get-Process node           # List node processes
Get-Process python         # List python processes
```

---

## 🚨 TROUBLESHOOTING

### Ports Already in Use
```powershell
.\MASTER-LAUNCH.ps1 -Mode dev -Clean
# or
.\MASTER-LAUNCH-FULL.ps1 -Clean
```

### Check System Health
```powershell
.\MASTER-LAUNCH.ps1 -Mode diagnostics
```

**Output shows:**
- ✓ Active services
- ✓ Available ports
- ✓ Health endpoint status
- ✓ Process count
- ✓ Project configuration

### View Running Services
```powershell
Get-NetTCPConnection | Where-Object { $_.LocalPort -in 3000,5432,6379,8000,9000,9090,3001 }
```

### Kill All Services
```powershell
Get-Process node,python -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## 📈 PERFORMANCE CONSIDERATIONS

### Recommended Specs
- **RAM:** 8GB minimum (16GB for comfortable operation)
- **CPU:** 4 cores minimum (8+ cores recommended)
- **Disk:** 20GB free space
- **Network:** 100Mbps+ recommended for services

### Service Startup Times
- Infrastructure (PostgreSQL, Redis, MinIO): 5-10 seconds
- Microservices (ALBA, ALBI, JONA, Mesh): 3-5 seconds each
- Core Services (API, Frontend): 2-3 seconds each
- Monitoring (Prometheus, Grafana): 5-8 seconds each

**Total Startup:** ~45-60 seconds for full system

---

## 🎓 INVESTOR DEMO SCRIPT

```powershell
# 1. Start everything with monitoring
.\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor

# 2. Wait 30 seconds for services to initialize

# 3. Open browser to main endpoints
Start http://localhost:3000/modules/fitness-dashboard
Start http://localhost:3001  # Grafana dashboards
Start http://localhost:8000/docs  # API documentation

# 4. Show health status
.\MASTER-LAUNCH.ps1 -Mode diagnostics

# 5. Keep monitoring going for entire demo
# Windows remain open for Q&A
```

**Demo Talking Points:**
- ✅ 11 services running in isolated environments
- ✅ Real-time biometric data simulation
- ✅ AI form analysis for fitness coaching
- ✅ Complete microservices architecture
- ✅ Production-grade monitoring & observability
- ✅ Containerized deployment ready

---

## 🔐 SECURITY NOTES

### Default Credentials (Development Only)
```
Grafana:     admin / admin
MinIO:       minioadmin / minioadmin
PostgreSQL:  postgres / postgres
Redis:       No password (local only)
```

⚠️ **Change these for production deployment!**

---

## 📝 MAINTENANCE

### Regular Tasks
```powershell
# Check health
.\MASTER-LAUNCH.ps1 -Mode diagnostics

# Clean and restart
.\MASTER-LAUNCH-FULL.ps1 -Clean

# View logs (Windows stay open - scroll in each)
# Alt+Tab to cycle through windows
```

### Database Cleanup
```powershell
# Connect to PostgreSQL
psql -U postgres -h localhost

# View databases
\l

# Reset database
DROP DATABASE kloud;
CREATE DATABASE kloud;
```

---

## 💡 BEST PRACTICES

1. **Always Use -Clean Before Demos**
   ```powershell
   .\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor
   ```

2. **Monitor Health During Operations**
   ```powershell
   .\MASTER-LAUNCH.ps1 -Mode monitor
   ```

3. **DryRun for Verification**
   ```powershell
   .\MASTER-LAUNCH-FULL.ps1 -DryRun
   ```

4. **Save Important Data Before Cleanup**
   - Database backups
   - Generated reports
   - Training datasets

5. **Document Service Dependencies**
   - Order matters: Infrastructure → Microservices → Core → Monitoring
   - 2-second delays prevent resource conflicts

---

## 🎯 RECOMMENDED USAGE MATRIX

| Use Case | Script | Mode | Flags |
|----------|--------|------|-------|
| **Development** | MASTER-LAUNCH.ps1 | dev | none |
| **Testing** | MASTER-LAUNCH.ps1 | full | -Monitor |
| **Investor Demo** | MASTER-LAUNCH-FULL.ps1 | full | -Clean -Monitor |
| **Production** | MASTER-LAUNCH-FULL.ps1 | docker | -Rebuild -Monitor |
| **Troubleshooting** | MASTER-LAUNCH.ps1 | diagnostics | none |
| **Quick Health Check** | MASTER-LAUNCH.ps1 | diagnostics | none |

---

## 📞 SUPPORT

For issues:
1. Run diagnostics: `.\MASTER-LAUNCH.ps1 -Mode diagnostics`
2. Check port conflicts: `netstat -ano | findstr LISTENING`
3. Review logs: Check individual service windows (don't close them)
4. Clean and retry: `.\MASTER-LAUNCH-FULL.ps1 -Clean -DryRun`

---

**Version:** 3.0
**Last Updated:** December 3, 2025
**Status:** ✅ Production Ready

🚀 **Kloud Cloud is ready for takeoff!**

