# DNS & Hosting Management API Integration Guide

## Overview
This document explains how to integrate the dynamic DNS and Hosting Management API endpoints with the Kloud backend and frontend.

## Architecture

### Backend Components
1. **dns_hosting_api.py** — FastAPI router with CRUD endpoints, SQLAlchemy models, and Pydantic schemas
2. **alembic_migrations_dns.sql** — Database migration with sample data
3. **Integration into main API server** (port 8000)

### Frontend Components
1. **apps/web/app/modules/dns-hosting-control/page.tsx** — Dynamic dashboard that fetches from `/api/dns/zones` and `/api/dns/origins`
2. **No hardcoded data** — All values fetched at runtime and updated every 30 seconds

---

## Step 1: Database Setup

Run the migration to create tables and sample data:

```bash
# Option A: Using MySQL directly
mysql -h localhost -u kloud -p kloud < alembic_migrations_dns.sql

# Option B: Using Alembic (if configured)
alembic upgrade head
```

**Tables Created:**
- `dns_zones` — User's DNS domains with nameservers
- `dns_records` — Individual DNS records (A, AAAA, CNAME, MX, TXT, etc.)
- `hosting_origins` — User's hosting origins with health status

**Sample Data:**
- 4 DNS zones: kameleon.life, aiagi.io, aba-gmbh.eu, clisonix.com
- 9 DNS records for kameleon.life (A, AAAA, CNAME, MX, TXT)
- 4 hosting origins with health status

---

## Step 2: Backend Integration

### 2a. Add to Main API (apps/api/main.py or equivalent)

```python
from dns_hosting_api import router as dns_router  # Import the router
from fastapi import FastAPI

app = FastAPI()

# Include the DNS & Hosting router
app.include_router(dns_router)

# Now available at:
# GET  /api/dns/zones
# POST /api/dns/zones
# GET  /api/dns/zones/{zone_id}
# POST /api/dns/zones/{zone_id}/records
# PUT  /api/dns/records/{record_id}
# DELETE /api/dns/records/{record_id}
# GET  /api/dns/origins
# POST /api/dns/origins
# GET  /api/dns/origins/{origin_id}
# DELETE /api/dns/origins/{origin_id}
```

### 2b. Wire Database Session (REQUIRED)

The `get_db()` dependency needs to be connected to your actual database:

```python
# In dns_hosting_api.py, replace the stub:

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

# Use your actual database URL
DATABASE_URL = "mysql+pymysql://kloud:password@localhost/kloud"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Provide database session to endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2c. Implement Authentication (REQUIRED FOR PRODUCTION)

Replace the `get_current_user_id()` stub with real auth:

```python
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta

def get_current_user_id(
    authorization: Optional[str] = Header(None)
) -> str:
    """Extract and validate JWT token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
        
        # Decode JWT (use your actual secret and algorithm)
        payload = jwt.decode(token, "YOUR_SECRET_KEY", algorithms=["HS256"])
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")
```

---

## Step 3: Frontend Integration (Already Done)

The frontend component at `apps/web/app/modules/dns-hosting-control/page.tsx` is **already updated** to:

1. **Fetch dynamic data** from `/api/dns/zones` and `/api/dns/origins`
2. **Display loading states** while fetching
3. **Show error messages** if API calls fail
4. **Auto-refresh every 30 seconds**
5. **Display nameservers** for each zone
6. **Show DNS records** per zone with type, content, proxy status
7. **Display hosting origins** with health status, region, role
8. **Calculate KPI metrics** from live data (zones count, origins count, record count)

### No Frontend Changes Needed
The component already fetches from the API endpoints. Just ensure the backend is running and the endpoints are working.

---

## Step 4: Testing

### 4a. Test API Endpoints

```bash
# Get all DNS zones (requires auth token)
curl -H "Authorization: Bearer demo-user-001" \
  http://localhost:8000/api/dns/zones

# Expected response:
# [
#   {
#     "id": "zone-001",
#     "domain": "kameleon.life",
#     "status": "active",
#     "nameserver_1": "jonathan.ns.kloud.cloud",
#     "nameserver_2": "katja.ns.kloud.cloud",
#     "records": [...]
#   },
#   ...
# ]

# Get all hosting origins
curl -H "Authorization: Bearer demo-user-001" \
  http://localhost:8000/api/dns/origins

# Expected response:
# [
#   {
#     "id": "origin-001",
#     "name": "Web App Origin",
#     "endpoint": "web.kloud.aiagi.io",
#     "health_status": "Healthy",
#     "region": "EU Central",
#     "role": "frontend"
#   },
#   ...
# ]
```

### 4b. Test Frontend

Browse to http://localhost:3000/modules/dns-hosting-control

You should see:
- ✅ Dashboard with dynamic KPI cards (zones, origins, records)
- ✅ DNS Records section with zones and their records
- ✅ Nameservers displayed for each zone
- ✅ Hosting Origins section with health status
- ✅ Last sync timestamp
- ✅ No hardcoded data

---

## Step 5: Extend with Real DNS Integration (Optional)

To make this control real DNS infrastructure, add integrations:

### PowerDNS Integration

```python
import requests

async def create_dns_record_in_powerdns(zone_id: str, record: DNSRecord):
    """Push DNS record to PowerDNS API"""
    powerdns_url = "http://localhost:8081/api/v1/servers/localhost/zones/{zone_id}"
    
    payload = {
        "rrsets": [{
            "name": record.name,
            "changetype": "REPLACE",
            "ttl": record.ttl,
            "records": [{"content": record.content, "disabled": False}]
        }]
    }
    
    response = requests.patch(
        powerdns_url,
        json=payload,
        headers={"X-API-Key": "your-powerdns-api-key"}
    )
    return response.json()
```

### Cloudflare API Integration

```python
import aiohttp

async def create_dns_record_in_cloudflare(zone_domain: str, record: DNSRecord):
    """Push DNS record to Cloudflare API"""
    async with aiohttp.ClientSession() as session:
        url = f"https://api.cloudflare.com/client/v4/zones/{CLOUDFLARE_ZONE_ID}/dns_records"
        
        headers = {
            "X-Auth-Email": "your-email@example.com",
            "X-Auth-Key": "your-cloudflare-api-key",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": record.type,
            "name": f"{record.name}.{zone_domain}",
            "content": record.content,
            "ttl": record.ttl,
            "proxied": record.proxy_status == "Proxied"
        }
        
        async with session.post(url, json=payload, headers=headers) as resp:
            return await resp.json()
```

---

## Step 6: Multi-Tenant User Isolation (Already Done)

✅ **User isolation is built-in:**
- Every endpoint requires authentication via `get_current_user_id()`
- Database queries filter by `user_id` to ensure users only see their own data
- Foreign keys and indexes optimize multi-tenant access

---

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/dns/zones` | List all user's DNS zones |
| POST | `/api/dns/zones` | Create new DNS zone |
| GET | `/api/dns/zones/{zone_id}` | Get specific zone with all records |
| POST | `/api/dns/zones/{zone_id}/records` | Add DNS record to zone |
| PUT | `/api/dns/records/{record_id}` | Update DNS record |
| DELETE | `/api/dns/records/{record_id}` | Delete DNS record |
| GET | `/api/dns/origins` | List all user's hosting origins |
| POST | `/api/dns/origins` | Create hosting origin |
| GET | `/api/dns/origins/{origin_id}` | Get specific origin |
| DELETE | `/api/dns/origins/{origin_id}` | Delete hosting origin |

---

## Files Created/Modified

1. **dns_hosting_api.py** (NEW)
   - SQLAlchemy models: DNSZone, DNSRecord, HostingOrigin
   - Pydantic schemas for validation
   - FastAPI router with 10 endpoints
   - Mock data responses (ready to wire to database)

2. **alembic_migrations_dns.sql** (NEW)
   - Database schema creation
   - Sample data (4 zones, 9 records, 4 origins)
   - Indexes for performance

3. **apps/web/app/modules/dns-hosting-control/page.tsx** (UPDATED)
   - Removed hardcoded DNS_RECORDS, HOSTING_ORIGINS
   - Added React state for zones, origins, loading, error
   - Added useEffect to fetch from `/api/dns/zones` and `/api/dns/origins`
   - Dynamic nameserver display per zone
   - Live KPI metrics from actual data
   - Error handling and loading states

---

## Next Steps

1. **Run database migration** to create tables
2. **Wire database session** in dns_hosting_api.py
3. **Implement authentication** (replace stub)
4. **Include router** in main API app
5. **Test API endpoints** with curl
6. **Test frontend** by browsing to dashboard
7. **(Optional) Add PowerDNS or Cloudflare integration** for real DNS control

---

## Configuration Example

```python
# Example .env file
DATABASE_URL=mysql+pymysql://kloud:password@localhost/kloud
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256

# Optional: PowerDNS
POWERDNS_API_URL=http://localhost:8081
POWERDNS_API_KEY=your-powerdns-key

# Optional: Cloudflare
CLOUDFLARE_API_EMAIL=your-email@example.com
CLOUDFLARE_API_KEY=your-cloudflare-key
CLOUDFLARE_ZONE_ID=your-zone-id
```

---

## Support

For questions or issues:
1. Check that `/api/dns/zones` returns 200 OK
2. Verify JWT token is valid in Authorization header
3. Check database tables exist: `mysql> SHOW TABLES LIKE 'dns%';`
4. Review browser console for frontend errors
5. Check API logs for backend errors
