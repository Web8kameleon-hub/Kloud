# Kloud Cloud SDK

Complete client libraries for the Kloud Cloud API (part of UltraWebThinking/Euroweb).

## 📦 Available SDKs

### Python SDK (`kloud_sdk.py`)
- **Language**: Python 3.7+
- **Dependencies**: `requests`
- **Type Hints**: Full type annotation support
- **Features**:
  - Synchronous requests
  - Automatic Bearer JWT authentication
  - File upload support (EEG, audio)
  - Streaming support
  - Context manager support (`with` statement)

### TypeScript/JavaScript SDK (`kloud_sdk.ts`)
- **Language**: TypeScript 4.0+ (compiled to ES2020)
- **Dependencies**: None (uses native `fetch` API)
- **Environment**: Node.js 18+ or modern browsers
- **Features**:
  - Promise-based async/await
  - Automatic timeout with AbortController
  - Dual file upload (browser & Node.js)
  - Form data handling
  - Zero external dependencies

## 🚀 Quick Start

### Python

```python
from kloud_sdk import KloudClient

# Initialize client
client = KloudClient(
    base_url="https://api.kloud.com",
    token="your-jwt-token-here"
)

# Check health
health = client.health()
print(f"Status: {health['status']}")

# Ask a question
answer = client.ask("Çfarë është Kloud?")
print(f"Answer: {answer['answer']}")

# Start data stream
stream = client.alba_streams_start(
    stream_id="my-stream",
    channels=["C3", "C4", "Pz"],
    sampling_rate_hz=256
)

# Get stream data
data = client.alba_streams_data(stream["stream_id"], limit=100)
print(f"Data points: {len(data['data_points'])}")

# Stop stream
client.alba_streams_stop(stream["stream_id"])
client.close()
```

### TypeScript/JavaScript

```typescript
import KloudClient from './kloud_sdk';

// Initialize client
const client = new KloudClient({
  baseUrl: "https://api.kloud.com",
  token: "your-jwt-token-here"
});

// Check health
const health = await client.health();
console.log(`Status: ${health.status}`);

// Ask a question
const answer = await client.ask("Çfarë është Kloud?");
console.log(`Answer: ${answer.answer}`);

// Start data stream
const stream = await client.albaStreamsStart(
  "my-stream",
  256,
  ["C3", "C4", "Pz"]
);

// Get stream data
const data = await client.albaStreamsData(stream.stream_id, 100);
console.log(`Data points: ${data.data_points.length}`);

// Stop stream
await client.albaStreamsStop(stream.stream_id);
```

## 📚 API Reference

### Health & Status Endpoints

#### `health()`
System health check.
```python
response = client.health()
# { "status": "healthy", "timestamp": "2024-01-15T10:30:00Z" }
```

#### `status()`
Full system status.
```python
response = client.status()
# { "status": "operational", "uptime": 3600, "version": "2.1.0" }
```

#### `db_ping()` / `dbPing()`
Database connectivity test.
```python
response = client.db_ping()
```

#### `redis_ping()` / `redisPing()`
Redis connectivity test.
```python
response = client.redis_ping()
```

---

### Ask & Neural Symphony

#### `ask(question, context=None, include_details=True)`
Query the AI assistant.

**Parameters:**
- `question` (string): Your question
- `context` (string, optional): Additional context
- `include_details` (bool): Include reasoning details

**Returns:** `{ "answer": "...", "confidence": 0.95, "details": {...} }`

```python
answer = client.ask(
    question="Cila është frekuenca e valëve Alfen?",
    context="In the context of EEG analysis",
    include_details=True
)
```

#### `neural_symphony(save_to=None)` / `neuralSymphony()`
Generate EEG alpha wave audio.

**Returns:** WAV audio bytes

```python
# Python
audio = client.neural_symphony(save_to="alpha_waves.wav")

# TypeScript
const audio = await client.neuralSymphony();
```

---

### File Uploads

#### `upload_eeg(file_path)` / `uploadEeg(filePath)` or `uploadEegBrowser(file)`
Process EEG file.

**Parameters:**
- `file_path` (string): Path to .edf or .csv file

**Returns:** `{ "status": "processing", "job_id": "...", "duration_ms": 2341 }`

```python
# Python
result = client.upload_eeg("patient_data.edf")

# TypeScript (Node.js)
const result = await client.uploadEeg("patient_data.edf");

# TypeScript (Browser)
const file = document.getElementById('eegInput').files[0];
const result = await client.uploadEegBrowser(file);
```

#### `upload_audio(file_path)` / `uploadAudio(filePath)` or `uploadAudioBrowser(file)`
Process audio file.

```python
result = client.upload_audio("speech_sample.wav")
```

---

### Brain Engine

#### `brain_youtube_insight(video_id)` / `brainYoutubeInsight(videoId)`
Analyze YouTube video for EEG patterns.

```python
insight = client.brain_youtube_insight("dQw4w9WgXcQ")
# { "rhythm": "60-90 bpm", "engagement": 0.87, "harmony": "major" }
```

#### `brain_harmony(file_path)` / `brainHarmony(filePath)`
Analyze harmonic structure of audio.

```python
result = client.brain_harmony("audio_sample.wav")
# { "harmony_type": "harmonic", "frequency": 432, "scale": "A440" }
```

#### `brain_cortex_map()` / `brainCortexMap()`
Get neural architecture map.

```python
map_data = client.brain_cortex_map()
```

#### `brain_temperature()` / `brainTemperature()`
Module thermal stress metrics.

```python
temp = client.brain_temperature()
# { "module": "main", "celsius": 42.3, "status": "normal" }
```

#### `brain_restart()` / `brainRestart()`
Safely restart cognitive modules.

```python
result = client.brain_restart()
# { "status": "restarting", "estimate_ms": 5000 }
```

---

### ALBA Data Collection

#### `alba_status()` / `albaStatus()`
Check ALBA module status.

```python
status = client.alba_status()
# { "status": "running", "streams": 3, "total_points": 1024000 }
```

#### `alba_streams_start(stream_id, sampling_rate_hz=256, channels=None, ...)`
Start data collection stream.

**Parameters:**
- `stream_id` (string): Unique stream identifier
- `sampling_rate_hz` (int, default 256): Sampling rate
- `channels` (list, default ["C3", "C4"]): Channel names
- `description` (string, optional): Stream description
- `metadata` (dict, optional): Additional metadata

**Returns:** `{ "stream_id": "...", "status": "active", "created_at": "..." }`

```python
stream = client.alba_streams_start(
    stream_id="session-001",
    sampling_rate_hz=256,
    channels=["C3", "C4", "Pz", "Oz"],
    description="Meditation session",
    metadata={"participant_id": "P001"}
)
```

#### `alba_streams_stop(stream_id)` / `albaStreamsStop(streamId)`
Stop data collection.

```python
result = client.alba_streams_stop("session-001")
# { "stream_id": "session-001", "status": "stopped", "duration_ms": 60000 }
```

#### `alba_streams_list()` / `albaStreamsList()`
List all active streams.

```python
streams = client.alba_streams_list()
# { "streams": [...], "count": 5, "total_data_points": 5120000 }
```

#### `alba_streams_data(stream_id, limit=100)` / `albaStreamsData(streamId, limit)`
Retrieve stream data.

**Parameters:**
- `stream_id` (string): Stream identifier
- `limit` (int): Max data points to return

**Returns:** `{ "data_points": [...], "count": 100, "stream_id": "..." }`

```python
data = client.alba_streams_data("session-001", limit=500)
for point in data["data_points"]:
    print(f"Timestamp: {point['timestamp']}, C3: {point['channels']['C3']}")
```

#### `alba_metrics()` / `albaMetrics()`
Get collection metrics.

```python
metrics = client.alba_metrics()
# { "total_streams": 15, "total_data_points": 15360000, "avg_sample_rate": 256 }
```

---

## 🔐 Authentication

### Setting Token

```python
# Python
client = KloudClient(token="your-jwt-token")
# Or set later
client.set_token("new-token")

# TypeScript
const client = new KloudClient({ token: "your-jwt-token" });
client.setToken("new-token");
```

### Token Format

Tokens are JWT Bearer tokens in the format:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Getting a Token

Contact your administrator or use the login endpoint:
```bash
curl -X POST https://api.kloud.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

---

## 📋 Error Handling

### Python

```python
from requests.exceptions import RequestException

try:
    result = client.ask("Question")
except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Message: {e.response.json()}")
except RequestException as e:
    print(f"Request failed: {e}")
finally:
    client.close()
```

### TypeScript

```typescript
try {
  const result = await client.ask("Question");
} catch (error) {
  if (error instanceof Error) {
    console.error(`Error: ${error.message}`);
  }
}
```

---

## 🛠️ Development

### Building TypeScript SDK

```bash
# Install TypeScript
npm install -D typescript

# Compile to JavaScript
tsc kloud_sdk.ts --target ES2020 --module ESNext --declaration

# Output: kloud_sdk.js, kloud_sdk.d.ts
```

### Testing SDKs

```bash
# Python
python -m pytest tests/

# TypeScript
npm test
```

---

## 📦 Distribution

### Python Package (PyPI)

```bash
# Create distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### NPM Package

```bash
# Initialize package
npm init

# Publish to NPM
npm publish
```

---

## 🌍 Base URLs

- **Production**: `https://api.kloud.com`
- **Staging**: `https://staging.kloud.cloud`
- **Development**: `http://localhost:8000`
- **Sandbox**: `https://sandbox.kloud.cloud`

---

## 📞 Support

For issues or questions:
- **Documentation**: https://docs.kloud.com
- **API Spec**: See `openapi.yaml`, `openapi.json`, `openapi.cbor`
- **Postman Collection**: Import `kloud-postman-collection.json`

---

## 📄 License

Part of UltraWebThinking/Euroweb. See LICENSE file.

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Organization**: UltraWebThinking / Euroweb / Kloud

