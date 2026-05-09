# 🛡️ Kloud Cloud - Security Documentation

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SECURITY LAYERS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   Layer 1   │    │   Layer 2   │    │   Layer 3   │              │
│  │   Firewall  │───▶│ Rate Limit  │───▶│    Auth     │              │
│  │   (UFW)     │    │  (Helmet)   │    │   (JWT)     │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│         │                  │                  │                      │
│         ▼                  ▼                  ▼                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   Layer 4   │    │   Layer 5   │    │   Layer 6   │              │
│  │    RBAC     │───▶│ Validation  │───▶│  Logging    │              │
│  │ (Roles)     │    │   (Zod)     │    │ (Winston)   │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Authentication

### JWT Token Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  Login   │────▶│  Verify  │────▶│  Token   │
│          │     │ Endpoint │     │ Password │     │ Generated│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                                                    │
     │           ┌────────────────────────────────────────┘
     │           ▼
     │     ┌──────────┐     ┌──────────┐     ┌──────────┐
     └────▶│  Bearer  │────▶│  Verify  │────▶│  Access  │
           │  Token   │     │   JWT    │     │ Granted  │
           └──────────┘     └──────────┘     └──────────┘
```

### Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user123",
    "email": "user@example.com",
    "role": "admin",
    "iat": 1706976000,
    "exp": 1707062400
  }
}
```

### Token Expiration

| Token Type | Expiration | Use Case |
|------------|------------|----------|
| Access Token | 15 minutes | API requests |
| Refresh Token | 7 days | Token renewal |
| API Key | 1 year | Server-to-server |

---

## Authorization (RBAC)

### Roles

| Role | Description | Access Level |
|------|-------------|--------------|
| `guest` | Unauthenticated | Read public only |
| `user` | Authenticated user | Own resources |
| `admin` | Administrator | All resources |
| `superadmin` | Super admin | System config |

### Permissions Matrix

| Resource | Guest | User | Admin | SuperAdmin |
|----------|-------|------|-------|------------|
| Public API | ✅ | ✅ | ✅ | ✅ |
| Own Profile | ❌ | ✅ | ✅ | ✅ |
| All Users | ❌ | ❌ | ✅ | ✅ |
| System Config | ❌ | ❌ | ❌ | ✅ |
| Audit Logs | ❌ | ❌ | ✅ | ✅ |

---

## Rate Limiting

### Configuration (Layer 13)

```typescript
// backend/layers/layer13-gateway/index.ts
export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // 100 requests per window
  message: {
    error: 'RATE_LIMIT_EXCEEDED',
    message: 'Too many requests'
  }
});
```

### Limits by Plan

| Plan | Rate Limit | Burst Limit |
|------|------------|-------------|
| Free | 10/min | 20 |
| Pro | 100/min | 200 |
| Enterprise | 1000/min | 2000 |

---

## Input Validation

### Zod Schemas (Layer 16)

```typescript
// backend/layers/layer16-validation/index.ts
export const ChatInputSchema = z.object({
  message: z.string()
    .min(1, 'Message required')
    .max(10000, 'Message too long')
    .transform(sanitize),
  session_id: z.string().uuid().optional(),
  options: z.object({
    temperature: z.number().min(0).max(2).default(0.7),
    max_tokens: z.number().min(1).max(4096).default(1024)
  }).optional()
});
```

### XSS Prevention

```typescript
import DOMPurify from 'isomorphic-dompurify';

export function sanitize(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: []
  });
}
```

### SQL Injection Prevention

- All database queries use parameterized statements
- ORMs (Prisma/Drizzle) handle escaping automatically
- Input validated before reaching database layer

---

## Security Headers (Helmet)

```typescript
// Enabled security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    }
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
  noSniff: true,
  xssFilter: true
}));
```

---

## Secrets Management

### Environment Variables

```bash
# Never commit these to git!
JWT_SECRET=your-256-bit-secret
DB_PASSWORD=database-password
API_ENCRYPTION_KEY=encryption-key
```

### Storage Rules

| Secret Type | Storage | Rotation |
|-------------|---------|----------|
| JWT Secret | Env var | 90 days |
| DB Password | Env var | 90 days |
| API Keys | Hashed in DB | On request |
| OAuth Tokens | Encrypted DB | Auto |

### Hashing

```typescript
import bcrypt from 'bcryptjs';

// Password hashing
const hash = await bcrypt.hash(password, 12);

// Verification
const isValid = await bcrypt.compare(password, hash);
```

---

## Network Security

### Firewall (UFW)

```bash
# Default rules
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable
ufw enable
```

### Internal Network

```
┌───────────────────────────────────────────┐
│            Docker Network                  │
│  ┌──────────────────────────────────────┐ │
│  │  kloud-cloud_default               │ │
│  │                                        │ │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  │ │
│  │  │ API │──│Redis│──│ DB  │──│Ocean│  │ │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  │ │
│  │                                        │ │
│  └──────────────────────────────────────┘ │
└───────────────────────────────────────────┘
        │                     ▲
        ▼                     │
    ┌───────┐            ┌────────┐
    │ Nginx │◀───────────│Firewall│
    │(Proxy)│            │ (UFW)  │
    └───────┘            └────────┘
        │
        ▼
    [Internet]
```

---

## Audit Logging

### Log Format

```json
{
  "timestamp": "2026-02-03T12:00:00.000Z",
  "level": "info",
  "event": "user.login",
  "user_id": "user123",
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "action": "LOGIN_SUCCESS",
  "metadata": {
    "mfa_used": true,
    "session_id": "sess_abc123"
  }
}
```

### Logged Events

- Authentication (login, logout, failed attempts)
- Authorization (permission denied)
- Data access (read sensitive data)
- Data modification (create, update, delete)
- Admin actions (user management, config changes)

---

## Vulnerability Response

### Reporting

Email: security@kloud.cloud

Please include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Your contact information

### Response Timeline

| Severity | Response | Fix |
|----------|----------|-----|
| Critical | 2 hours | 24 hours |
| High | 24 hours | 7 days |
| Medium | 72 hours | 30 days |
| Low | 7 days | 90 days |

---

## Compliance

### Data Protection

- GDPR compliant (EU data handling)
- User data encrypted at rest
- Data deletion on request
- Privacy policy published

### Security Certifications

- [ ] SOC 2 Type II (Planned)
- [ ] ISO 27001 (Planned)
- [x] TLS 1.3 Enabled
- [x] Regular security audits

---

*Security Documentation v2.0.0 | February 2026*

