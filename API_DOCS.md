# Kameleon Life API Documentation

## Endpoints

### Health

- `GET /health`
  - Returns API health status.
  - Response: `{ "status": "ok", "service": "Kameleon Life API" }`

### ASI Trinity Status

- `GET /asi/status`
  - Returns status of ASI Trinity architecture (Alba, Albi, Jona).
  - Response:

    ```json
    {
        "status": "operational",
        "timestamp": "...",
        "trinity": {
          "alba": {"status": "active", "role": "network_monitor", "health": 0.92},
          "albi": {"status": "active", "role": "neural_processor", "health": 0.88},
          "jona": {"status": "active", "role": "data_coordinator", "health": 0.95}
        },
        "system": { "version": "2.1.0", "uptime": 123.45, "instance": "abcd1234" }
    }
    ```

### Usage Tracking

- `GET /api/usage/stats`
  - Returns usage statistics for API keys.

### Billing

- `POST /api/billing/customer`
  - Create Stripe customer.
- `POST /api/billing/subscription`
  - Create Stripe subscription.
- `GET /api/billing/usage`
  - Get Stripe usage for customer.

## Frontend Components

- **PhoneMonitor**: Fetches `/api/asi-status` for real-time device metrics.
- **Dashboard**: Displays health, usage, billing, and system status.

## Configuration

- API port: `8000` (default, configurable in package.json)
- Frontend port: `3000` (Next.js, auto-detects free port)
- Environment variables: `.env` for backend and frontend URLs

## How to Run

- `npm run dev` (starts backend and frontend)
- Backend: FastAPI (Python)
- Frontend: Next.js (React)

## Notes

- All endpoints return real data or error (no mock values).
- CORS enabled for all origins.
- For more endpoints, see backend source code.
