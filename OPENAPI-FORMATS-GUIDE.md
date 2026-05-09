# OpenAPI Specification – Kloud Cloud API v1.0.0

## 📋 Tre Format Profesional Të Prodhuara

### 1. **openapi.yaml** (49.9 KB)
```
Format: YAML 3.1.0
Qëllimi: Source of truth – human-readable, për redaktim manual
Vegla compatibile: VS Code, OpenAPI editors, spec validators
```

**Përdorimi:**
```bash
# Validate
openapi-generator-cli validate -i openapi.yaml

# Generate SDK
openapi-generator-cli generate -i openapi.yaml -g python -o ./sdk

# Publikim në Swagger UI
swaggerhub api:create Kloud/Cloud-API:1.0.0 openapi.yaml
```

### 2. **openapi.json** (74.2 KB)
```
Format: JSON 3.1.0
Qëllimi: Programmatic use – parsable by machines
Vegla compatibile: Postman, API gateways, SDK generators
```

**Përdorimi:**
```bash
# Import në Postman
# Menu: File > Import > Link → paste JSON URL

# Validate me ajv
ajv compile -s openapi.json

# Transform në Swagger 2.0 (Swagger Hub)
swagger-converter openapi.json > swagger-2.0.json
```

### 3. **openapi.cbor** (28.9 KB)
```
Format: CBOR (Concise Binary Object Representation) RFC 7049
Qëllimi: Embedded systems, IoT devices – minimal bandwidth
Madhësia: 39% të JSON (49% më i vogël)
Vegla compatibile: IoT gateways, edge computing, embedded APIs
```

**Përdorimi (Python):**
```python
import cbor2

# Decrypt CBOR specification
with open('openapi.cbor', 'rb') as f:
    spec = cbor2.load(f)

print(spec['info']['title'])  # 'Kloud Cloud API'
```

**Përdorimi (Node.js):**
```javascript
const cbor = require('cbor');
const fs = require('fs');

fs.readFile('openapi.cbor', (err, data) => {
  const spec = cbor.decode(data);
  console.log(spec.info.title);
});
```

---

## 🔐 Autentikim i Integruar (Të Tre Format)

### Bearer JWT
```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

**Shembull:** 
```bash
curl -H "Authorization: Bearer eyJhbGc..." http://localhost:8000/api/ask
```

### Alternative Authentication
- **API Key:** `X-API-Key: your-api-key`
- **OAuth 2.0:** Client Credentials flow në `/auth/token`

---

## 📊 Struktura E Specifikimit

### Components (Reusable Schemas)
- **16+ ObjectSchemas** për request/response
- **Error handling** – standardized error codes
- **Security schemes** – 3 authentication methods
- **Reusable responses** – DRY principle

### Endpoints (51 Total)
**By Category:**
- Core: 3 endpoints
- Brain: 18 endpoints
- Audio: 8 endpoints
- EEG: 2 endpoints
- ALBA: 9 endpoints
- Billing: 4 endpoints
- ASI: 3 endpoints
- Utility: 4 endpoints

### Request/Response Examples
```json
POST /api/ask
{
  "question": "What is my system status?",
  "context": null,
  "include_details": true
}

200 Response:
{
  "answer": "Your system is operational...",
  "timestamp": "2025-11-30T14:44:00Z",
  "modules_used": ["brain", "cortex"],
  "processing_time_ms": 234,
  "details": {}
}
```

---

## 🛠️ Si T'i Përdorësh Këto Format

### Setup: Postman
1. **Import YAML ose JSON:**
   ```
   File → Import → paste openapi.json URL
   ```
2. **Vendos Bearer token:**
   ```
   Environment → Add variable: token = eyJ...
   Headers: Authorization: Bearer {{token}}
   ```
3. **Test endpoints:**
   ```
   Send → Check 200/401/422 responses
   ```

### Setup: API Gateway (Kong, AWS API GW)
```bash
# Kong
curl -X POST http://kong:8001/apis \
  -F "name=kloud" \
  -F "upstream_url=http://localhost:8000" \
  -F "uris=/api" \
  -d "plugins=openapi-spec" \
  -F "spec=@openapi.json"

# AWS API Gateway
aws apigateway import-rest-api --body file://openapi.json
```

### Setup: SDK Generation
```bash
# Python SDK
openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./kloud-sdk-python

# TypeScript SDK
openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-fetch \
  -o ./kloud-sdk-ts

# Go SDK
openapi-generator-cli generate \
  -i openapi.yaml \
  -g go \
  -o ./kloud-sdk-go
```

---

## 🔄 Rate Limiting & Politika

Të gjithë endpoints kanë:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1701355440
```

**Limits per kategori:**
- General API: 100 req/min
- Brain endpoints: 10 req/min
- Signal processing: 20 req/min
- File uploads: 5 req/min

---

## ✅ Validation & Testing

### Validate YAML/JSON
```bash
# Online validator
https://www.apivalidator.dev/

# Local validator
npm install -g swagger-cli
swagger-cli validate openapi.yaml

# Spectacle
npm install -g spectacle
spectacle openapi.yaml -d ./docs
```

### Postman Collection Test
```bash
newman run kloud.postman_collection.json \
  --environment kloud.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export test-results.json
```

---

## 📚 Dokumentim I Gjeneruar

Të tre formatet kanë:
- ✅ Complete endpoint documentation
- ✅ Request/response schemas
- ✅ Error codes and handling
- ✅ Authentication details
- ✅ Rate limiting info
- ✅ CBOR binary format support
- ✅ Reusable components

---

## 🚀 Hapi Tjetër

Mund të:
1. **Upload në API registry:**
   - SwaggerHub
   - Postman API Network
   - apisprout.io

2. **Generate SDK:**
   - Python, JavaScript, Go, Java, C#
   
3. **Publish Interactive Docs:**
   - ReDoc
   - Swagger UI
   - Spectacle

4. **Setup Monitoring:**
   - Sentry for errors
   - DataDog for metrics
   - New Relic for APM

---

**Të tre formatet janë gati për production! ✅**

- **openapi.yaml** – për developers & editors
- **openapi.json** – për integrations & tools
- **openapi.cbor** – për embedded & IoT systems

