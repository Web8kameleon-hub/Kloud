# Kloud Blog Paywall Service

Premium content access control with Stripe subscriptions.

## Subscription Tiers

| Tier | Price | Features |
| ------ | ------- | ---------- |
| **Free** | 0€ | Public blog posts, Basic docs, Community |
| **Basic** | 9€/month | Premium articles, Technical deep dives |
| **Pro** | 29€/month | Whitepapers, Private Discord, Early access |
| **Enterprise** | 199€/month | 1:1 calls, Architecture reviews, Priority support |

## API Endpoints

### Get Tiers

```bash
GET /api/tiers
```

### Create Subscription

```bash
POST /api/subscribe
Content-Type: application/json

{
  "email": "user@example.com",
  "tier": "pro"
}
```

### Check Subscription

```bash
GET /api/subscription/{email}
```

### Check Content Access

```bash
POST /api/access/check
Content-Type: application/json

{
  "article_id": "alda-labor-array-whitepaper",
  "user_token": "user@example.com"
}
```

### Set Article Tier (Admin)

```bash
POST /api/articles/{article_id}/tier?tier=pro
```

## Environment Variables

```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...
PAYWALL_SECRET=your-secret-key
```

## Docker

```bash
docker build -t kloud-blog-paywall .
docker run -p 8020:8020 \
  -e STRIPE_SECRET_KEY=sk_live_... \
  kloud-blog-paywall
```

## Premium Articles Configuration

Articles are configured with required tiers:

```python
# Basic tier (9€/month)
"eeg-signal-processing-deep-dive"
"neural-mesh-architecture"
"healthcare-ai-compliance"

# Pro tier (29€/month)
"alda-labor-array-whitepaper"
"liam-binary-algebra-guide"
"distributed-inference-patterns"

# Enterprise tier (199€/month)
"kloud-architecture-blueprint"
"custom-integration-guide"
```

## Stripe Webhook Setup

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://api.kloud.com/webhook/stripe`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
4. Copy webhook secret to `STRIPE_WEBHOOK_SECRET`

---

© 2026 Kloud - ABA GmbH

