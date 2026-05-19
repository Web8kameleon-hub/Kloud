# Sitemap Submission — Google Search Console & Bing Webmaster

**Production Domain:** https://kameleon.life  
**Sitemap URL:** https://kameleon.life/sitemap.xml  
**Updated:** 2026-05-19T07:31:55.914Z  
**Pages Indexed:** Current deployment

---

## Google Search Console

### 1. Submit via API (Recommended)

```bash
# Requires Google OAuth credentials + Service Account
curl -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fkameleon.life%2F/sitemaps" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sitemap\": \"https://kameleon.life/sitemap.xml\"}"
```

### 2. Submit via Web UI (Quick)

1. Open: https://search.google.com/search-console
2. Select property: **kameleon.life**
3. Left menu → **Sitemaps**
4. Enter URL: `https://kameleon.life/sitemap.xml`
5. Click **Submit**

### 3. Verify Submission

```bash
# Check using Search Console API
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fkameleon.life%2F/sitemaps"
```

**Expected Response:**
```json
{
  "sitemaps": [
    {
      "path": "https://kameleon.life/sitemap.xml",
      "lastSubmitted": "2026-05-19T07:31:55.914Z",
      "lastDownloaded": "2026-05-19T07:31:55.914Z",
      "type": "WEB",
      "isPending": false,
      "isSitemapsIndex": true
    }
  ]
}
```

---

## Bing Webmaster Tools

### 1. Submit via API (Recommended)

```bash
# Bing Webmaster API (requires API key)
curl -X POST \
  "https://www.bing.com/webmaster/api.svc/json/SubmitSitemap?apikey=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"siteUrl\": \"https://kameleon.life\", \"sitemapUrl\": \"https://kameleon.life/sitemap.xml\"}"
```

### 2. Submit via Web UI

1. Open: https://www.bing.com/webmasters/
2. Select site: **kameleon.life**
3. Tools → **Sitemaps**
4. Enter URL: `https://kameleon.life/sitemap.xml`
5. Click **Submit**

### 3. Verify Submission

```bash
# Check using Bing API
curl "https://www.bing.com/webmaster/api.svc/json/GetSitemaps?apikey=YOUR_API_KEY&siteUrl=https://kameleon.life"
```

**Expected Response:**
```json
{
  "d": {
    "sitemaps": [
      {
        "url": "https://kameleon.life/sitemap.xml",
        "lastSubmitted": "2026-05-19T07:31:55Z",
        "lastDownloaded": "2026-05-19T07:31:55Z",
        "status": "Active"
      }
    ]
  }
}
```

---

## Automated Script (Using curl + Environment Variables)

### Google Search Console

```bash
#!/bin/bash

# Set variables
DOMAIN="kameleon.life"
SITEMAP_URL="https://kameleon.life/sitemap.xml"
GOOGLE_ACCESS_TOKEN="${GOOGLE_ACCESS_TOKEN}"  # Set via env

if [ -z "$GOOGLE_ACCESS_TOKEN" ]; then
  echo "❌ GOOGLE_ACCESS_TOKEN not set"
  exit 1
fi

echo "📤 Submitting sitemap to Google Search Console..."
curl -X POST \
  "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2F${DOMAIN}%2F/sitemaps" \
  -H "Authorization: Bearer $GOOGLE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"sitemap\": \"$SITEMAP_URL\"}"

echo "✅ Submitted!"
```

### Bing Webmaster Tools

```bash
#!/bin/bash

# Set variables
DOMAIN="kameleon.life"
SITEMAP_URL="https://kameleon.life/sitemap.xml"
BING_API_KEY="${BING_API_KEY}"  # Set via env

if [ -z "$BING_API_KEY" ]; then
  echo "❌ BING_API_KEY not set"
  exit 1
fi

echo "📤 Submitting sitemap to Bing Webmaster..."
curl -X POST \
  "https://www.bing.com/webmaster/api.svc/json/SubmitSitemap?apikey=$BING_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"siteUrl\": \"https://${DOMAIN}\", \"sitemapUrl\": \"$SITEMAP_URL\"}"

echo "✅ Submitted!"
```

---

## One-Liner Submissions (Web UI)

### Google Search Console
```
https://search.google.com/search-console/sitemaps?resource_id=https%3A%2F%2Fkameleon.life%2F
```

Then paste: `https://kameleon.life/sitemap.xml`

### Bing Webmaster
```
https://www.bing.com/webmasters/home/mysites
```

Then select **kameleon.life** → Tools → Sitemaps → Submit `https://kameleon.life/sitemap.xml`

---

## Status

- ✅ **Sitemap Generated:** `https://kameleon.life/sitemap.xml`
- ✅ **Last Updated:** 2026-05-19T07:31:55.914Z
- ✅ **Sitemap Reachability Check:** HTTP 200 (verified on 2026-05-19)
- ✅ **robots.txt Declaration:** `Sitemap: https://kameleon.life/sitemap.xml` present
- ⏳ **Google Submission:** Pending (manual or API submission required)
- ⏳ **Bing Submission:** Pending (manual or API submission required)

## Important Update (Search Engine Ping)

- Google legacy ping endpoint (`/ping?sitemap=...`) is deprecated and returns 404.
- Bing legacy ping endpoint (`/ping?sitemap=...`) returns 410 Gone.
- Correct method: submit via Google Search Console and Bing Webmaster Tools.

## Next Steps

1. **Authenticate:** Get OAuth tokens from Google Console and Bing API key
2. **Run script:** Use automated script to submit both sitemaps
3. **Monitor:** Check Search Console & Webmaster Tools for indexation status
4. **Recrawl:** Usually triggered within 24 hours of submission

---

**Note:** Bing typically recrawls faster than Google. Expect recrawl start within 24-48 hours.
