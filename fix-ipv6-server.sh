#!/bin/bash
# IPv6 Fix Script for Kloud Server
# Fixes UFW, NGINX, and tests both IPv4 and IPv6

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          🔧 KLOUD IPv6 FIX SCRIPT                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Enable UFW IPv6
echo "1️⃣ ENABLING UFW IPv6..."
if grep -q "IPV6=no" /etc/default/ufw; then
    sed -i 's/IPV6=no/IPV6=yes/' /etc/default/ufw
    echo "   ✅ Changed IPV6=no → IPV6=yes"
elif grep -q "IPV6=yes" /etc/default/ufw; then
    echo "   ✅ Already enabled: IPV6=yes"
else
    echo "IPV6=yes" >> /etc/default/ufw
    echo "   ✅ Added IPV6=yes"
fi

# 2. Open ports for IPv6
echo ""
echo "2️⃣ OPENING PORTS 80 & 443..."
ufw allow 80/tcp > /dev/null 2>&1
ufw allow 443/tcp > /dev/null 2>&1
ufw reload > /dev/null 2>&1
echo "   ✅ Ports 80 & 443 opened for IPv4 & IPv6"

# 3. Check UFW status
echo ""
echo "3️⃣ UFW STATUS:"
ufw status verbose | grep -E "(Status|IPv6|80|443)" | sed 's/^/   /'

# 4. Fix NGINX configuration
echo ""
echo "4️⃣ FIXING NGINX IPv6 LISTENING..."

NGINX_CONF="/etc/nginx/sites-available/kloud.com"

if [ -f "$NGINX_CONF" ]; then
    # Backup original
    cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%s)"
    
    # Check if [::]:80 exists
    if grep -q "listen \[::\]:80" "$NGINX_CONF"; then
        echo "   ✅ IPv6 listen already configured"
    else
        # Add IPv6 listen after IPv4 listen
        sed -i '/listen 80;/a\    listen [::]:80;' "$NGINX_CONF"
        echo "   ✅ Added: listen [::]:80;"
    fi
    
    # Check if [::]:443 exists (if SSL configured)
    if grep -q "listen 443" "$NGINX_CONF"; then
        if ! grep -q "listen \[::\]:443" "$NGINX_CONF"; then
            sed -i '/listen 443/a\    listen [::]:443 ssl;' "$NGINX_CONF"
            echo "   ✅ Added: listen [::]:443 ssl;"
        fi
    fi
    
    # Test NGINX config
    echo ""
    echo "   Testing NGINX configuration..."
    if nginx -t 2>&1 | grep -q "successful"; then
        echo "   ✅ NGINX config test PASSED"
        systemctl reload nginx
        echo "   ✅ NGINX reloaded"
    else
        echo "   ❌ NGINX config test FAILED"
        echo "   Restoring backup..."
        mv "$NGINX_CONF.backup."* "$NGINX_CONF"
        nginx -t
    fi
else
    echo "   ⚠️ $NGINX_CONF not found"
fi

# 5. Test IPv4 connectivity
echo ""
echo "5️⃣ TESTING IPv4 CONNECTIVITY..."
if curl -4 -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost | grep -q "200"; then
    echo "   ✅ IPv4 localhost: WORKING"
else
    echo "   ⚠️ IPv4 localhost: FAILED"
fi

if curl -4 -s -o /dev/null -w "%{http_code}" --max-time 5 http://kloud.com | grep -q "200"; then
    echo "   ✅ IPv4 kloud.com: WORKING"
else
    echo "   ⚠️ IPv4 kloud.com: FAILED"
fi

if curl -4 -s -o /dev/null -w "%{http_code}" --max-time 5 http://www.kloud.com | grep -q "200"; then
    echo "   ✅ IPv4 www.kloud.com: WORKING"
else
    echo "   ⚠️ IPv4 www.kloud.com: FAILED"
fi

# 6. Test IPv6 connectivity
echo ""
echo "6️⃣ TESTING IPv6 CONNECTIVITY..."

if curl -6 -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost 2>/dev/null | grep -q "200"; then
    echo "   ✅ IPv6 localhost: WORKING"
else
    echo "   ⚠️ IPv6 localhost: FAILED (this is OK if only external IPv6 matters)"
fi

echo "   Testing external IPv6..."
if curl -6 -s -o /dev/null -w "%{http_code}" --max-time 10 http://kloud.com 2>/dev/null | grep -q "200"; then
    echo "   ✅ IPv6 kloud.com: WORKING"
else
    echo "   ❌ IPv6 kloud.com: TIMEOUT (main issue!)"
fi

if curl -6 -s -o /dev/null -w "%{http_code}" --max-time 10 http://www.kloud.com 2>/dev/null | grep -q "200"; then
    echo "   ✅ IPv6 www.kloud.com: WORKING"
else
    echo "   ❌ IPv6 www.kloud.com: TIMEOUT"
fi

# 7. Test API endpoint
echo ""
echo "7️⃣ TESTING API ENDPOINT..."
if curl -s --max-time 5 http://localhost:8000/health 2>/dev/null | grep -q "ok\|alive\|healthy"; then
    echo "   ✅ FastAPI (port 8000): RUNNING"
else
    echo "   ⚠️ FastAPI (port 8000): NOT RESPONDING"
fi

if curl -s --max-time 5 http://localhost/api/health 2>/dev/null | grep -q "ok\|alive\|healthy"; then
    echo "   ✅ NGINX proxy /api/: WORKING"
else
    echo "   ⚠️ NGINX proxy /api/: NOT RESPONDING"
fi

# 8. Check NGINX listening
echo ""
echo "8️⃣ NGINX LISTENING PORTS:"
netstat -tlnp | grep nginx | grep -E ":80|:443" | sed 's/^/   /'

# 9. Summary
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    FIX SUMMARY                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if curl -6 -s -o /dev/null -w "%{http_code}" --max-time 10 http://www.kloud.com 2>/dev/null | grep -q "200"; then
    echo "🎉 SUCCESS! IPv6 is now working!"
    echo ""
    echo "✅ www.kloud.com accessible via IPv6"
    echo "✅ Browser timeout should be FIXED"
    echo "✅ Postman monitor should PASS"
    echo ""
    echo "Next steps:"
    echo "1. Test in browser: https://www.kloud.com"
    echo "2. Re-run Postman monitor"
    echo "3. Celebrate! 🎊"
else
    echo "⚠️ IPv6 still has issues"
    echo ""
    echo "Possible causes:"
    echo "1. IPv6 routing issue from Hetzner (upstream)"
    echo "2. Firewall beyond UFW blocking IPv6"
    echo "3. IPv6 not fully configured on network interface"
    echo ""
    echo "Recommended next steps:"
    echo "1. Check: ip -6 addr show"
    echo "2. Check: ip -6 route"
    echo "3. Contact Hetzner support about IPv6 connectivity"
    echo "4. OR: Remove AAAA record from DNS (IPv4-only workaround)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Script completed: $(date)"
echo "═══════════════════════════════════════════════════════════════"
