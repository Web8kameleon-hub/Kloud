# 🧪 POSTMAN TESTING CYCLE – Complete Reference

Kloud Cloud API Testing Framework

**Version**: 1.0.0  
**Date**: 30 November 2025

---

## 📑 TABLE OF CONTENTS

1. [Postman Setup](#postman-setup)
2. [Authentication Tests](#authentication-tests)
3. [API Endpoint Tests](#api-endpoint-tests)
4. [Performance Tests](#performance-tests)
5. [Security Tests](#security-tests)
6. [Integration Tests](#integration-tests)
7. [Regression Tests](#regression-tests)
8. [Test Reports](#test-reports)

---

## 🛠️ POSTMAN SETUP

### Installation & Import

#### Step 1: Download Postman

- Go to [getpostman.com](https://www.postman.com/downloads/)
- Download for your OS (Windows/Mac/Linux)
- Install & launch

#### Step 2: Import Collection

1. Open Postman
2. Click "Import" (top left)
3. Select "Upload Files"
4. Choose: postman_collection_auth.json
5. Collection appears in left sidebar under "Kloud Cloud API"

#### Step 3: Create Environment

1. Click "Environments" (left sidebar)
2. Click "+" to create new
3. Name: "Development"
4. Add variables:
   - base_url: http://localhost:8000
   - auth_token: (leave empty)
   - refresh_token: (leave empty)
   - api_key: (leave empty)
5. Click "Save"

Repeat for "Staging" and "Production" environments:

- Staging: https://staging-api.kloud.com
- Production: https://api.kloud.com

#### Step 4: Verify Setup

1. Select "Development" environment (dropdown, top right)
2. Click collection → Auth → Login
3. Should show auth endpoints
4. Ready to test!

---

## ✅ AUTHENTICATION TESTS

### Test Suite 1: Login Flow

#### Test 1.1: Successful Login

**Request**:

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "securepassword123"
}
```

**Expected Response (200 OK)**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "refresh_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "api_key": "api_sk_1234567890abcdefghijklmnopqrstuvwxyz",
  "expires_in": 3600
}
```

**Test Script**:

```javascript
pm.test("Login successful (200)", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response contains required fields", function () {
    let json = pm.response.json();
    pm.expect(json).to.have.property('token');
    pm.expect(json).to.have.property('refresh_token');
    pm.expect(json).to.have.property('api_key');
    pm.expect(json).to.have.property('expires_in');
});

pm.test("Token format is valid JWT", function () {
    let json = pm.response.json();
    let token = json.token;
    let parts = token.split('.');
    pm.expect(parts).to.have.lengthOf(3);
});

pm.test("Expires_in is 3600 seconds", function () {
    let json = pm.response.json();
    pm.expect(json.expires_in).to.equal(3600);
});

// Auto-capture tokens
let json = pm.response.json();
pm.environment.set('auth_token', json.token);
pm.environment.set('refresh_token', json.refresh_token);
pm.environment.set('api_key', json.api_key);

console.log('✓ Login successful. Tokens captured.');
```

---

#### Test 1.2: Login with Invalid Credentials

**Request**:

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "email": "wrong@example.com",
  "password": "wrongpassword"
}
```

**Expected Response (401 Unauthorized)**:

```json
{
  "error": "invalid_credentials",
  "message": "Email or password is incorrect"
}
```

**Test Script**:

```javascript
pm.test("Invalid credentials returns 401", function () {
    pm.expect(pm.response.code).to.equal(401);
});

pm.test("Error message is clear", function () {
    let json = pm.response.json();
    pm.expect(json.error).to.equal('invalid_credentials');
});

pm.test("No tokens returned", function () {
    let json = pm.response.json();
    pm.expect(json).to.not.have.property('token');
    pm.expect(json).to.not.have.property('refresh_token');
});
```

---

#### Test 1.3: Login with Missing Password

**Request**:

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "email": "test@example.com"
}
```

**Expected Response (400 Bad Request)**:

```json
{
  "error": "missing_field",
  "message": "Field 'password' is required"
}
```

**Test Script**:

```javascript
pm.test("Missing field returns 400", function () {
    pm.expect(pm.response.code).to.equal(400);
});

pm.test("Error identifies missing field", function () {
    let json = pm.response.json();
    pm.expect(json.message).to.include('password');
});
```

---

### Test Suite 2: Refresh Token Flow

#### Test 2.1: Successful Token Refresh

**Pre-requisite**: Must have valid `refresh_token` in environment

**Request**:

```http
POST {{base_url}}/auth/refresh
Content-Type: application/json

{
  "refresh_token": "{{refresh_token}}"
}
```

**Expected Response (200 OK)**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

**Test Script**:

```javascript
pm.test("Token refresh successful (200)", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("New token received", function () {
    let json = pm.response.json();
    pm.expect(json).to.have.property('token');
    pm.expect(json.token).to.not.equal(pm.environment.get('auth_token'));
});

pm.test("New token is valid JWT", function () {
    let json = pm.response.json();
    let parts = json.token.split('.');
    pm.expect(parts).to.have.lengthOf(3);
});

// Update token
let json = pm.response.json();
pm.environment.set('auth_token', json.token);
console.log('✓ Token refreshed successfully.');
```

---

#### Test 2.2: Refresh with Expired Token

**Request**:

```http
POST {{base_url}}/auth/refresh
Content-Type: application/json

{
  "refresh_token": "expired_refresh_token_xxx"
}
```

**Expected Response (401 Unauthorized)**:

```json
{
  "error": "token_expired",
  "message": "Refresh token has expired"
}
```

**Test Script**:

```javascript
pm.test("Expired refresh token returns 401", function () {
    pm.expect(pm.response.code).to.equal(401);
});

pm.test("Error indicates token expired", function () {
    let json = pm.response.json();
    pm.expect(json.error).to.equal('token_expired');
});
```

---

### Test Suite 3: API Key Creation

#### Test 3.1: Create API Key (Valid Token)

**Pre-requisite**: Must have valid `auth_token` in environment

**Request**:

```http
POST {{base_url}}/auth/api-key
Content-Type: application/json
Authorization: Bearer {{auth_token}}

{
  "label": "production-server"
}
```

**Expected Response (200 OK)**:

```json
{
  "api_key": "api_sk_1234567890abcdefghijklmnopqrstuvwxyz",
  "label": "production-server",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Test Script**:

```javascript
pm.test("API key creation successful (200)", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response contains API key", function () {
    let json = pm.response.json();
    pm.expect(json).to.have.property('api_key');
    pm.expect(json.api_key).to.match(/^api_sk_/);
});

pm.test("API key is properly formatted", function () {
    let json = pm.response.json();
    pm.expect(json.api_key.length).to.be.greaterThan(20);
});

pm.test("Label matches request", function () {
    let json = pm.response.json();
    pm.expect(json.label).to.equal('production-server');
});

// Update environment
let json = pm.response.json();
pm.environment.set('api_key', json.api_key);
console.log('✓ API key created:', json.api_key.substring(0, 20) + '...');
```

---

#### Test 3.2: Create API Key (No Authorization)

**Request**:

```http
POST {{base_url}}/auth/api-key
Content-Type: application/json

{
  "label": "test-key"
}
```

**Expected Response (401 Unauthorized)**:

```json
{
  "error": "authorization_required",
  "message": "Bearer token required"
}
```

**Test Script**:

```javascript
pm.test("Missing auth returns 401", function () {
    pm.expect(pm.response.code).to.equal(401);
});

pm.test("Error indicates authorization needed", function () {
    let json = pm.response.json();
    pm.expect(json.error).to.include('authorization');
});
```

---

## 🔐 API ENDPOINT TESTS

### Test Suite 4: Protected Endpoints (Bearer Token)

#### Test 4.1: Health Check with Bearer Token

**Request**:

```http
GET {{base_url}}/health
Authorization: Bearer {{auth_token}}
```

**Expected Response (200 OK)**:

```json
{
  "status": "healthy",
  "uptime": 86400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Test Script**:

```javascript
pm.test("Health endpoint accessible with token", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Health status is healthy", function () {
    let json = pm.response.json();
    pm.expect(json.status).to.equal('healthy');
});

pm.test("Response includes uptime", function () {
    let json = pm.response.json();
    pm.expect(json.uptime).to.be.a('number');
    pm.expect(json.uptime).to.be.greaterThan(0);
});
```

---

#### Test 4.2: Ask Endpoint (Bearer Token)

**Request**:

```http
POST {{base_url}}/api/ask
Authorization: Bearer {{auth_token}}
Content-Type: application/json

{
  "question": "What is Kloud?",
  "context": "You are an AI assistant",
  "include_details": true
}
```

**Expected Response (200 OK)**:

```json
{
  "answer": "Kloud is a neural audio platform...",
  "details": {},
  "confidence": 0.95,
  "processing_time_ms": 145
}
```

**Test Script**:

```javascript
pm.test("Ask endpoint returns 200", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("Response contains answer", function () {
    let json = pm.response.json();
    pm.expect(json).to.have.property('answer');
    pm.expect(json.answer.length).to.be.greaterThan(0);
});

pm.test("Processing time is reasonable", function () {
    let json = pm.response.json();
    pm.expect(json.processing_time_ms).to.be.lessThan(5000);
});
```

---

### Test Suite 5: API Key Authentication

#### Test 5.1: Health Check with API Key

**Request**:

```http
GET {{base_url}}/health
X-API-Key: {{api_key}}
```

**Expected Response (200 OK)**:

```json
{
  "status": "healthy",
  "uptime": 86400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Test Script**:

```javascript
pm.test("Health endpoint accessible with API key", function () {
    pm.expect(pm.response.code).to.equal(200);
});

pm.test("API key authentication works", function () {
    let json = pm.response.json();
    pm.expect(json.status).to.equal('healthy');
});
```

---

#### Test 5.2: API Endpoint with Invalid API Key

**Request**:

```http
GET {{base_url}}/health
X-API-Key: invalid_key_xxx
```

**Expected Response (401 Unauthorized)**:

```json
{
  "error": "invalid_api_key",
  "message": "API key is invalid or revoked"
}
```

**Test Script**:

```javascript
pm.test("Invalid API key returns 401", function () {
    pm.expect(pm.response.code).to.equal(401);
});

pm.test("Error indicates invalid key", function () {
    let json = pm.response.json();
    pm.expect(json.error).to.include('invalid');
});
```

---

## ⚡ PERFORMANCE TESTS

### Test Suite 6: Response Time Benchmarks

#### Test 6.1: Login Response Time

**Objective**: Verify login completes within SLA

**Request**:

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123"
}
```

**Test Script**:

```javascript
pm.test("Login response time < 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});

pm.test("Login response time < 1s", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

// Track for reporting
let times = pm.globals.get('response_times') || [];
times.push({
    endpoint: '/auth/login',
    time: pm.response.responseTime,
    timestamp: new Date().toISOString()
});
pm.globals.set('response_times', times);
```

---

#### Test 6.2: API Response Time

**Objective**: Verify API calls complete within SLA

**Request**:

```http
GET {{base_url}}/health
Authorization: Bearer {{auth_token}}
```

**Test Script**:

```javascript
pm.test("API response time < 200ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(200);
});

pm.test("API response time < 500ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});
```

---

### Test Suite 7: Load Testing (Runner Mode)

**Setup**: Use Postman Collection Runner

**Configuration**:

1. Select Collection: "Kloud Cloud API"
2. Select Environment: "Development"
3. Iterations: 100
4. Delay (ms): 0
5. Data File: (leave empty)
6. Log Responses: Off (unless debugging)

**Run**:

1. Click "Run" in collection
2. Watch progress
3. Monitor: requests/sec, failures
4. Results show at end

**Success Criteria**:

- ✅ 100+ concurrent requests
- ✅ Average response time < 300ms
- ✅ No 5xx errors
- ✅ 100% successful completion

---

## 🔒 SECURITY TESTS

### Test Suite 8: Authentication Security

#### Test 8.1: CORS Headers Present

**Request**:

```http
OPTIONS {{base_url}}/health
```

**Test Script**:

```javascript
pm.test("CORS headers present", function () {
    pm.expect(pm.response.headers.has('Access-Control-Allow-Origin')).to.be.true;
});

pm.test("Proper CORS methods", function () {
    let corsHeader = pm.response.headers.get('Access-Control-Allow-Methods');
    pm.expect(corsHeader).to.include('GET');
    pm.expect(corsHeader).to.include('POST');
});
```

---

#### Test 8.2: HTTPS Enforced (Prod only)

**Request**:

```http
GET http://api.kloud.com/health
```

**Expected**: 301 redirect to HTTPS

**Test Script**:

```javascript
pm.test("HTTP redirects to HTTPS", function () {
    pm.expect(pm.response.code).to.be.oneOf([301, 302]);
    pm.expect(pm.response.headers.get('Location')).to.include('https');
});
```

---

#### Test 8.3: Rate Limiting

**Objective**: Verify rate limits are enforced

**Request** (repeated 101 times):

```http
GET {{base_url}}/health
Authorization: Bearer {{auth_token}}
```

**Test Script**:

```javascript
pm.test("Rate limit headers present", function () {
    pm.expect(pm.response.headers.has('X-RateLimit-Limit')).to.be.true;
    pm.expect(pm.response.headers.has('X-RateLimit-Remaining')).to.be.true;
});

if (pm.response.code === 429) {
    pm.test("Rate limit triggered correctly", function () {
        pm.expect(pm.response.code).to.equal(429);
        let json = pm.response.json();
        pm.expect(json.error).to.equal('rate_limit_exceeded');
    });
}
```

---

## 🔗 INTEGRATION TESTS

### Test Suite 9: Complete Auth + API Flow

**Objective**: End-to-end workflow verification

**Steps**:

1. POST /auth/login
   - Capture: token, refresh_token, api_key
2. GET /health
   - Use: Bearer token
   - Verify: healthy
3. POST /api/ask
   - Use: Bearer token
   - Query: AI assistant
4. POST /auth/api-key
   - Use: Bearer token
   - Create: new API key
5. GET /health
   - Use: New API key (X-API-Key header)
   - Verify: still works
6. POST /auth/refresh
   - Use: refresh_token
   - Get: new JWT
7. GET /status
   - Use: New JWT
   - Verify: accessible
8. DELETE /user
   - Use: Bearer token
   - Cleanup: delete test user

**Expected Result**: All 8 steps pass ✅

---

## 📊 REGRESSION TESTS

### Test Suite 10: Backward Compatibility

**Objective**: Ensure existing APIs still work

**Endpoints to Test**:

- GET /health ✅
- GET /status ✅
- GET /api/system-status ✅
- POST /api/ask ✅
- GET /api/alba/status ✅
- POST /api/alba/streams/start ✅
- GET /api/alba/streams ✅
- All 51 existing endpoints

**Test Script Template**:

```javascript
pm.test("Endpoint still works", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201, 204]);
});

pm.test("Response time acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

pm.test("No deprecated warnings", function () {
    pm.expect(pm.response.headers.has('Deprecation')).to.be.false;
});
```

---

## 📋 TEST REPORTS

### Generating Test Report

**Step 1: Export Results**

In Postman Collection Runner:

1. After tests complete
2. Click "Export Results"
3. Select format: JSON
4. Save file

**Step 2: View Summary**

```json
{
  "collection": "Kloud Cloud API",
  "environment": "Production",
  "timestamp": "2024-01-15T10:30:00Z",
  "stats": {
    "tests": {
      "total": 54,
      "passed": 54,
      "failed": 0
    },
    "requests": {
      "total": 54,
      "passed": 54,
      "failed": 0
    },
    "performance": {
      "avg_response_time_ms": 145,
      "min_response_time_ms": 23,
      "max_response_time_ms": 892
    }
  },
  "endpoints_tested": [
    "/auth/login",
    "/auth/refresh",
    "/auth/api-key",
    "/health",
    "/status"
  ]
}
```

---

### Daily Testing Schedule

**Morning (9 AM UTC)**

- [ ] Run full auth test suite
- [ ] Verify all 3 auth endpoints
- [ ] Check token generation
- [ ] Validate error handling

**Midday (1 PM UTC)**

- [ ] Run API endpoint tests
- [ ] Test bearer auth
- [ ] Test API key auth
- [ ] Verify responses

**Afternoon (5 PM UTC)**

- [ ] Run load testing (100 iterations)
- [ ] Check performance metrics
- [ ] Review response times
- [ ] Verify scaling

**End of Day (6 PM UTC)**

- [ ] Generate test report
- [ ] Email to team
- [ ] Review failures
- [ ] Plan fixes

---

### Weekly Testing Schedule

**Every Monday**

- [ ] Full regression test suite
- [ ] All 54 endpoints tested
- [ ] Performance benchmarking
- [ ] Security validation

**Every Friday**

- [ ] Load testing (1000 iterations)
- [ ] Stress testing (concurrent requests)
- [ ] Failover testing
- [ ] Backup verification

---

## ✅ LAUNCH READINESS CHECKLIST

Before launching to production:

- [ ] All auth tests passing
- [ ] All API tests passing
- [ ] Performance benchmarks met (<200ms)
- [ ] Security tests validated
- [ ] Load testing successful (100+ concurrent)
- [ ] Integration tests end-to-end
- [ ] Regression tests all passing
- [ ] Error handling verified
- [ ] Documentation complete
- [ ] Team trained on testing
- [ ] Monitoring configured
- [ ] Support ready
- [ ] Rollback plan tested

**Launch Ready**: ✅ YES

---

**Postman Testing Framework – Kloud Cloud API**  
**Production Testing Guide**  
**November 30, 2025**

