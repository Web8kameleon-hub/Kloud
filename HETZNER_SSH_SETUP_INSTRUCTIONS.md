# KAMELEON.LIFE - HETZNER NEU SSH SETUP + DEPLOYMENT

## Status
- ✅ Code ready (Web8kameleon-hub/Kloud master branch)
- ✅ DNS records configured (91.98.47.131)
- ⏳ SSH Access: PENDING (ed25519 key not authorized on server)
- ⏳ Cleanup + Deploy: READY TO EXECUTE

---

## Step 1: Add SSH Key to Server

You need to add your public key to `~root/.ssh/authorized_keys` on hetzner-neu.

**Option A: Via Hetzner Console/Web UI** (Fastest)
1. Go to Hetzner Cloud Console → debian-32gb-fsn1-1 → VNC Console
2. Login as root (or use existing session if still open)
3. Run:
   ```bash
   mkdir -p ~/.ssh
   echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPylx877olpdJK5N2of2sZV3hxQsGIe0VwhirCGahiVX clisonix-ops' >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

**Option B: If you have console access already open**
Just paste the above commands directly.

---

## Step 2: Verify SSH Access

From your local machine:
```powershell
ssh -i C:\Users\Admin\.ssh\id_ed25519 root@91.98.47.131 "whoami; hostname"
# Expected: root, debian-32gb-fsn1-1
```

---

## Step 3: Run the Cleanup + Deploy Script

Once SSH is working:

**Option A: Upload and run locally on server**
```powershell
# From your machine
scp -i C:\Users\Admin\.ssh\id_ed25519 C:\Users\Admin\Desktop\kloud\HETZNER_DEPLOY_CLEANUP.sh root@91.98.47.131:/tmp/deploy.sh

# Then on server
ssh -i C:\Users\Admin\.ssh\id_ed25519 root@91.98.47.131 "bash /tmp/deploy.sh"
```

**Option B: Run directly (copy-paste into SSH session)**
```bash
# SSH into server
ssh -i C:\Users\Admin\.ssh\id_ed25519 root@91.98.47.131

# Then paste everything from HETZNER_DEPLOY_CLEANUP.sh
```

---

## What the Script Does

1. **CLEANUP** (5 steps):
   - Stops clisonix docker-compose stack
   - Removes all clisonix containers (100+ containers)
   - Removes clisonix networks and volumes
   - Deletes /root/Clisonix-cloud* folders

2. **DEPLOY** (6 steps):
   - Creates `/opt/kloud` with secure random .env
   - Extracts Kloud source (or clones from GitHub)
   - Starts core services: web, api, ocean-core, postgres, redis, clx
   - Runs health checks
   - Shows access points

---

## Expected Output

```
✅ CLISONIX CLEANUP COMPLETE

=========================================
[DEPLOY] Starting kameleon.life (Kloud)
=========================================

...

=========================================
✅ KAMELEON KLOUD DEPLOYED!
=========================================

Access Points:
  • Web:        http://91.98.47.131:3000
  • API:        http://91.98.47.131:8000
  • Ocean Core: http://91.98.47.131:8030

DNS Status:
  • kameleon.life A record: 91.98.47.131 ✅
  • www CNAME -> kameleon.life ✅
```

---

## Next Steps After Deploy

1. **Test web**: curl http://91.98.47.131:3000
2. **Test API**: curl http://91.98.47.131:8000/health
3. **Test Ocean**: curl http://91.98.47.131:8030/health
4. **Access via domain**: kameleon.life (DNS propagates within minutes)

---

## Troubleshooting

**SSH still fails after adding key:**
- Verify file permissions: `ls -la ~/.ssh/`
- Verify key added: `cat ~/.ssh/authorized_keys | grep clisonix-ops`
- Restart SSH: `systemctl restart ssh`

**Container build fails:**
- Check logs: `docker compose logs web`
- Ensure Docker daemon is running: `docker ps`
- Ensure .env has required variables: `cat .env`

**Port conflicts:**
- Check if ports are in use: `netstat -tlnp | grep :3000`
- Kill old process: `lsof -i :3000 | awk 'NR!=1 {print $2}' | xargs kill -9`

---

## Timeline

- **Now**: SSH setup + cleanup
- **~5 min**: Deploy (web build + containers start)
- **~2 min**: Health checks
- **~5 min**: DNS propagation to kameleon.life

**Total time: ~12 minutes**

---

## Files Ready

- **Local**: `/C:/Users/Admin/Desktop/kloud/HETZNER_DEPLOY_CLEANUP.sh`
- **Server repo**: `/opt/kloud/` (will be extracted/cloned)
- **Source**: github.com/Web8kameleon-hub/Kloud (master)
- **DNS**: kameleon.life → 91.98.47.131 ✅
