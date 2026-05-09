# 🚀 QUICK START - KLOUD CLOUD

## ⚡ Fastest Way to Get Running

### Option 1: Use Master Launcher (RECOMMENDED)
```powershell
cd c:\kloud-cloud

# Full system with all 11 services in separate windows
.\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor

# OR just API + Frontend for quick dev
.\MASTER-LAUNCH.ps1 -Mode dev
```

### Option 2: Traditional npm dev
```powershell
cd c:\kloud-cloud
npm run dev
```

---

## 📋 IMPORTANT: Script Execution Syntax

**WRONG (will fail):**
```powershell
PS C:\kloud-cloud> MASTER-LAUNCH.ps1
PS C:\kloud-cloud> start-all.ps1
```

**CORRECT (use `./`):**
```powershell
PS C:\kloud-cloud> .\MASTER-LAUNCH.ps1
PS C:\kloud-cloud> .\MASTER-LAUNCH-FULL.ps1
```

The `./` tells PowerShell to run scripts from the current directory.

---

## 🎯 Available Launcher Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| **MASTER-LAUNCH.ps1** | `.\MASTER-LAUNCH.ps1 -Mode dev` | Modular startup (7 modes) |
| **MASTER-LAUNCH-FULL.ps1** | `.\MASTER-LAUNCH-FULL.ps1 -Monitor` | All 11 services |
| **npm dev** | `npm run dev` | Traditional monorepo start |

---

## 🌐 Access Endpoints (After Startup)

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | — |
| API Docs | http://localhost:8000/docs | — |
| Grafana | http://localhost:3001 | admin / admin |
| MinIO | http://localhost:9001 | minioadmin / minioadmin |
| Fitness AI | http://localhost:3000/modules/fitness-dashboard | — |

---

## ✅ Verify System Health

```powershell
.\MASTER-LAUNCH.ps1 -Mode diagnostics
```

Shows:
- ✓ All service ports
- ✓ Health endpoint status
- ✓ Running processes
- ✓ Project configuration

---

## 🆘 Troubleshooting

### Script won't run
```powershell
# Remember the ./
.\MASTER-LAUNCH.ps1 -Help
```

### Ports already in use
```powershell
# Clean up old processes
.\MASTER-LAUNCH.ps1 -Mode dev -Clean
```

### Next.js manifest errors
Already fixed! The manifests are now pre-created in `.next/server/`

### View logs while running
Each service stays in its window - scroll to see output

---

## 💡 Pro Tips

1. **Use Alt+Tab** to switch between service windows
2. **Close a window** to stop that service gracefully
3. **Run `-DryRun`** to preview startup without launching:
   ```powershell
   .\MASTER-LAUNCH-FULL.ps1 -DryRun
   ```

---

**Status:** ✅ Ready to Launch!

🚀 **Next Command:**
```powershell
cd c:\kloud-cloud
.\MASTER-LAUNCH-FULL.ps1 -Clean -Monitor
```

