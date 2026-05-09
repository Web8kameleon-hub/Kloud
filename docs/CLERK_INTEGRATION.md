# Clerk Integration Guide

## Overview

Kloud uses **Clerk** for user authentication and identity management.
This integration allows Ocean to identify users and provide personalized experiences.

## Architecture

```text
Clerk Auth --> Webhook Handler --> UserRegistry --> Ocean API
(Frontend)     (Port 8070)         (Backend)       (Port 8030)
```

## Setup

### 1. Environment Variables

Add these to your `.env`:

```bash
# Clerk Authentication
CLERK_SECRET_KEY=sk_test_xxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx
```

### 2. Configure Clerk Webhooks

1. Go to Clerk Dashboard
2. Navigate to Webhooks and Add Endpoint
3. Set URL: `https://api.kloud.cloud/webhooks/clerk`
4. Select events: user.created, user.updated, user.deleted
5. Copy the Signing Secret to CLERK_WEBHOOK_SECRET

### 3. Services

- User Management: Port 8070 - Handles Clerk webhooks
- Ocean API: Port 8030 - Main chat API with user context

## API Endpoints

### Webhook Receiver

```bash
POST /webhooks/clerk
```

### Get User by Clerk ID

```bash
GET /api/users/by-clerk/{clerk_id}
```

### Chat with User Context

```bash
POST /api/v1/chat
# Body: {"message": "Hello", "clerk_user_id": "user_xxx"}
```

## Frontend Integration

Use the useOceanChat hook:

```tsx
import { useOceanChat } from '@/hooks/use-ocean-chat';

function ChatComponent() {
  const { messages, sendMessage, isLoading } = useOceanChat();
  await sendMessage("Hello Ocean!");
}
```

## Rate Limits

- FREE: 10 req/min, 1000/hour
- PRO: 100 req/min, Unlimited
- ENTERPRISE: 1000 req/min, Unlimited

## User Data Flow

1. User Signs Up - Clerk creates user, Webhook fires
2. Webhook Received - clerk_webhook.py processes event
3. User Created - UserRegistry.register_user() stores user
4. User Chats - Frontend sends clerk_user_id with request
5. Ocean Receives - Identifies user, personalizes response

## Files

- `services/user-management/clerk_webhook.py` - Webhook handler
- `services/user-management/user_core.py` - User storage
- `ocean-core/user_context.py` - User context for Ocean
- `apps/web/src/hooks/use-ocean-chat.tsx` - Frontend hook

## Testing

```bash
# Start services
docker-compose up user-management ocean-core

# Simulate webhook
curl -X POST http://localhost:8070/webhooks/clerk \
  -H "Content-Type: application/json" \
  -d '{"type":"user.created","data":{"id":"user_test123"}}'

# Verify user
curl http://localhost:8070/api/users/by-clerk/user_test123

# Chat with context
curl -X POST http://localhost:8030/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","clerk_user_id":"user_test123"}'
```

## Troubleshooting

### Webhook not receiving events

- Check Clerk Dashboard for webhook logs
- Verify CLERK_WEBHOOK_SECRET is correct
- Ensure endpoint is publicly accessible

### User not found in chat

- Check if webhook was processed in logs
- Verify clerk_user_id matches exactly
- Check UserRegistry has user entry

### Signature verification failed

- Update CLERK_WEBHOOK_SECRET from Clerk Dashboard
- Ensure headers are forwarded correctly

