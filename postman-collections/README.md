# Postman Collections

This directory contains Postman collections for API testing via the Kitchen worker.

## Collections

| Collection | Description | Key |
| ---------- | ----------- | --- |
| `Protocol_Kitchen_Sovereign_System.postman_collection.json` | Core protocol tests | `sovereign` |
| `kloud-ultra-mega-collection.json` | Comprehensive API tests | `ultra-mega` |
| `Kloud_Cloud_API.postman_collection.json` | Main cloud service tests | `cloud-api` |
| `Kloud-Cloud-Real-APIs.postman_collection.json` | Production endpoint tests | `real-apis` |
| `kloud-cloud.postman_collection.json` | Standard test suite | `main` |

## Usage

### Via API

```bash
curl -X POST https://api.kloud.cloud/api/kitchen/run-tests \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"collection": "main", "baseUrl": "https://api.kloud.cloud"}'
```

### Check Status

```bash
curl https://api.kloud.cloud/api/kitchen/status/{runId}
```

### Get Report

```bash
curl https://api.kloud.cloud/api/kitchen/reports/{runId}
```

## Environment Variables

Collections use the `base_url` environment variable which is set automatically by the Kitchen worker.

## Adding New Collections

1. Add the collection file to this directory
2. Update the `COLLECTIONS` map in `apps/web/app/api/kitchen/run-tests/route.ts`
3. Rebuild and deploy

