# Kloud TypeScript SDK

Official TypeScript SDK for Kloud Cloud API - Neural harmonic processing, EEG analysis, and ASI Trinity integration.

## Installation

```bash
npm install @kloud/sdk
# or
yarn add @kloud/sdk
# or
pnpm add @kloud/sdk
```

## Quick Start

```typescript
import Kloud from '@kloud/sdk';

const kloud = new Kloud({
  apiKey: 'your-api-key'
});

// Check system health
const health = await kloud.core.health();
console.log(`System status: ${health.status}`);

// Get ASI Trinity status
const asiStatus = await kloud.asi.getStatus();
console.log(`ASI Active: ${asiStatus.asi_active}`);
```

## API Modules

### Core API
System health and status endpoints.

```typescript
// Health check
const health = await kloud.core.health();

// Detailed status
const status = await kloud.core.status();

// Ping
const ping = await kloud.core.ping();
```

### Brain API
Neural harmonic processing and analysis.

```typescript
// Analyze harmonics
const analysis = await kloud.brain.analyzeHarmonics({
  frequencies: [8, 10, 12, 14],
  amplitudes: [0.5, 0.8, 0.6, 0.4]
});

// Get brain sync metrics
const sync = await kloud.brain.getSync();

// Cortex analysis
const cortex = await kloud.brain.analyzeCortex({
  pattern_data: [0.1, 0.5, 0.3, 0.8, 0.2],
  analysis_type: 'deep'
});

// Ask AI assistant
const response = await kloud.brain.ask(
  "What does increased alpha wave activity indicate?"
);
```

### EEG API
EEG data collection and processing.

```typescript
// Start recording session
const session = await kloud.eeg.startSession({
  channels: 8,
  sample_rate: 256
});

// Get session data
const data = await kloud.eeg.getSessionData(session.session_id);

// Analyze frequencies
const frequencies = await kloud.eeg.analyzeFrequencies(session.session_id);

// Stop session
await kloud.eeg.stopSession(session.session_id);
```

### ASI API
ASI Trinity system interface (ALBA, ALBI, JONA).

```typescript
// Get ASI status
const status = await kloud.asi.getStatus();

// Get component metrics
const albaMetrics = await kloud.asi.getALBAMetrics();
const albiMetrics = await kloud.asi.getALBIMetrics();
const jonaMetrics = await kloud.asi.getJONAMetrics();

// Trigger sync
await kloud.asi.triggerSync();
```

### Billing API
Payment and subscription management.

```typescript
// Get available plans
const plans = await kloud.billing.getPlans();

// Get current subscription
const subscription = await kloud.billing.getSubscription();

// Create checkout session
const checkout = await kloud.billing.createCheckout('pro');

// Get usage stats
const usage = await kloud.billing.getUsage();
```

### Reporting API (Port 8001)
Docker and system metrics.

```typescript
// Get Docker containers
const containers = await kloud.reporting.getDockerContainers();
console.log(`${containers.total} containers, ${containers.healthy} healthy`);

// Get Docker stats
const stats = await kloud.reporting.getDockerStats();

// Get system metrics
const metrics = await kloud.reporting.getSystemMetrics();
```

### Excel API (Port 8002)
Excel and reporting operations.

```typescript
// Generate Excel report
const report = await kloud.excel.generateReport({
  report_type: 'monthly_summary',
  format: 'xlsx'
});

// Get templates
const templates = await kloud.excel.getTemplates();
```

## Configuration

```typescript
const kloud = new Kloud({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.kloud.com', // Optional, defaults to production
  timeout: 30000, // Optional, request timeout in ms
  retries: 3 // Optional, number of retry attempts
});
```

## Error Handling

```typescript
import { Kloud, KloudError } from '@kloud/sdk';

try {
  const health = await kloud.core.health();
} catch (error) {
  if (error instanceof KloudError) {
    console.error(`API Error: ${error.message}`);
    console.error(`Code: ${error.code}`);
    console.error(`Status: ${error.statusCode}`);
  }
}
```

## TypeScript Support

Full TypeScript support with all types exported:

```typescript
import {
  Kloud,
  HealthResponse,
  ASIStatus,
  BrainSyncResult,
  EEGSession,
  BillingPlan
} from '@kloud/sdk';
```

## Production Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Main API | https://api.kloud.com | Core, Brain, EEG, ASI, Billing |
| Reporting | https://reporting.kloud.com | Docker, System Metrics |
| Excel | https://excel.kloud.com | Excel Reports |
| Frontend | https://kloud.com | Web Dashboard |

## License

MIT © Kloud Cloud

