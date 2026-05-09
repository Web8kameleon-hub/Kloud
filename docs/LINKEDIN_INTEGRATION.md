# 🔗 LinkedIn Integration Guide for Kloud

## Quick Setup (5 minutes)

### Step 1: Create LinkedIn App

1. Go to: **<https://www.linkedin.com/developers/apps>**
2. Click **"Create App"**
3. Fill in:
   - **App name**: `Kloud Content Factory`
   - **LinkedIn Page**: Select your company page (ABA GmbH / Kloud)
   - **App logo**: Upload Kloud logo
   - **Legal agreement**: ✓ Check

### Step 2: Request Access Products

After creating the app:

1. Go to **Products** tab
2. Request these products:
   - ✅ **Share on LinkedIn** (instant approval)
   - ✅ **Sign In with LinkedIn using OpenID Connect** (instant)
   - ⚠️ **Marketing Developer Platform** (requires approval for organization posting)

### Step 3: Get Credentials

Go to **Auth** tab and copy:

```text
Client ID: xxxxxxxxxxxx
Client Secret: xxxxxxxxxxxx
```

### Step 4: Configure Redirect URI

In **Auth** tab → **OAuth 2.0 settings**:

- Add: `https://kloud.com/api/linkedin/callback`

### Step 5: Set Environment Variables

On your server:

```bash
export LINKEDIN_CLIENT_ID="your_client_id"
export LINKEDIN_CLIENT_SECRET="your_client_secret"
export LINKEDIN_REDIRECT_URI="https://kloud.com/api/linkedin/callback"
export LINKEDIN_ORGANIZATION_URN="urn:li:organization:111866162"
```

### Step 6: Connect LinkedIn

1. Start the LinkedIn OAuth server:

   ```bash
   cd services/content-factory
   python linkedin_oauth_server.py
   ```

2. Visit: `https://kloud.com/api/linkedin/auth`
3. Authorize the app
4. Save the access token

---

## Organization URN

Your LinkedIn Company Page ID: **111866162**
Full URN: `urn:li:organization:111866162`

---

## API Endpoints

| Endpoint                  | Method | Description      |
| ------------------------- | ------ | ---------------- |
| `/api/linkedin/auth`      | GET    | Start OAuth flow |
| `/api/linkedin/callback`  | GET    | OAuth callback   |
| `/api/linkedin/post`      | POST   | Create post      |
| `/api/linkedin/posts`     | GET    | Get recent posts |

---

## Post Example

```bash
curl -X POST "https://kloud.com/api/linkedin/post" \
  -H "Content-Type: application/json" \
  -d '{
    "commentary": "🧠 Introducing Kloud Cloud\n\nAI-Powered Industrial Intelligence Platform\n\n✅ Real-time EEG Analysis\n✅ Curiosity Ocean AI Assistant\n✅ 63+ Research Articles\n\n#AI #MedTech #IndustrialAI",
    "article_url": "https://kloud.com",
    "article_title": "Kloud Cloud - AI Intelligence Platform",
    "article_description": "Industrial AI platform for EEG analysis and compliance"
  }'
```

---

## Permissions Required

| Permission               | Description                    |
| ------------------------ | ------------------------------ |
| `w_organization_social`  | Post on behalf of organization |
| `r_organization_social`  | Read organization posts        |
| `rw_organization_admin`  | Admin access                   |

---

## Rate Limits

- **10 posts per hour** per organization
- **3000 characters** max per post
- Access tokens expire in **60 days**

---

## Auto-Publishing with CLX Publisher

The `clx_publisher.py` module integrates with LinkedIn:

```python
from clx_publisher import ContentPublisher, Platform

publisher = ContentPublisher()
publisher.configure_platform(Platform.LINKEDIN, access_token="your_token")

# Publish EAP document to LinkedIn
results = await publisher.publish(
    eap_document,
    platforms=[Platform.LINKEDIN]
)
```

---

## Troubleshooting

### "Access token not configured"

→ Run OAuth flow: `/api/linkedin/auth`

### "Insufficient permissions"

→ Request **Marketing Developer Platform** product

### "Organization not found"

→ Verify you're admin of the company page

### "Rate limit exceeded"

→ Wait 1 hour between batches

---

## Support

- LinkedIn Developer Portal: <https://www.linkedin.com/developers/>
- API Documentation: <https://learn.microsoft.com/en-us/linkedin/marketing/>
- Kloud Support: <support@kloud.com>

