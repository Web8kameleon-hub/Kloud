# KLOUD NANOGRIDATA PROTOCOL v1.0 - PRODUCTION DEPLOYMENT GUIDE

**Status:** ✅ PRODUCTION READY  
**Date:** 2026-01-17  
**Version:** 1.0.0  
**Security Level:** MILITARY-GRADE (0x03)

---

## 📋 TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [Security Features](#security-features)
3. [Implementation Guide](#implementation-guide)
4. [Deployment Instructions](#deployment-instructions)
5. [Integration with Ocean Core](#integration-with-ocean-core)
6. [Testing & Validation](#testing--validation)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ ARCHITECTURE OVERVIEW

### DNA Model: Unified Core + Flexible Profiles

```
┌─────────────────────────────────────────────────────────────┐
│              NANOGRIDATA PROTOCOL v1.0 (DNA)                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  CORE (Genotypic):                                           │
│  ├─ Binary Frame Header (14 bytes)                          │
│  ├─ CBOR Payload Encoding                                   │
│  ├─ HMAC-SHA256 / AES-256-GCM MAC                          │
│  └─ Timestamp Validation                                    │
│                                                               │
│  PROFILES (Phenotypic):                                      │
│  ├─ ESP32-PRESSURE (0x10) → Pressure sensors              │
│  ├─ STM32-GAS (0x20) → Gas concentration                  │
│  ├─ ASIC-MULTI (0x30) → Multi-sensor                      │
│  ├─ Raspberry Pi (0x40) → Computing node                  │
│  └─ CUSTOM (0xFF) → User-defined                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Frame Structure

```
HEADER (14 bytes):
  ├─ Magic: 0xC1 0x53 (Kloud signature)
  ├─ Version: 0x01
  ├─ Model ID: 0x10-0xFF (chip/lab identifier)
  ├─ Payload Type: TELEMETRY | CONFIG | EVENT | COMMAND | CALIBRATION
  ├─ Flags: Security level (0x00-0x03)
  ├─ Length: Payload size (big-endian, 2 bytes)
  ├─ Timestamp: Unix epoch (big-endian, 4 bytes)
  └─ Reserved: 0x0000 (2 bytes)

PAYLOAD (variable):
  └─ CBOR-encoded data (max 1024 bytes)

MAC (variable):
  ├─ Security 0x00: CRC-16 (2 bytes)
  ├─ Security 0x01: HMAC-SHA256 (16 bytes)
  ├─ Security 0x02: HMAC-SHA256 (32 bytes)
  └─ Security 0x03: HMAC-SHA256 + Timestamp (32 bytes)
```

---

## 🔐 SECURITY FEATURES

### 1. CBOR Injection Prevention

**Problem:** Unvalidated CBOR decoding can lead to code injection  
**Solution:** Strict size limits and tag restrictions

```typescript
// ✓ SECURE DECODING
const decoded = cbor.decodeFirstSync(payload, {
  maxStrLength: 256,        // Prevent large string allocations
  maxArrayLength: 64,       // Prevent array DoS
  maxKeys: 20,              // Limit object keys
  tags: new Map()           // Disable custom CBOR tags
});
```

### 2. Replay Attack Prevention

**Problem:** Same packet can be processed multiple times  
**Solution:** TTL-based nonce cache

```typescript
// Cache format: "modelId-timestamp" → expiry_time
private replayCache: Map<string, number>;

// Check before processing
if (this.replayCache.has(key)) {
  throw new Error('Replay attack detected');
}
```

### 3. Timing-Safe MAC Comparison

**Problem:** String comparison leaks timing information  
**Solution:** Use `timingSafeEqual`

```typescript
// ✗ VULNERABLE
if (packet.mac === expectedMac) { /* ... */ }

// ✓ SECURE
timingSafeEqual(packet.mac, expectedMac)
```

### 4. Mandatory Shared Secrets

**Problem:** Default secrets compromise security  
**Solution:** Require secret on initialization

```typescript
constructor(sharedSecret: Buffer) {
  if (!sharedSecret || sharedSecret.length < 32) {
    throw new Error('Shared secret required (min 32 bytes)');
  }
  // ...
}
```

### 5. Strict Timestamp Validation

**Problem:** Packets with old timestamps can bypass validation  
**Solution:** Allow ±1 hour drift, reject future packets

```typescript
const drift = Math.abs(header.timestamp - now);
if (drift > 3600) {
  throw new Error(`Timestamp drift too large: ${drift}s`);
}
```

---

## 📦 IMPLEMENTATION GUIDE

### Server-Side (Node.js/TypeScript)

#### 1. Install Dependencies

```bash
npm install cbor cryptography dotenv
npm install --save-dev typescript @types/node @types/cbor
```

#### 2. Configure Environment

```bash
# .env
ESP32_SECRET=strong_secret_key_32bytes_minimum_required!
STM32_SECRET=another_strong_secret_key_for_stm32!!
INFLUX_URL=http://localhost:8086
INFLUX_TOKEN=your_token_here
INFLUX_ORG=Kloud
INFLUX_BUCKET=nanogridata
DATABASE_URL=postgresql://user:pass@localhost/nanogridata
```

#### 3. Initialize Decoder

```typescript
import { NanogridataSecureDecoder, ModelID } from './nanogridata_secure_decoder';

const secrets = new Map<number, Buffer>([
  [ModelID.ESP32_PRESSURE, Buffer.from(process.env.ESP32_SECRET!)],
  [ModelID.STM32_GAS, Buffer.from(process.env.STM32_SECRET!)],
]);

const decoder = new NanogridataSecureDecoder(secrets);
```

#### 4. Process Incoming Packets

```typescript
// Receive raw packet from network
const rawPacket = receivedData; // Buffer

// Deserialize with full validation
const result = decoder.deserialize(rawPacket);

if (!result.valid) {
  console.error(`Invalid packet: ${result.error}`);
  return;
}

// Decode CBOR payload
const payload = decoder.decodePayloadCBOR(result.packet!);

// Process further
console.log(`Packet from model 0x${result.packet!.header.modelId.toString(16)}`);
console.log(`Payload:`, payload);
```

### Embedded-Side (ESP32/STM32)

#### 1. Configure for Target Platform

```c
// For ESP32:
#define ESP32
#include "nanogridata_config.h"
#include "nanogridata_protocol_v1.c"

// For STM32:
#define STM32
#include "nanogridata_config.h"
#include "nanogridata_protocol_v1.c"
```

#### 2. Create and Send Packet

```c
#include "nanogridata_protocol_v1.c"

void send_sensor_data(uint32_t pressure_pa) {
  // Initialize packet
  nanogridata_packet_t packet;

  // Build payload (telemetry format)
  uint8_t payload[NANOGRIDATA_MAX_PAYLOAD];
  int offset = build_pressure_telemetry(
    payload,
    "ESP32-001",
    "LAB-HETZNER-01",
    time(NULL),
    pressure_pa
  );

  // Create packet with HMAC security
  uint8_t shared_secret[] = {0xAA, 0xBB, 0xCC, ...}; // 32 bytes minimum
  nanogridata_create_packet(
    &packet,
    MODEL_ESP32_PRESSURE,
    PAYLOAD_TYPE_TELEMETRY,
    payload,
    offset,
    SECURITY_STANDARD,
    shared_secret,
    32
  );

  // Serialize for transmission
  uint8_t tx_buffer[NANOGRIDATA_MAX_PAYLOAD + 50];
  uint16_t tx_size = nanogridata_serialize(&packet, tx_buffer, sizeof(tx_buffer));

  // Send via UART/WiFi/LoRa
  uart_write(tx_buffer, tx_size);
}
```

---

## 🚀 DEPLOYMENT INSTRUCTIONS

### Step 1: Server Setup

```bash
# 1. Clone repository
git clone https://github.com/LedjanAhmati/Kloud-cloud.git
cd Kloud-cloud

# 2. Install dependencies
npm install

# 3. Compile TypeScript
npx tsc nanogridata_secure_decoder.ts ocean_core_adapter.ts

# 4. Setup database
psql -c "CREATE DATABASE nanogridata;"
psql nanogridata < schema.sql  # Create tables

# 5. Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Step 2: Chip Deployment (ESP32)

```c
// platformio.ini
[env:esp32]
platform = espressif32
board = esp32devkitc
framework = arduino
lib_deps = 
  WiFi
  SPIFFS
upload_speed = 921600

// Include in main sketch:
#define ESP32
#include "nanogridata_config.h"
#include "nanogridata_protocol_v1.c"

void setup() {
  Serial.begin(115200);
  nanogridata_init();
}

void loop() {
  uint32_t pressure = read_pressure_sensor();
  send_sensor_data(pressure);
  delay(5000);  // 5 seconds
}
```

### Step 3: Chip Deployment (STM32)

```c
// CubeMX Configuration:
// - UART1: 9600 baud, DMA enabled
// - Timer: RTC for timestamps
// - ADC: Pressure sensor

// Modify nanogridata_config.h:
#define PLATFORM_STM32
#define NANOGRIDATA_MAX_PAYLOAD 256
#define NANOGRIDATA_USE_DMA 1

// In main.c:
#include "nanogridata_config.h"
#include "nanogridata_protocol_v1.c"

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USART1) {
    // Process received packet
    nanogridata_packet_t packet;
    if (nanogridata_deserialize(rx_buffer, rx_size, &packet) == 0) {
      // Valid packet received
      process_command(&packet);
    }
  }
}
```

---

## 🔗 INTEGRATION WITH OCEAN CORE

### 1. Setup Ocean Core Adapter

```typescript
import { OceanCoreAdapter } from './ocean_core_adapter';

const adapter = new OceanCoreAdapter({
  influxUrl: process.env.INFLUX_URL!,
  influxToken: process.env.INFLUX_TOKEN!,
  influxOrg: 'Kloud',
  influxBucket: 'nanogridata',
  databaseUrl: process.env.DATABASE_URL!,
  logLevel: 'info',
});
```

### 2. Register Custom Profiles

```typescript
adapter.registerProfile({
  modelId: 0x50,
  name: 'CUSTOM-SENSOR',
  unit: 'custom_unit',
  validateFunction: (data) => ({ valid: true }),
  decodeFunction: (data) => data,
});
```

### 3. Process Packets

```typescript
// From network packet
const result = decoder.deserialize(rawPacket);

if (result.valid && result.packet) {
  // Process through Ocean Core
  const processed = await adapter.processPacket(
    result.packet,
    result.packet.payload
  );

  if (processed) {
    console.log(`Stored in InfluxDB: ${processed.deviceId}`);
  }
}
```

### 4. Listen to Events

```typescript
adapter.on('packetProcessed', (data) => {
  console.log(`✓ Processed: ${data.deviceId}`);
  // Update dashboard, trigger alerts, etc.
});

adapter.on('processingError', ({ error, packet }) => {
  console.error(`✗ Error: ${error}`);
  // Log, alert, retry logic
});
```

---

## ✅ TESTING & VALIDATION

### Unit Tests

```bash
# Install test dependencies
npm install --save-dev jest @types/jest ts-jest

# Run tests
npm test
```

### Integration Tests

```bash
# Start mock server
npm run test:server

# Send test packets
npm run test:packets

# Verify in InfluxDB
influx query 'from(bucket:"nanogridata") |> range(start: -1h)'
```

### Security Validation

```bash
# Check for vulnerabilities
npm audit

# Run security linter
npm run lint:security

# Verify CBOR limits
npm run test:cbor-limits

# Test replay attack detection
npm run test:replay-attacks

# Verify timing-safe comparison
npm run test:timing-safety
```

---

## 🐛 TROUBLESHOOTING

### Issue 1: MAC Verification Failed

**Cause:** Shared secret mismatch  
**Solution:** Verify secret key on both encoder and decoder

```bash
# Check ESP32 secret matches server config
echo "ESP32 Secret (hex): $(echo -n 'your_secret' | xxd -p)"
```

### Issue 2: CBOR Decode Error

**Cause:** Invalid CBOR encoding or size limit exceeded  
**Solution:** Check payload size

```typescript
if (payload.length > 1024) {
  throw new Error('Payload exceeds CBOR limit');
}
```

### Issue 3: Replay Attack Detected

**Cause:** Same packet received twice within 5 minutes  
**Solution:** Ensure unique timestamps on each packet

```c
uint32_t unique_timestamp = time(NULL);
// Ensure each packet has different timestamp
```

### Issue 4: Timestamp Drift Error

**Cause:** Chip clock out of sync  
**Solution:** Synchronize time via NTP

```c
// ESP32: Enable NTP
#define NANOGRIDATA_ENABLE_NTP 1

// STM32: Set RTC via serial command
void sync_rtc(uint32_t timestamp) {
  // Set RTC to timestamp
}
```

---

## 📊 MONITORING & DIAGNOSTICS

### InfluxDB Queries

```sql
-- Get latest pressure readings
from(bucket:"nanogridata")
  |> filter(fn: (r) => r.profile == "NANO-ESP32-PRESSURE")
  |> range(start: -1h)
  |> last()

-- Count errors by device
from(bucket:"nanogridata")
  |> filter(fn: (r) => r.status == "error")
  |> group(by: ["device_id"])
  |> count()

-- Average pressure per lab
from(bucket:"nanogridata")
  |> filter(fn: (r) => r.profile == "NANO-ESP32-PRESSURE")
  |> range(start: -24h)
  |> group(by: ["lab_id"])
  |> mean()
```

### Logging

```typescript
// Enable debug logging
process.env.LOG_LEVEL = 'debug';

// Check Ocean Core error log
const errors = adapter.getErrorLog();
console.log(`Recent errors: ${errors.length}`);
errors.forEach(({ timestamp, error }) => {
  console.log(`${timestamp}: ${error}`);
});
```

---

## 🎯 PRODUCTION CHECKLIST

- [ ] Shared secrets configured for all model IDs
- [ ] InfluxDB and PostgreSQL databases created
- [ ] Environment variables set (.env file)
- [ ] CBOR size limits tested and validated
- [ ] Replay attack detection enabled
- [ ] Timing-safe comparison verified
- [ ] Timestamp validation configured (±1 hour)
- [ ] Error logging and monitoring setup
- [ ] Database backups configured
- [ ] Security audit completed
- [ ] Load testing performed (1000+ packets/sec)
- [ ] Failover and recovery tested
- [ ] Documentation updated
- [ ] Team training completed

---

## 📞 SUPPORT

For issues or questions:
- GitHub Issues: https://github.com/LedjanAhmati/Kloud-cloud/issues
- Email: support@kloud.com
- Documentation: https://docs.kloud.com/nanogridata

---

**Created:** 2026-01-17  
**Last Updated:** 2026-01-17  
**Maintainer:** Ledjan Ahmati  
**License:** Proprietary (Kloud)

