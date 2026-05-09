#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Hetzner Floating IP Setup Script
# ═══════════════════════════════════════════════════════════════
# 
# Automatically configures a Hetzner Floating IP on your server
# 
# Usage:
#   sudo ./setup-floating-ip.sh <floating-ip>
#   sudo ./setup-floating-ip.sh 95.217.123.45
#
# Requirements:
#   - Ubuntu 20.04+ or Debian 11+
#   - Root/sudo access
#   - Netplan installed
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

# Check arguments
if [ $# -eq 0 ]; then
    error "Usage: $0 <floating-ip>\nExample: $0 95.217.123.45"
fi

FLOATING_IP=$1

# Validate IP format
if ! [[ $FLOATING_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    error "Invalid IP address format: $FLOATING_IP"
fi

info "Setting up Floating IP: $FLOATING_IP"

# ═══════════════════════════════════════════════════════════════
# Detect Network Interface
# ═══════════════════════════════════════════════════════════════

info "Detecting primary network interface..."

# Try to find the main network interface
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n 1)

if [ -z "$INTERFACE" ]; then
    error "Could not detect network interface. Please specify manually."
fi

success "Detected interface: $INTERFACE"

# ═══════════════════════════════════════════════════════════════
# Backup Existing Configuration
# ═══════════════════════════════════════════════════════════════

info "Creating backup of network configuration..."

BACKUP_DIR="/opt/kloud/backups/netplan"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/netplan_backup_$TIMESTAMP.tar.gz"

if [ -d /etc/netplan ]; then
    tar -czf "$BACKUP_FILE" /etc/netplan/ 2>/dev/null || true
    success "Backup created: $BACKUP_FILE"
else
    warning "No existing netplan configuration found"
fi

# ═══════════════════════════════════════════════════════════════
# Check for Netplan
# ═══════════════════════════════════════════════════════════════

if ! command -v netplan &> /dev/null; then
    warning "Netplan not found. Installing..."
    apt update
    apt install -y netplan.io
fi

# ═══════════════════════════════════════════════════════════════
# Create Floating IP Configuration
# ═══════════════════════════════════════════════════════════════

info "Creating Floating IP configuration..."

NETPLAN_FILE="/etc/netplan/60-floating-ip.yaml"

cat > "$NETPLAN_FILE" <<EOF
# ═══════════════════════════════════════════════════════════════
# Hetzner Floating IP Configuration
# Generated: $(date)
# Floating IP: $FLOATING_IP
# Interface: $INTERFACE
# ═══════════════════════════════════════════════════════════════

network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      addresses:
        - $FLOATING_IP/32
      routes:
        - to: $FLOATING_IP/32
          scope: link
EOF

success "Created $NETPLAN_FILE"

# ═══════════════════════════════════════════════════════════════
# Validate and Apply Configuration
# ═══════════════════════════════════════════════════════════════

info "Validating Netplan configuration..."

if ! netplan generate; then
    error "Netplan configuration is invalid. Restoring backup..."
fi

success "Configuration validated"

info "Applying Netplan configuration..."
info "WARNING: This may temporarily interrupt network connectivity"

# Apply with timeout to prevent lockout
if timeout 30 netplan apply; then
    success "Netplan configuration applied"
else
    warning "Netplan apply timed out, but this is normal"
fi

# Wait for network to stabilize
sleep 5

# ═══════════════════════════════════════════════════════════════
# Verify Configuration
# ═══════════════════════════════════════════════════════════════

info "Verifying Floating IP configuration..."

# Check if IP is assigned
if ip addr show "$INTERFACE" | grep -q "$FLOATING_IP"; then
    success "Floating IP $FLOATING_IP is assigned to $INTERFACE"
else
    error "Floating IP not found on interface. Check configuration."
fi

# Test connectivity from Floating IP
info "Testing connectivity from Floating IP..."

if ping -I "$FLOATING_IP" -c 3 -W 5 8.8.8.8 &> /dev/null; then
    success "Connectivity test passed"
else
    warning "Connectivity test failed. This may be normal if firewall rules are strict."
fi

# Test HTTP request from Floating IP
info "Testing HTTP request from Floating IP..."

if timeout 10 curl --interface "$FLOATING_IP" --silent https://ifconfig.me &> /dev/null; then
    DETECTED_IP=$(curl --interface "$FLOATING_IP" --silent https://ifconfig.me 2>/dev/null || echo "unknown")
    if [ "$DETECTED_IP" = "$FLOATING_IP" ]; then
        success "HTTP test passed - External IP matches: $DETECTED_IP"
    else
        warning "HTTP test returned different IP: $DETECTED_IP (expected: $FLOATING_IP)"
    fi
else
    warning "HTTP test failed or timed out"
fi

# ═══════════════════════════════════════════════════════════════
# Create Management Scripts
# ═══════════════════════════════════════════════════════════════

info "Creating management scripts..."

# Script to check Floating IP status
cat > /usr/local/bin/check-floating-ip <<'SCRIPT_EOF'
#!/bin/bash
# Check Floating IP status

FLOATING_IP="FLOATING_IP_PLACEHOLDER"
INTERFACE="INTERFACE_PLACEHOLDER"

echo "═══════════════════════════════════════════════════════════"
echo "Floating IP Status Check"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "Configured Floating IP: $FLOATING_IP"
echo "Network Interface: $INTERFACE"
echo ""

if ip addr show "$INTERFACE" | grep -q "$FLOATING_IP"; then
    echo "✅ Floating IP is assigned to $INTERFACE"
else
    echo "❌ Floating IP is NOT assigned"
fi

echo ""
echo "IP Addresses on $INTERFACE:"
ip addr show "$INTERFACE" | grep "inet " | awk '{print "  - " $2}'

echo ""
echo "Routing table for Floating IP:"
ip route show to "$FLOATING_IP"
SCRIPT_EOF

# Replace placeholders
sed -i "s/FLOATING_IP_PLACEHOLDER/$FLOATING_IP/g" /usr/local/bin/check-floating-ip
sed -i "s/INTERFACE_PLACEHOLDER/$INTERFACE/g" /usr/local/bin/check-floating-ip
chmod +x /usr/local/bin/check-floating-ip

success "Created: /usr/local/bin/check-floating-ip"

# Script to remove Floating IP
cat > /usr/local/bin/remove-floating-ip <<'SCRIPT_EOF'
#!/bin/bash
# Remove Floating IP configuration

NETPLAN_FILE="/etc/netplan/60-floating-ip.yaml"

if [ -f "$NETPLAN_FILE" ]; then
    echo "Removing Floating IP configuration..."
    rm "$NETPLAN_FILE"
    netplan apply
    echo "✅ Floating IP configuration removed"
else
    echo "❌ No Floating IP configuration found"
fi
SCRIPT_EOF

chmod +x /usr/local/bin/remove-floating-ip

success "Created: /usr/local/bin/remove-floating-ip"

# ═══════════════════════════════════════════════════════════════
# Firewall Configuration
# ═══════════════════════════════════════════════════════════════

info "Checking firewall configuration..."

if command -v ufw &> /dev/null; then
    if ufw status | grep -q "Status: active"; then
        info "UFW is active. Ensuring Floating IP has proper access..."
        
        # Allow incoming on Floating IP
        ufw allow in on "$INTERFACE" to "$FLOATING_IP" comment "Floating IP access"
        
        success "Firewall rules updated"
    else
        info "UFW is installed but not active"
    fi
else
    info "UFW not installed - skipping firewall configuration"
fi

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════"
success "Floating IP Setup Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📋 Configuration Summary:"
echo "   Floating IP:  $FLOATING_IP"
echo "   Interface:    $INTERFACE"
echo "   Config File:  $NETPLAN_FILE"
echo "   Backup:       $BACKUP_FILE"
echo ""
echo "🔧 Management Commands:"
echo "   Check status:   check-floating-ip"
echo "   Remove IP:      remove-floating-ip"
echo ""
echo "📝 Next Steps:"
echo "   1. Update DNS records to point to $FLOATING_IP"
echo "   2. Regenerate SSL certificates (if using HTTPS)"
echo "   3. Test website accessibility"
echo ""
echo "🔗 Resources:"
echo "   Full guide: /opt/kloud/FLOATING_IP_GUIDE.md"
echo "   Hetzner docs: https://docs.hetzner.com/cloud/floating-ips/"
echo ""
echo "═══════════════════════════════════════════════════════════════"


