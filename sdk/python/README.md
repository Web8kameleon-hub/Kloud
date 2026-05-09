# Kloud Python SDK

Official Python SDK for Kloud Cloud API - Neural harmonic processing, EEG analysis, and ASI Trinity integration.

## Installation

```bash
pip install kloud
```

## Quick Start

```python
from kloud import Kloud

client = Kloud(api_key="your-api-key")

# Check system health
health = client.core.health()
print(f"Status: {health['status']}")

# Get ASI Trinity status
asi = client.asi.status()
print(f"ASI Active: {asi['asi_active']}")
```

## API Modules

### Core API

System health and status endpoints.

```python
# Health check
health = client.core.health()

# Detailed status
status = client.core.status()

# Ping
pong = client.core.ping()
```

### Brain API

Neural harmonic processing and analysis.

```python
# Analyze harmonics
analysis = client.brain.analyze_harmonics(
    frequencies=[8, 10, 12, 14],
    amplitudes=[0.5, 0.8, 0.6, 0.4]
)

# Get brain sync metrics
sync = client.brain.get_sync()

# Cortex analysis
cortex = client.brain.analyze_cortex(
    pattern_data=[0.1, 0.5, 0.3, 0.8, 0.2],
    analysis_type="deep"
)

# Ask AI assistant
response = client.brain.ask(
    "What does increased alpha wave activity indicate?"
)
```

### EEG API

EEG data collection and processing.

```python
# Start recording session
session = client.eeg.start_session(channels=8, sample_rate=256)

# Get session data
data = client.eeg.get_session_data(session["session_id"])

# Analyze frequencies
frequencies = client.eeg.analyze_frequencies(session["session_id"])

# Stop session
client.eeg.stop_session(session["session_id"])
```

### ASI API

ASI Trinity system interface (ALBA, ALBI, JONA).

```python
# Get ASI status
status = client.asi.status()

# Get component metrics
alba = client.asi.alba_metrics()
albi = client.asi.albi_metrics()
jona = client.asi.jona_metrics()

# Trigger sync
client.asi.sync()
```

### Billing API

Payment and subscription management.

```python
# Get available plans
plans = client.billing.get_plans()

# Get current subscription
subscription = client.billing.get_subscription()

# Create checkout session
checkout = client.billing.create_checkout("pro")

# Get usage stats
usage = client.billing.get_usage()
```

### Reporting API (Port 8001)

Docker and system metrics.

```python
# Get Docker containers
containers = client.reporting.docker_containers()
print(f"{containers['total']} containers, {containers['healthy']} healthy")

# Get Docker stats
stats = client.reporting.docker_stats()

# Get system metrics
metrics = client.reporting.system_metrics()
```

### Excel API (Port 8002)

Excel and reporting operations.

```python
# Generate Excel report
report = client.excel.generate_report(
    report_type="monthly_summary",
    format="xlsx"
)

# Get templates
templates = client.excel.get_templates()
```

## Configuration

```python
client = Kloud(
    api_key="your-api-key",
    base_url="https://api.kloud.com",  # Optional
    reporting_url="https://reporting.kloud.com",  # Optional
    excel_url="https://excel.kloud.com",  # Optional
    timeout=30,  # Request timeout in seconds
    retries=3  # Number of retry attempts
)
```

### Environment Variables

```bash
export KLOUD_API_KEY="your-api-key"
```

Then:

```python
from kloud import Kloud

# API key will be read from environment
client = Kloud()
```

## Error Handling

```python
from kloud import (
    Kloud,
    KloudError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError
)

try:
    health = client.core.health()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except NotFoundError:
    print("Resource not found")
except KloudError as e:
    print(f"API Error: {e.message} (code: {e.code})")
```

## CLI Usage

```bash
# Check health
kloud --api-key YOUR_KEY --health

# Get status
kloud --api-key YOUR_KEY --status

# Get ASI status
kloud --api-key YOUR_KEY --asi

# Get Docker containers
kloud --api-key YOUR_KEY --containers
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

