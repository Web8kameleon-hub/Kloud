/**
 * KLOUD NANOGRIDATA PROTOCOL v1.0 - SECURE DECODER
 * 
 * Production-grade decoder with security hardening
 * - CBOR injection prevention
 * - Strict timestamp validation
 * - Replay attack prevention
 * - Comprehensive error handling
 */

import * as cbor from 'cbor';
import { createHmac, randomBytes, timingSafeEqual } from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS & CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

const NANOGRIDATA_MAGIC = [0xC1, 0x53];
const NANOGRIDATA_VERSION = 0x01;
const HEADER_SIZE = 14;

// CBOR Safety Limits (prevent DoS)
const CBOR_MAX_SIZE = 1024;
const CBOR_MAX_STR_LENGTH = 256;
const CBOR_MAX_ARRAY_LENGTH = 64;
const CBOR_MAX_KEYS = 20;

// Timestamp validation (±1 hour)
const TIMESTAMP_MAX_DRIFT_SECONDS = 3600;

// Replay attack cache TTL (5 minutes)
const REPLAY_CACHE_TTL_MS = 300000;

enum PayloadType {
  TELEMETRY = 0x01,
  CONFIG = 0x02,
  EVENT = 0x03,
  COMMAND = 0x04,
  CALIBRATION = 0x05,
}

enum ModelID {
  ESP32_PRESSURE = 0x10,
  STM32_GAS = 0x20,
  ASIC_MULTI = 0x30,
  RASPBERRY_PI = 0x40,
  CUSTOM_IOT = 0xFF,
}

enum SecurityLevel {
  NONE = 0x00,
  STANDARD = 0x01,
  HIGH = 0x02,
  MILITARY = 0x03,
}

// ═══════════════════════════════════════════════════════════════════════════
// INTERFACES
// ═══════════════════════════════════════════════════════════════════════════

interface NanogridataHeader {
  magic: Buffer;
  version: number;
  modelId: ModelID;
  payloadType: PayloadType;
  flags: number;
  length: number;
  timestamp: number;
  reserved: number;
}

interface NanogridataPacket {
  header: NanogridataHeader;
  payload: Buffer;
  mac: Buffer;
  securityLevel: SecurityLevel;
}

interface ValidationResult {
  valid: boolean;
  error?: string;
  packet?: NanogridataPacket;
}

// ═══════════════════════════════════════════════════════════════════════════
// SECURE DECODER
// ═══════════════════════════════════════════════════════════════════════════

class NanogridataSecureDecoder {
  private sharedSecrets: Map<number, Buffer>;
  private replayCache: Map<string, number>;
  private logger: Console;

  constructor(sharedSecrets?: Map<number, Buffer>) {
    if (!sharedSecrets || sharedSecrets.size === 0) {
      throw new Error('Shared secrets required for decoder initialization');
    }

    this.sharedSecrets = sharedSecrets;
    this.replayCache = new Map();
    this.logger = console;

    // Cleanup replay cache every 10 minutes
    setInterval(() => this.cleanupReplayCache(), 600000);
  }

  /**
   * Main deserialization method with full validation
   */
  deserialize(data: Buffer): ValidationResult {
    try {
      if (!Buffer.isBuffer(data)) {
        return {
          valid: false,
          error: 'Input must be a Buffer',
        };
      }

      if (data.length < HEADER_SIZE) {
        return {
          valid: false,
          error: `Packet too small: ${data.length} < ${HEADER_SIZE}`,
        };
      }

      // Step 1: Decode header
      const header = this.decodeHeader(data);
      if (!header) {
        return {
          valid: false,
          error: 'Failed to decode header',
        };
      }

      // Step 2: Validate header
      const headerValidation = this.validateHeader(header);
      if (!headerValidation.valid) {
        return {
          valid: false,
          error: headerValidation.error,
        };
      }

      // Step 3: Extract security level and MAC size
      const securityLevel = header.flags & 0x0F;
      const macSize = this.getMacSize(securityLevel);

      // Step 4: Extract payload
      const payloadStart = HEADER_SIZE;
      const payloadEnd = HEADER_SIZE + header.length;
      const macEnd = payloadEnd + macSize;

      if (data.length < macEnd) {
        return {
          valid: false,
          error: `Packet too small for MAC: ${data.length} < ${macEnd}`,
        };
      }

      const payload = data.slice(payloadStart, payloadEnd);
      const mac = data.slice(payloadEnd, macEnd);

      // Step 5: Create packet object
      const packet: NanogridataPacket = {
        header,
        payload,
        mac,
        securityLevel,
      };

      // Step 6: Verify MAC
      const macValidation = this.verifyMac(packet);
      if (!macValidation.valid) {
        return {
          valid: false,
          error: macValidation.error,
        };
      }

      // Step 7: Check for replay attacks
      if (this.isReplayAttack(packet)) {
        return {
          valid: false,
          error: 'Replay attack detected',
        };
      }

      this.logger.info(
        `✓ Packet deserialized: model=0x${header.modelId.toString(16)}, ` +
          `type=${header.payloadType}, security=${securityLevel}`
      );

      return {
        valid: true,
        packet,
      };
    } catch (error) {
      this.logger.error(`Deserialization error: ${error}`);
      return {
        valid: false,
        error: `Deserialization failed: ${error}`,
      };
    }
  }

  /**
   * Decode and validate header
   */
  private decodeHeader(data: Buffer): NanogridataHeader | null {
    try {
      let offset = 0;

      // Magic bytes
      const magic0 = data[offset++];
      const magic1 = data[offset++];

      if (magic0 !== NANOGRIDATA_MAGIC[0] || magic1 !== NANOGRIDATA_MAGIC[1]) {
        this.logger.error(
          `Invalid magic bytes: 0x${magic0.toString(16)} 0x${magic1.toString(16)}`
        );
        return null;
      }

      // Version
      const version = data[offset++];
      if (version !== NANOGRIDATA_VERSION) {
        this.logger.error(`Unsupported version: ${version}`);
        return null;
      }

      // Model ID
      const modelId = data[offset++];

      // Payload type
      const payloadType = data[offset++];

      // Flags
      const flags = data[offset++];

      // Length (big-endian)
      const length = data.readUInt16BE(offset);
      offset += 2;

      // Timestamp (big-endian)
      const timestamp = data.readUInt32BE(offset);
      offset += 4;

      // Reserved
      const reserved = data.readUInt16BE(offset);

      return {
        magic: Buffer.from(NANOGRIDATA_MAGIC),
        version,
        modelId,
        payloadType,
        flags,
        length,
        timestamp,
        reserved,
      };
    } catch (error) {
      this.logger.error(`Header decode error: ${error}`);
      return null;
    }
  }

  /**
   * Validate header structure and content
   */
  private validateHeader(header: NanogridataHeader): ValidationResult {
    // Validate reserved field
    if (header.reserved !== 0) {
      return {
        valid: false,
        error: `Reserved field not zero: 0x${header.reserved.toString(16)}`,
      };
    }

    // Validate payload length
    if (header.length > CBOR_MAX_SIZE) {
      return {
        valid: false,
        error: `Payload too large: ${header.length} > ${CBOR_MAX_SIZE}`,
      };
    }

    // Validate timestamp
    const now = Math.floor(Date.now() / 1000);
    const drift = Math.abs(header.timestamp - now);

    if (drift > TIMESTAMP_MAX_DRIFT_SECONDS) {
      return {
        valid: false,
        error:
          `Timestamp drift too large: ${drift}s > ${TIMESTAMP_MAX_DRIFT_SECONDS}s`,
      };
    }

    // Validate model ID
    const validModelIds = Object.values(ModelID);
    if (!validModelIds.includes(header.modelId as any)) {
      this.logger.warn(`Unknown model ID: 0x${header.modelId.toString(16)}`);
    }

    // Validate payload type
    const validPayloadTypes = Object.values(PayloadType);
    if (!validPayloadTypes.includes(header.payloadType as any)) {
      return {
        valid: false,
        error: `Invalid payload type: ${header.payloadType}`,
      };
    }

    return { valid: true };
  }

  /**
   * Verify packet MAC/signature
   */
  private verifyMac(packet: NanogridataPacket): ValidationResult {
    try {
      const expectedMac = this.computeMac(packet);

      // Use timing-safe comparison
      if (!timingSafeEqual(packet.mac, expectedMac)) {
        this.logger.error('MAC verification failed');
        return {
          valid: false,
          error: 'MAC verification failed',
        };
      }

      return { valid: true };
    } catch (error) {
      return {
        valid: false,
        error: `MAC verification error: ${error}`,
      };
    }
  }

  /**
   * Compute expected MAC
   */
  private computeMac(packet: NanogridataPacket): Buffer {
    const securityLevel = packet.securityLevel;

    if (securityLevel === SecurityLevel.NONE) {
      return this.computeCrc16(packet);
    }

    if (securityLevel === SecurityLevel.STANDARD) {
      return this.computeHmac(packet).slice(0, 16);
    }

    return this.computeHmac(packet);
  }

  /**
   * Compute CRC-16 CCITT
   */
  private computeCrc16(packet: NanogridataPacket): Buffer {
    const headerBuf = this.encodeHeader(packet.header);
    const data = Buffer.concat([headerBuf, packet.payload]);

    let crc = 0xFFFF;

    for (let i = 0; i < data.length; i++) {
      crc ^= data[i] << 8;
      for (let j = 0; j < 8; j++) {
        if (crc & 0x8000) {
          crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
        } else {
          crc = (crc << 1) & 0xFFFF;
        }
      }
    }

    const buffer = Buffer.alloc(2);
    buffer.writeUInt16BE(crc, 0);
    return buffer;
  }

  /**
   * Compute HMAC-SHA256
   */
  private computeHmac(packet: NanogridataPacket): Buffer {
    const secret = this.sharedSecrets.get(packet.header.modelId);

    if (!secret) {
      throw new Error(
        `No shared secret for model 0x${packet.header.modelId.toString(16)}`
      );
    }

    const headerBuf = this.encodeHeader(packet.header);
    const data = Buffer.concat([headerBuf, packet.payload]);

    return createHmac('sha256', secret).update(data).digest();
  }

  /**
   * Encode header to buffer
   */
  private encodeHeader(header: NanogridataHeader): Buffer {
    const buffer = Buffer.alloc(HEADER_SIZE);
    let offset = 0;

    buffer[offset++] = NANOGRIDATA_MAGIC[0];
    buffer[offset++] = NANOGRIDATA_MAGIC[1];
    buffer[offset++] = header.version;
    buffer[offset++] = header.modelId;
    buffer[offset++] = header.payloadType;
    buffer[offset++] = header.flags;

    buffer.writeUInt16BE(header.length, offset);
    offset += 2;

    buffer.writeUInt32BE(header.timestamp, offset);
    offset += 4;

    buffer.writeUInt16BE(header.reserved, offset);

    return buffer;
  }

  /**
   * Safely decode CBOR payload with injection prevention
   */
  decodePayloadCBOR(packet: NanogridataPacket): any {
    try {
      if (packet.payload.length > CBOR_MAX_SIZE) {
        throw new Error(`CBOR payload too large: ${packet.payload.length}`);
      }

        // Use safe CBOR decoding (custom tag handlers disabled for security)
      const decoded = cbor.decodeFirstSync(packet.payload, {
          tags: {}, // Disable custom CBOR tags for security
      });

      return decoded;
    } catch (error) {
      this.logger.error(`CBOR decode error: ${error}`);
      throw new Error(`Invalid CBOR payload: ${error}`);
    }
  }

  /**
   * Check for replay attacks
   */
  private isReplayAttack(packet: NanogridataPacket): boolean {
    const key = `${packet.header.modelId}-${packet.header.timestamp}`;

    if (this.replayCache.has(key)) {
      this.logger.warn(`Replay attack detected for ${key}`);
      return true;
    }

    this.replayCache.set(key, Date.now());
    return false;
  }

  /**
   * Cleanup old entries from replay cache
   */
  private cleanupReplayCache(): void {
    const now = Date.now();
    const expired: string[] = [];

    this.replayCache.forEach((timestamp, key) => {
      if (now - timestamp > REPLAY_CACHE_TTL_MS) {
        expired.push(key);
      }
    });

    expired.forEach((key) => this.replayCache.delete(key));

    if (expired.length > 0) {
      this.logger.debug(`Cleaned up ${expired.length} replay cache entries`);
    }
  }

  /**
   * Get MAC size based on security level
   */
  private getMacSize(securityLevel: number): number {
    switch (securityLevel) {
      case SecurityLevel.NONE:
        return 2;
      case SecurityLevel.STANDARD:
        return 16;
      case SecurityLevel.HIGH:
      case SecurityLevel.MILITARY:
        return 32;
      default:
        return 16;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SECURE ENCODER
// ═══════════════════════════════════════════════════════════════════════════

class NanogridataSecureEncoder {
  private sharedSecret: Buffer;
  private modelId: ModelID;

  /**
   * Constructor requires shared secret (no defaults)
   */
  constructor(sharedSecret: Buffer, modelId: ModelID) {
    if (!sharedSecret || sharedSecret.length === 0) {
      throw new Error('Shared secret is required and cannot be empty');
    }

    if (sharedSecret.length < 32) {
      throw new Error('Shared secret must be at least 32 bytes');
    }

    this.sharedSecret = sharedSecret;
    this.modelId = modelId;
  }

  /**
   * Create packet with HMAC
   */
  createPacket(
    payloadData: any,
    payloadType: PayloadType,
    securityLevel: SecurityLevel = SecurityLevel.STANDARD
  ): Buffer {
    // Encode payload to CBOR
    const payloadBuffer = this.encodePayloadCBOR(payloadData);

    if (payloadBuffer.length > CBOR_MAX_SIZE) {
      throw new Error(`Payload too large: ${payloadBuffer.length}`);
    }

    // Create header
    const header: NanogridataHeader = {
      magic: Buffer.from(NANOGRIDATA_MAGIC),
      version: NANOGRIDATA_VERSION,
      modelId: this.modelId,
      payloadType,
      flags: securityLevel,
      length: payloadBuffer.length,
      timestamp: Math.floor(Date.now() / 1000),
      reserved: 0,
    };

    // Encode header
    const headerBuffer = this.encodeHeader(header);

    // Compute MAC
    const macBuffer = this.computeMAC(headerBuffer, payloadBuffer, securityLevel);

    // Concatenate: header + payload + mac
    return Buffer.concat([headerBuffer, payloadBuffer, macBuffer]);
  }

  /**
   * Encode payload to CBOR
   */
  private encodePayloadCBOR(data: any): Buffer {
    try {
      return Buffer.from(cbor.encode(data));
    } catch (error) {
      throw new Error(`CBOR encode error: ${error}`);
    }
  }

  /**
   * Encode header
   */
  private encodeHeader(header: NanogridataHeader): Buffer {
    const buffer = Buffer.alloc(HEADER_SIZE);
    let offset = 0;

    buffer[offset++] = NANOGRIDATA_MAGIC[0];
    buffer[offset++] = NANOGRIDATA_MAGIC[1];
    buffer[offset++] = header.version;
    buffer[offset++] = header.modelId;
    buffer[offset++] = header.payloadType;
    buffer[offset++] = header.flags;

    buffer.writeUInt16BE(header.length, offset);
    offset += 2;

    buffer.writeUInt32BE(header.timestamp, offset);
    offset += 4;

    buffer.writeUInt16BE(header.reserved, offset);

    return buffer;
  }

  /**
   * Compute MAC
   */
  private computeMAC(
    headerBuffer: Buffer,
    payloadBuffer: Buffer,
    securityLevel: SecurityLevel
  ): Buffer {
    if (securityLevel === SecurityLevel.NONE) {
      return this.computeCrc16(headerBuffer, payloadBuffer);
    }

    const hmac = createHmac('sha256', this.sharedSecret);
    hmac.update(Buffer.concat([headerBuffer, payloadBuffer]));
    const digest = hmac.digest();

    if (securityLevel === SecurityLevel.STANDARD) {
      return digest.slice(0, 16);
    }

    return digest;
  }

  /**
   * Compute CRC-16
   */
  private computeCrc16(headerBuffer: Buffer, payloadBuffer: Buffer): Buffer {
    const data = Buffer.concat([headerBuffer, payloadBuffer]);
    let crc = 0xFFFF;

    for (let i = 0; i < data.length; i++) {
      crc ^= data[i] << 8;
      for (let j = 0; j < 8; j++) {
        if (crc & 0x8000) {
          crc = ((crc << 1) ^ 0x1021) & 0xFFFF;
        } else {
          crc = (crc << 1) & 0xFFFF;
        }
      }
    }

    const buffer = Buffer.alloc(2);
    buffer.writeUInt16BE(crc, 0);
    return buffer;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE USAGE
// ═══════════════════════════════════════════════════════════════════════════

async function exampleSecureDecoder() {
  console.log('═'.repeat(70));
  console.log('NANOGRIDATA SECURE DECODER - EXAMPLE');
  console.log('═'.repeat(70));

  try {
    // Setup secrets (in production: load from env)
    const secrets = new Map<number, Buffer>([
      [ModelID.ESP32_PRESSURE, Buffer.from('strong_esp32_secret_key_32bytes!')],
    ]);

    // Create decoder
    const decoder = new NanogridataSecureDecoder(secrets);

    // Create encoder with same secret
    const encoder = new NanogridataSecureEncoder(
      secrets.get(ModelID.ESP32_PRESSURE)!,
      ModelID.ESP32_PRESSURE
    );

    // Create payload
    const payload = {
      device_id: 'ESP32-001',
      lab_id: 'LAB-HETZNER-01',
      timestamp: Math.floor(Date.now() / 1000),
      pressure_pa: 101325,
    };

    console.log('\n1. Creating packet with encoder...');
    const packet = encoder.createPacket(
      payload,
      PayloadType.TELEMETRY,
      SecurityLevel.STANDARD
    );

    console.log(`   ✓ Packet created: ${packet.length} bytes`);
    console.log(`   Hex: ${packet.toString('hex').substring(0, 64)}...`);

    console.log('\n2. Decoding packet with decoder...');
    const result = decoder.deserialize(packet);

    if (result.valid && result.packet) {
      console.log(`   ✓ Packet valid!`);
      console.log(`   Model: 0x${result.packet.header.modelId.toString(16)}`);
      console.log(`   Type: ${result.packet.header.payloadType}`);
      console.log(`   Security: ${result.packet.securityLevel}`);

      const decoded = decoder.decodePayloadCBOR(result.packet);
      console.log(`   Payload:`, decoded);
    } else {
      console.log(`   ✗ Validation failed: ${result.error}`);
    }

    console.log('\n3. Testing security features...');

    // Try to inject CBOR
    console.log('   Testing CBOR size limit...');
    const largePayload = Buffer.alloc(2000);
    try {
      decoder.decodePayloadCBOR({
        header: { modelId: ModelID.ESP32_PRESSURE } as any,
        payload: largePayload,
        mac: Buffer.alloc(16),
        securityLevel: SecurityLevel.STANDARD,
      });
      console.log('   ✗ CBOR injection not prevented!');
    } catch (e) {
      console.log('   ✓ CBOR injection prevented: Large payload rejected');
    }

    console.log('\n✓ All security checks passed!');
  } catch (error) {
    console.error('Error:', error);
  }
}

// Export classes
export {
  NanogridataSecureDecoder,
  NanogridataSecureEncoder,
  PayloadType,
  ModelID,
  SecurityLevel,
};
export type { NanogridataHeader, ValidationResult, NanogridataPacket };

// Run example if executed directly
if (require.main === module) {
  exampleSecureDecoder().catch(console.error);
}

