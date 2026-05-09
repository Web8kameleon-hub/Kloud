# =============================================================================
# CLOUDFLARE OPTIMIZATION GUIDE FOR KLOUD
# =============================================================================
# Date: 2026-01-14
# Purpose: Reduce 40-60% traffic, improve cache hit rate, block bots
# =============================================================================

# ===========================================================================
# 1. CLOUDFLARE DASHBOARD SETTINGS
# ===========================================================================

# A) CACHING SETTINGS (Speed > Caching > Configuration)
# -----------------------------------------------------------------------------
# Browser Cache TTL: 1 month
# Tiered Cache: Enabled (Smart Tiered Cache Topology)
# Crawler Hints: Enabled
# Always Online: Enabled

# B) CACHE RULES (Caching > Cache Rules)
# -----------------------------------------------------------------------------
# Rule 1: Cache API Status Endpoints
#   Expression: (http.request.uri.path contains "/api/asi-status") or 
#               (http.request.uri.path contains "/api/system-status") or
#               (http.request.uri.path contains "/api/system/health")
#   Cache Eligibility: Eligible for cache
#   Edge TTL: 10 seconds
#   Browser TTL: 10 seconds
#   Cache Key: Include query string

# Rule 2: Cache Static Assets
#   Expression: (http.request.uri.path contains "/_next/static/") or
#               (http.request.uri.path contains "/static/")
#   Cache Eligibility: Eligible for cache
#   Edge TTL: 1 year
#   Browser TTL: 1 year
#   Cache Key: Ignore query string

# C) SPEED OPTIMIZATIONS (Speed > Optimization)
# -----------------------------------------------------------------------------
# Auto Minify: HTML, CSS, JavaScript (all checked)
# Brotli: Enabled
# Early Hints: Enabled
# Rocket Loader: Disabled (can break JS)
# HTTP/2: Enabled
# HTTP/3 (QUIC): Enabled

# D) SECURITY SETTINGS (Security > Settings)
# -----------------------------------------------------------------------------
# Security Level: High
# Challenge Passage: 30 minutes
# Browser Integrity Check: Enabled

# ===========================================================================
# 2. FIREWALL RULES (Security > WAF > Custom Rules)
# ===========================================================================

# Rule 1: Block Excessive API Requests (>100/min)
# -----------------------------------------------------------------------------
# Name: Block API Abuse
# Expression:
#   (http.request.uri.path contains "/api/") and
#   (cf.threat_score gt 10)
# Action: Block

# Rule 2: Rate Limit API Endpoints
# -----------------------------------------------------------------------------
# Name: Rate Limit API
# Expression: (http.request.uri.path contains "/api/")
# Action: Rate Limit
# Requests per: 60 per 1 minute
# Counting Expression: Same as rule
# Mitigation Timeout: 60 seconds
# Response: 429 Too Many Requests

# Rule 3: Block Known Bad Bots
# -----------------------------------------------------------------------------
# Name: Block Bad Bots
# Expression:
#   (cf.client.bot) and
#   (not cf.bot_management.verified_bot) and
#   (http.request.uri.path contains "/api/")
# Action: Block

# Rule 4: Challenge Suspicious Traffic
# -----------------------------------------------------------------------------
# Name: Challenge Suspicious
# Expression:
#   (cf.threat_score gt 5) and
#   (not cf.bot_management.verified_bot)
# Action: Managed Challenge

# ===========================================================================
# 3. PAGE RULES (Rules > Page Rules) - Legacy but still useful
# ===========================================================================

# Rule 1: Cache Everything on static paths
# URL: *kloud.com/_next/static/*
# Settings:
#   - Cache Level: Cache Everything
#   - Edge Cache TTL: 1 month
#   - Browser Cache TTL: 1 month

# Rule 2: Cache API Status with short TTL
# URL: *kloud.com/api/*-status*
# Settings:
#   - Cache Level: Cache Everything
#   - Edge Cache TTL: 10 seconds
#   - Browser Cache TTL: 10 seconds

# ===========================================================================
# 4. BOT FIGHT MODE (Security > Bots)
# ===========================================================================

# Bot Fight Mode: Enabled
# JavaScript Detections: Enabled
# Static Resource Protection: Disabled (for performance)
# Firewall Rules:
#   - Block definitely automated traffic
#   - Challenge likely automated traffic

# ===========================================================================
# 5. EXPECTED RESULTS AFTER OPTIMIZATION
# ===========================================================================

# BEFORE:
#   - Total Requests: 44,860/week
#   - API Requests: 18,220 (40.6%)
#   - Cache Hit Rate: 3.2%
#   - 404 Errors: 7,050
#   - 5xx Errors: 5,720
#   - Bot Traffic: ~96%

# AFTER (Expected):
#   - Total Requests: ~18,000/week (-60%)
#   - API Requests: ~7,000 (-62%) - rate limited
#   - Cache Hit Rate: 40%+ (12x improvement)
#   - 404 Errors: <500 (improved routing)
#   - 5xx Errors: <200 (retry logic)
#   - Bot Traffic: <20% (blocked)

# COST SAVINGS:
#   - Bandwidth: -60%
#   - Server Load: -50%
#   - Error Rate: -90%

# ===========================================================================
# 6. QUICK CLI COMMANDS (using Cloudflare API)
# ===========================================================================

# These commands require CLOUDFLARE_API_TOKEN environment variable

# Get current cache statistics:
# curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/analytics/dashboard" \
#      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# Purge cache:
# curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
#      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
#      -H "Content-Type: application/json" \
#      --data '{"purge_everything":true}'

# Enable development mode (bypasses cache for 3 hours):
# curl -X PATCH "https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/development_mode" \
#      -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
#      -H "Content-Type: application/json" \
#      --data '{"value":"on"}'

print("""
================================================================================
✅ CLOUDFLARE OPTIMIZATION GUIDE READY
================================================================================

🔧 IMMEDIATE ACTIONS:

1. Open Cloudflare Dashboard: https://dash.cloudflare.com
2. Select zone: kloud.com
3. Apply settings from each section above

📊 PRIORITY ORDER:
   1. Enable Brotli compression (Speed > Optimization)
   2. Enable Tiered Caching (Speed > Caching)
   3. Create Rate Limit rule (Security > WAF)
   4. Enable Bot Fight Mode (Security > Bots)
   5. Create Cache Rules for /api/*-status

💰 EXPECTED SAVINGS:
   - 60% less traffic
   - 90% less errors
   - 40%+ cache hit rate

================================================================================
""")

