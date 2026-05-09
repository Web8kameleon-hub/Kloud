# 🌐 Hetzner Floating IP Setup Guide

**High Availability Configuration for Kloud Cloud**

---

## 📋 Overview

Floating IPs enable flexible, high-availability setups by allowing you to:
- **Instantly switch** between servers (failover in seconds)
- **Zero downtime** during maintenance or server migration
- **Geographic flexibility** - move IP between servers in the same location
- **DDoS protection** with Hetzner's network

---

## 🎯 Use Cases

### ✅ **When to Use Floating IP**

1. **High Availability** - Automatic failover if primary server fails
2. **Zero-downtime Maintenance** - Switch traffic during updates
3. **Load Balancing** - Distribute traffic across multiple servers
4. **Disaster Recovery** - Quick migration to backup server

### ⚠️ **Important Limitations**

- Floating IP and server **must be in same location** (Nuremberg, Helsinki, etc.)
- Requires **manual network configuration** on your server
- Small additional cost (~€1.20/month per IP)

---

## 🚀 Quick Start

### **Step 1: Create Floating IP in Hetzner Cloud**

1. **Via Hetzner Cloud Console:**
   ```
   Project → Floating IPs → Create Floating IP
   
   Settings:
   - Type: IPv4
   - Location: Same as your server (e.g., Nuremberg)
   - Assign to: Your Kloud server
   ```

2. **Via Hetzner CLI (hcloud):**
   ```bash
   # Install hcloud CLI
   brew install hcloud  # macOS
   # or download from: https://github.com/hetznercloud/cli
   
   # Login
   hcloud context create kloud-prod
   
   # Create Floating IP
   hcloud floating-ip create \
     --type ipv4 \
     --home-location nbg1 \
     --description "Kloud Production" \
     --name kloud-floating-ip
   
   # Assign to server
   hcloud floating-ip assign kloud-floating-ip your-server-name
   ```

**You'll receive an IP like:** `95.217.123.45`

---

### **Step 2: Configure Floating IP on Server**

The Floating IP must be configured on your server's network interface.

#### **Option A: Automatic Configuration (Recommended)**

Use our automated script:

```bash
# Download and run configuration script
curl -sSL https://raw.githubusercontent.com/LedjanAhmati/Kloud-cloud/main/scripts/setup-floating-ip.sh -o setup-floating-ip.sh

chmod +x setup-floating-ip.sh

# Run with your Floating IP
sudo ./setup-floating-ip.sh 95.217.123.45
```

#### **Option B: Manual Configuration**

1. **Identify your network interface:**
   ```bash
   ip addr show
   # Look for: eth0, ens3, enp0s3, etc.
   ```

2. **Create Netplan configuration:**
   ```bash
   sudo nano /etc/netplan/60-floating-ip.yaml
   ```

3. **Add configuration:**
   ```yaml
   network:
     version: 2
     ethernets:
       eth0:  # Replace with your interface name
         addresses:
           - 95.217.123.45/32  # Your Floating IP
   ```

4. **Apply configuration:**
   ```bash
   sudo netplan apply
   
   # Verify
   ip addr show eth0
   # Should see your Floating IP listed
   ```

5. **Test connectivity:**
   ```bash
   ping -I 95.217.123.45 8.8.8.8
   curl --interface 95.217.123.45 https://ifconfig.me
   # Should return your Floating IP
   ```

---

### **Step 3: Update DNS Records**

Point your domain to the Floating IP:

```
A Record:
kloud.com        → 95.217.123.45
*.kloud.com      → 95.217.123.45
api.kloud.com    → 95.217.123.45
```

**Propagation time:** 5 minutes to 24 hours (usually < 1 hour)

---

### **Step 4: Update SSL Certificates**

Let's Encrypt certificates are tied to the IP address.

```bash
# Stop nginx temporarily
docker compose -f /opt/kloud/docker-compose.prod.yml stop nginx

# Request new certificates with Floating IP
certbot certonly --standalone \
  -d kloud.com \
  -d api.kloud.com \
  -d www.kloud.com \
  --email admin@kloud.com \
  --agree-tos \
  --non-interactive

# Restart nginx
docker compose -f /opt/kloud/docker-compose.prod.yml start nginx
```

---

## 🔄 High Availability Setup (Optional)

### **Keepalived for Automatic Failover**

Keepalived monitors your server and automatically moves the Floating IP to a backup server if the primary fails.

#### **Architecture:**

```
                    ┌─────────────────┐
                    │  Floating IP    │
                    │  95.217.123.45  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
         ┌────▼─────┐                 ┌────▼─────┐
         │ Primary  │                 │  Backup  │
         │  Server  │◄────VRRP───────►│  Server  │
         │ (Master) │                 │  (Slave) │
         └──────────┘                 └──────────┘
```

#### **Setup Keepalived:**

**On Primary Server:**

```bash
# Install Keepalived
apt install -y keepalived

# Configure
sudo nano /etc/keepalived/keepalived.conf
```

```conf
vrrp_script check_nginx {
    script "/usr/bin/docker ps | grep nginx"
    interval 2
    weight 2
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 101  # Higher = preferred
    advert_int 1
    
    authentication {
        auth_type PASS
        auth_pass your-secret-password
    }
    
    virtual_ipaddress {
        95.217.123.45/32
    }
    
    track_script {
        check_nginx
    }
    
    notify_master "/opt/kloud/scripts/floating-ip-master.sh"
    notify_backup "/opt/kloud/scripts/floating-ip-backup.sh"
}
```

**On Backup Server (same config but):**
```conf
state BACKUP
priority 100  # Lower than master
```

#### **Create Notification Scripts:**

**Master script** (`/opt/kloud/scripts/floating-ip-master.sh`):
```bash
#!/bin/bash
# Assign Floating IP via Hetzner API

HCLOUD_TOKEN="your-hetzner-api-token"
FLOATING_IP_ID="your-floating-ip-id"
SERVER_ID="primary-server-id"

curl -X POST \
  -H "Authorization: Bearer $HCLOUD_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"server\": $SERVER_ID}" \
  "https://api.hetzner.cloud/v1/floating_ips/$FLOATING_IP_ID/actions/assign"

# Send alert
echo "Floating IP failover: PRIMARY is now MASTER" | \
  mail -s "Kloud Failover Alert" admin@kloud.com
```

**Backup script** (`/opt/kloud/scripts/floating-ip-backup.sh`):
```bash
#!/bin/bash
echo "Floating IP failover: PRIMARY is now BACKUP" | \
  mail -s "Kloud Failover Alert" admin@kloud.com
```

**Make executable:**
```bash
chmod +x /opt/kloud/scripts/floating-ip-*.sh
```

**Start Keepalived:**
```bash
systemctl enable keepalived
systemctl start keepalived
systemctl status keepalived
```

---

## 🧪 Testing Failover

### **Test 1: Manual IP Switch**

```bash
# Via Hetzner Console:
# Floating IPs → Select IP → Assign to different server

# Via CLI:
hcloud floating-ip assign kloud-floating-ip backup-server-name
```

### **Test 2: Simulate Server Failure**

```bash
# On primary server - stop nginx
docker compose -f /opt/kloud/docker-compose.prod.yml stop nginx

# Keepalived should detect failure and switch IP
# Check logs:
journalctl -u keepalived -f
```

### **Test 3: Verify DNS Resolution**

```bash
# From external machine
dig kloud.com +short
# Should return Floating IP: 95.217.123.45

# Test website accessibility
curl -I https://kloud.com
```

---

## 📊 Monitoring

### **Monitor Floating IP Status**

```bash
# Check which server has the Floating IP
hcloud floating-ip describe kloud-floating-ip

# Check Keepalived status
systemctl status keepalived

# View VRRP state
ip addr show eth0 | grep 95.217.123.45
```

### **Grafana Dashboard Metrics**

Add to your Grafana dashboard:

```promql
# Floating IP assignment status (1 = this server has IP)
node_network_address_assign_type{address="95.217.123.45"} == 1

# Keepalived state (MASTER=1, BACKUP=0)
keepalived_vrrp_state{instance="VI_1"}
```

---

## 🔒 Security Considerations

### **Firewall Rules**

```bash
# Allow VRRP (Keepalived) between servers
ufw allow from backup-server-ip to any proto vrrp

# On backup server
ufw allow from primary-server-ip to any proto vrrp
```

### **API Token Security**

Store Hetzner API token securely:

```bash
# Create secrets file
sudo nano /opt/kloud/.hetzner-secrets
```

```bash
HCLOUD_TOKEN=your-hetzner-api-token-here
FLOATING_IP_ID=123456
```

```bash
# Secure permissions
sudo chmod 600 /opt/kloud/.hetzner-secrets

# Source in scripts
source /opt/kloud/.hetzner-secrets
```

---

## 💰 Cost Calculation

| Item | Cost (EUR/month) |
|------|------------------|
| Floating IPv4 | €1.20 |
| Primary Server (CX21) | €5.83 |
| Backup Server (CX21, optional) | €5.83 |
| **Total (HA setup)** | **€12.86** |

**Without backup server:** €7.03/month

---

## 📚 Common Operations

### **Switch IP to Backup Server**

```bash
# Manual switch
hcloud floating-ip assign kloud-floating-ip backup-server

# Or via API
curl -X POST \
  -H "Authorization: Bearer $HCLOUD_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"server": BACKUP_SERVER_ID}' \
  "https://api.hetzner.cloud/v1/floating_ips/$FLOATING_IP_ID/actions/assign"
```

### **Maintenance Mode**

```bash
# 1. Switch IP to backup
hcloud floating-ip assign kloud-floating-ip backup-server

# 2. Wait for DNS propagation (2-5 minutes)
watch -n 5 'curl -I https://kloud.com'

# 3. Perform maintenance on primary server
apt update && apt upgrade -y
docker compose -f /opt/kloud/docker-compose.prod.yml pull
docker compose -f /opt/kloud/docker-compose.prod.yml up -d

# 4. Switch IP back to primary
hcloud floating-ip assign kloud-floating-ip primary-server
```

### **Remove Floating IP**

```bash
# Unassign from server
hcloud floating-ip unassign kloud-floating-ip

# Delete Floating IP
hcloud floating-ip delete kloud-floating-ip
```

---

## 🐛 Troubleshooting

### **Floating IP not accessible**

```bash
# 1. Verify IP is assigned to correct server
hcloud floating-ip list

# 2. Check network configuration
ip addr show eth0

# 3. Verify routing
ip route get 8.8.8.8 from 95.217.123.45

# 4. Test from server
curl --interface 95.217.123.45 https://ifconfig.me
```

### **Keepalived not switching**

```bash
# Check logs
journalctl -u keepalived -n 100

# Verify VRRP communication
tcpdump -i eth0 vrrp

# Check script execution
bash -x /opt/kloud/scripts/floating-ip-master.sh
```

### **SSL certificate errors after IP change**

```bash
# Regenerate certificates
certbot renew --force-renewal

# Or delete and recreate
certbot delete --cert-name kloud.com
certbot certonly --standalone -d kloud.com -d api.kloud.com
```

---

## 📖 Additional Resources

- **Hetzner Floating IP Docs:** https://docs.hetzner.com/cloud/floating-ips/overview/
- **Keepalived Documentation:** https://keepalived.readthedocs.io/
- **Hetzner Cloud API:** https://docs.hetzner.cloud/
- **hcloud CLI:** https://github.com/hetznercloud/cli

---

## ✅ Post-Setup Checklist

- [ ] Floating IP created in Hetzner Console
- [ ] Floating IP configured on server network interface
- [ ] DNS records updated to point to Floating IP
- [ ] SSL certificates regenerated with new IP
- [ ] Website accessible via Floating IP
- [ ] Keepalived installed (if HA setup)
- [ ] Failover scripts created and tested
- [ ] Backup server configured (if HA setup)
- [ ] Failover tested successfully
- [ ] Monitoring dashboard updated
- [ ] Team notified of new IP address

---

**Last Updated:** December 12, 2025  
**Maintainer:** Kloud DevOps Team

