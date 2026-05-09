/**
 * KLOUD NANOGRIDATA PROTOCOL v1.0
 * 
 * Unike + Hibride + Stabilne
 * 
 * Frame binar i përbashkët për të gjithë chip-at
 * Payload CBOR i fleksibël për çdo model
 * Profile-based dekodim në Ocean Core
 * 
 * DNA e përbashkët → Nanogridata Core Protocol
 * Fenotipe të ndryshme → Profile-a për çdo model chip-i / laborator
 */

import * as cbor from 'cbor';
import { createHmac, randomBytes } from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// 1️⃣  SHTRESA BAZË: Frame Binar i Përbashkët
// ═══════════════════════════════════════════════════════════════════════════

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
  NO_SECURITY = 0x00,      // CRC vetëm
  STANDARD = 0x01,         // HMAC-SHA256
  HIGH = 0x02,             // HMAC + AES-256-GCM
  MILITARY = 0x03,         // HMAC + AES-256-GCM + timestamp validation
}

/**
 * Nanogridata Frame Header (8-18 bytes)
 * 
 * Struktura:
 * - Magic (2 bytes): 0xC1 0x53 (Kloud Signature)
 * - Version (1 byte): 0x01
 * - Model ID (1 byte): Identifikon chip-in/laboratorin
 * - Payload Type (1 byte): Telemetry, Config, Event, etc.
 * - Flags (1 byte): Security level, compression, etc.
 * - Length (2 bytes): Payload length (big-endian)
 * - Timestamp (4 bytes): Unix timestamp
 * - Reserved (optional, 2 bytes): Future use
 */
interface NanogridataHeader {
  magic: Buffer;           // 0xC1 0x53
  version: number;         // 0x01
  modelId: ModelID;
  payloadType: PayloadType;
  flags: number;           // bit 0-1: security level, bit 2: compression
  length: number;          // payload length
  timestamp: number;       // Unix timestamp
  reserved?: number;       // Future use
}

/**
 * Nanogridata Packet (Complete)
 */
interface NanogridataPacket {
  header: NanogridataHeader;
  payload: Buffer | Record<string, any>; // Raw or CBOR
  mac?: Buffer;                           // 2-16 bytes (CRC/HMAC)
}

// ═══════════════════════════════════════════════════════════════════════════
// 2️⃣  ENCODER: Pack data në Nanogridata format
// ═══════════════════════════════════════════════════════════════════════════

class NanogridataEncoder {
  private sharedSecret: Buffer;

  constructor(sharedSecret?: Buffer) {
    this.sharedSecret = sharedSecret || Buffer.alloc(32, 0xAA);
  }

  /**
   * Enkodoni header-in në bytes
   */
  encodeHeader(header: NanogridataHeader): Buffer {
    const buffer = Buffer.alloc(14); // 2+1+1+1+1+2+4+2
    let offset = 0;

    // Magic (0xC1 0x53)
    buffer[offset++] = 0xC1;
    buffer[offset++] = 0x53;

    // Version
    buffer[offset++] = header.version;

    // Model ID
    buffer[offset++] = header.modelId;

    // Payload Type
    buffer[offset++] = header.payloadType;

    // Flags (security level + compression)
    buffer[offset++] = header.flags;

    // Length (big-endian, 2 bytes)
    buffer.writeUInt16BE(header.length, offset);
    offset += 2;

    // Timestamp (4 bytes, big-endian)
    buffer.writeUInt32BE(header.timestamp, offset);
    offset += 4;

    // Reserved
    buffer.writeUInt16BE(header.reserved || 0, offset);

    return buffer;
  }

  /**
   * Enkodoni payload-in në CBOR
   */
  encodePayload(data: Record<string, any>): Buffer {
    return Buffer.from(cbor.encode(data));
  }

  /**
   * Kalkuloni HMAC për packet-in
   */
  computeMAC(
    header: Buffer,
    payload: Buffer,
    securityLevel: SecurityLevel
  ): Buffer {
    if (securityLevel === SecurityLevel.NO_SECURITY) {
      // CRC-16
      return this.crc16(Buffer.concat([header, payload]));
    }

    if (
      securityLevel === SecurityLevel.STANDARD ||
      securityLevel === SecurityLevel.HIGH
    ) {
      // HMAC-SHA256, return first 16 bytes
      const hmac = createHmac('sha256', this.sharedSecret);
      hmac.update(Buffer.concat([header, payload]));
      return hmac.digest().slice(0, 16);
    }

    if (securityLevel === SecurityLevel.MILITARY) {
      // HMAC-SHA256 + timestamp validation in header
      const hmac = createHmac('sha256', this.sharedSecret);
      hmac.update(Buffer.concat([header, payload]));
      return hmac.digest(); // Full 32 bytes
    }

    return Buffer.alloc(2, 0);
  }

  /**
   * Krijoni një Nanogridata packet
   */
  createPacket(
    modelId: ModelID,
    payloadType: PayloadType,
    data: Record<string, any>,
    securityLevel: SecurityLevel = SecurityLevel.STANDARD
  ): NanogridataPacket {
    // Enkodoni payload
    const payloadBuffer = this.encodePayload(data);

    // Krijoni header
    const header: NanogridataHeader = {
      magic: Buffer.from([0xC1, 0x53]),
      version: 0x01,
      modelId,
      payloadType,
      flags: securityLevel & 0x0F,
      length: payloadBuffer.length,
      timestamp: Math.floor(Date.now() / 1000),
      reserved: 0,
    };

    // Enkodoni header
    const headerBuffer = this.encodeHeader(header);

    // Kalkuloni MAC
    const mac = this.computeMAC(headerBuffer, payloadBuffer, securityLevel);

    return {
      header,
      payload: payloadBuffer,
      mac,
    };
  }

  /**
   * Serializoni packet-in në bytes (për transmisim)
   */
  serialize(packet: NanogridataPacket): Buffer {
    const headerBuffer = this.encodeHeader(packet.header);
    const mac = packet.mac || Buffer.alloc(2, 0);

    return Buffer.concat([headerBuffer, packet.payload as Buffer, mac]);
  }

  private crc16(data: Buffer): Buffer {
    let crc = 0xFFFF;
    for (let i = 0; i < data.length; i++) {
      crc ^= data[i];
      for (let j = 0; j < 8; j++) {
        if (crc & 1) {
          crc = (crc >> 1) ^ 0xA001;
        } else {
          crc >>= 1;
        }
      }
    }
    const result = Buffer.alloc(2);
    result.writeUInt16LE(crc, 0);
    return result;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 3️⃣  DECODER: Shpakoni Nanogridata format
// ═══════════════════════════════════════════════════════════════════════════

interface PayloadProfile {
  modelId: ModelID;
  name: string;
  schema: Record<string, any>;
  handler: (payload: Record<string, any>) => any;
}

class NanogridataDecoder {
  private profiles: Map<ModelID, PayloadProfile>;
  private sharedSecret: Buffer;

  constructor(sharedSecret?: Buffer) {
    this.sharedSecret = sharedSecret || Buffer.alloc(32, 0xAA);
    this.profiles = new Map();
    this.registerDefaultProfiles();
  }

  /**
   * Regjistrojeni një profile për një model
   */
  registerProfile(profile: PayloadProfile): void {
    this.profiles.set(profile.modelId, profile);
  }

  /**
   * Dekodoni një Nanogridata packet
   */
  deserialize(buffer: Buffer): NanogridataPacket {
    if (buffer.length < 14) {
      throw new Error('Packet too short');
    }

    let offset = 0;

    // Lexoni magic
    const magic = buffer.slice(offset, (offset += 2));
    if (magic[0] !== 0xC1 || magic[1] !== 0x53) {
      throw new Error('Invalid magic bytes');
    }

    // Version
    const version = buffer[offset++];
    if (version !== 0x01) {
      throw new Error(`Unsupported version: ${version}`);
    }

    // Model ID
    const modelId = buffer[offset++];

    // Payload Type
    const payloadType = buffer[offset++];

    // Flags
    const flags = buffer[offset++];
    const securityLevel = flags & 0x0F;

    // Length
    const length = buffer.readUInt16BE(offset);
    offset += 2;

    // Timestamp
    const timestamp = buffer.readUInt32BE(offset);
    offset += 4;

    // Reserved
    const reserved = buffer.readUInt16BE(offset);
    offset += 2;

    // Payload
    const payloadBuffer = buffer.slice(offset, offset + length);
    offset += length;

    // MAC
    const macSize = this.getMACSize(securityLevel);
    const mac = buffer.slice(offset, offset + macSize);

    // Verify MAC
    const headerBuffer = buffer.slice(0, 14);
    const expectedMac = this.computeMAC(
      headerBuffer,
      payloadBuffer,
      securityLevel
    );
    if (!mac.equals(expectedMac)) {
      console.warn('⚠️  MAC verification failed');
    }

    // Dekodoni payload
    let decodedPayload: Record<string, any>;
    try {
      decodedPayload = cbor.decode(payloadBuffer);
    } catch (e) {
      decodedPayload = {};
    }

    return {
      header: {
        magic,
        version,
        modelId: modelId as ModelID,
        payloadType: payloadType as PayloadType,
        flags,
        length,
        timestamp,
        reserved,
      },
      payload: decodedPayload,
      mac,
    };
  }

  /**
   * Dekodoni payload sipas profile-it të modelit
   */
  decodeWithProfile(packet: NanogridataPacket): any {
    const profile = this.profiles.get(packet.header.modelId);
    if (!profile) {
      console.warn(
        `⚠️  No profile found for model ${packet.header.modelId}`
      );
      return packet.payload;
    }

    return profile.handler(packet.payload);
  }

  private computeMAC(
    header: Buffer,
    payload: Buffer,
    securityLevel: SecurityLevel
  ): Buffer {
    if (securityLevel === SecurityLevel.NO_SECURITY) {
      return this.crc16(Buffer.concat([header, payload]));
    }

    const hmac = createHmac('sha256', this.sharedSecret);
    hmac.update(Buffer.concat([header, payload]));

    const digest = hmac.digest();
    const macSize = this.getMACSize(securityLevel);
    return digest.slice(0, macSize);
  }

  private getMACSize(securityLevel: SecurityLevel): number {
    switch (securityLevel) {
      case SecurityLevel.NO_SECURITY:
        return 2;
      case SecurityLevel.STANDARD:
        return 16;
      case SecurityLevel.HIGH:
        return 16;
      case SecurityLevel.MILITARY:
        return 32;
      default:
        return 2;
    }
  }

  private crc16(data: Buffer): Buffer {
    let crc = 0xFFFF;
    for (let i = 0; i < data.length; i++) {
      crc ^= data[i];
      for (let j = 0; j < 8; j++) {
        if (crc & 1) {
          crc = (crc >> 1) ^ 0xA001;
        } else {
          crc >>= 1;
        }
      }
    }
    const result = Buffer.alloc(2);
    result.writeUInt16LE(crc, 0);
    return result;
  }

  /**
   * Regjistrojeni profile-a të paracaktuar
   */
  private registerDefaultProfiles(): void {
    // NANO-ESP32-PRESSURE
    this.registerProfile({
      modelId: ModelID.ESP32_PRESSURE,
      name: 'NANO-ESP32-PRESSURE',
      schema: {
        device_id: 'string',
        lab_id: 'string',
        sensor_type: 'pressure',
        entries: [{ ts: 'number', value: 'number' }],
      },
      handler: (payload) => ({
        type: 'PRESSURE',
        deviceId: payload.device_id,
        labId: payload.lab_id,
        measurements: payload.entries.map((e: any) => ({
          timestamp: new Date(e.ts * 1000),
          pressure: e.value,
          unit: 'Pa',
        })),
      }),
    });

    // NANO-STM32-GAS
    this.registerProfile({
      modelId: ModelID.STM32_GAS,
      name: 'NANO-STM32-GAS',
      schema: {
        device_id: 'string',
        lab_id: 'string',
        sensor_type: 'gas',
        gas_type: 'string',
        entries: [{ ts: 'number', ppm: 'number' }],
      },
      handler: (payload) => ({
        type: 'GAS',
        deviceId: payload.device_id,
        labId: payload.lab_id,
        gasType: payload.gas_type,
        measurements: payload.entries.map((e: any) => ({
          timestamp: new Date(e.ts * 1000),
          concentration: e.ppm,
          unit: 'ppm',
        })),
      }),
    });

    // NANO-ASIC-MULTI
    this.registerProfile({
      modelId: ModelID.ASIC_MULTI,
      name: 'NANO-ASIC-MULTI',
      schema: {
        device_id: 'string',
        lab_id: 'string',
        sensors: [{ type: 'string', unit: 'string', entries: [] }],
      },
      handler: (payload) => ({
        type: 'MULTI_SENSOR',
        deviceId: payload.device_id,
        labId: payload.lab_id,
        sensors: payload.sensors.map((s: any) => ({
          sensorType: s.type,
          unit: s.unit,
          measurements: s.entries.map((e: any) => ({
            timestamp: new Date(e.ts * 1000),
            value: e.value,
          })),
        })),
      }),
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 4️⃣  PROFILE MANAGEMENT: Tabela për modele
// ═══════════════════════════════════════════════════════════════════════════

interface ModelProfile {
  model_id: number;
  name: string;
  payload_profile: string;
  decode_handler: string;
  security_level: SecurityLevel;
  created_at: Date;
  updated_at: Date;
}

class ProfileRegistry {
  /**
   * Shembull i tabelës në PostgreSQL:
   * 
   * CREATE TABLE nanogridata_models (
   *   id SERIAL PRIMARY KEY,
   *   model_id INT UNIQUE NOT NULL,
   *   name VARCHAR(255) NOT NULL,
   *   payload_profile VARCHAR(255),
   *   decode_handler VARCHAR(255),
   *   security_level INT DEFAULT 1,
   *   created_at TIMESTAMP DEFAULT NOW(),
   *   updated_at TIMESTAMP DEFAULT NOW()
   * );
   * 
   * INSERT INTO nanogridata_models VALUES
   *   (NULL, 0x10, 'NANO-ESP32-PRESSURE', 'pressure_v1', 'decode_pressure_v1', 1, NOW(), NOW()),
   *   (NULL, 0x20, 'NANO-STM32-GAS', 'gas_v1', 'decode_gas_v1', 1, NOW(), NOW()),
   *   (NULL, 0x30, 'NANO-ASIC-MULTI', 'multi_sensor_v1', 'decode_multi_v1', 2, NOW(), NOW());
   */

  static readonly REGISTRY: ModelProfile[] = [
    {
      model_id: ModelID.ESP32_PRESSURE,
      name: 'NANO-ESP32-PRESSURE',
      payload_profile: 'pressure_v1',
      decode_handler: 'decode_pressure_v1',
      security_level: SecurityLevel.STANDARD,
      created_at: new Date('2026-01-17'),
      updated_at: new Date('2026-01-17'),
    },
    {
      model_id: ModelID.STM32_GAS,
      name: 'NANO-STM32-GAS',
      payload_profile: 'gas_v1',
      decode_handler: 'decode_gas_v1',
      security_level: SecurityLevel.STANDARD,
      created_at: new Date('2026-01-17'),
      updated_at: new Date('2026-01-17'),
    },
    {
      model_id: ModelID.ASIC_MULTI,
      name: 'NANO-ASIC-MULTI',
      payload_profile: 'multi_sensor_v1',
      decode_handler: 'decode_multi_v1',
      security_level: SecurityLevel.HIGH,
      created_at: new Date('2026-01-17'),
      updated_at: new Date('2026-01-17'),
    },
  ];

  static getProfile(modelId: ModelID): ModelProfile | undefined {
    return this.REGISTRY.find((p) => p.model_id === modelId);
  }

  static getAllProfiles(): ModelProfile[] {
    return this.REGISTRY;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 5️⃣  USAGE EXAMPLES
// ═══════════════════════════════════════════════════════════════════════════

function demonstrateNanogridata(): void {
  console.log('\n🧬 KLOUD NANOGRIDATA PROTOCOL v1.0 - DEMONSTRATION\n');

  const sharedSecret = randomBytes(32);
  const encoder = new NanogridataEncoder(sharedSecret);
  const decoder = new NanogridataDecoder(sharedSecret);

  // ─────────────────────────────────────────────────────────────────────────
  // Example 1: Pressure Sensor (ESP32)
  // ─────────────────────────────────────────────────────────────────────────
  console.log('📊 Example 1: ESP32 Pressure Sensor\n');

  const pressurePacket = encoder.createPacket(
    ModelID.ESP32_PRESSURE,
    PayloadType.TELEMETRY,
    {
      device_id: 'ESP32-001',
      lab_id: 'LAB-HETZNER-01',
      sensor_type: 'pressure',
      entries: [
        { ts: Math.floor(Date.now() / 1000) - 10, value: 101325 },
        { ts: Math.floor(Date.now() / 1000) - 5, value: 101326 },
        { ts: Math.floor(Date.now() / 1000), value: 101327 },
      ],
    },
    SecurityLevel.STANDARD
  );

  const pressureBuffer = encoder.serialize(pressurePacket);
  console.log(`✅ Pressure packet serialized (${pressureBuffer.length} bytes)`);
  console.log(`   Hex: ${pressureBuffer.toString('hex').substring(0, 64)}...\n`);

  // Deserialize
  const decodedPressure = decoder.deserialize(pressureBuffer);
  const decodedPressureData = decoder.decodeWithProfile(decodedPressure);
  console.log(`✅ Pressure packet deserialized:`);
  console.log(`   Type: ${decodedPressureData.type}`);
  console.log(`   Device: ${decodedPressureData.deviceId}`);
  console.log(`   Lab: ${decodedPressureData.labId}`);
  console.log(`   Measurements: ${decodedPressureData.measurements.length}\n`);

  // ─────────────────────────────────────────────────────────────────────────
  // Example 2: Gas Sensor (STM32)
  // ─────────────────────────────────────────────────────────────────────────
  console.log('💨 Example 2: STM32 Gas Sensor\n');

  const gasPacket = encoder.createPacket(
    ModelID.STM32_GAS,
    PayloadType.TELEMETRY,
    {
      device_id: 'STM32-002',
      lab_id: 'LAB-HETZNER-01',
      sensor_type: 'gas',
      gas_type: 'CO2',
      entries: [
        { ts: Math.floor(Date.now() / 1000) - 10, ppm: 412 },
        { ts: Math.floor(Date.now() / 1000) - 5, ppm: 413 },
        { ts: Math.floor(Date.now() / 1000), ppm: 414 },
      ],
    },
    SecurityLevel.STANDARD
  );

  const gasBuffer = encoder.serialize(gasPacket);
  console.log(`✅ Gas packet serialized (${gasBuffer.length} bytes)`);
  console.log(`   Hex: ${gasBuffer.toString('hex').substring(0, 64)}...\n`);

  const decodedGas = decoder.deserialize(gasBuffer);
  const decodedGasData = decoder.decodeWithProfile(decodedGas);
  console.log(`✅ Gas packet deserialized:`);
  console.log(`   Type: ${decodedGasData.type}`);
  console.log(`   Gas Type: ${decodedGasData.gasType}`);
  console.log(`   Device: ${decodedGasData.deviceId}`);
  console.log(`   Measurements: ${decodedGasData.measurements.length}\n`);

  // ─────────────────────────────────────────────────────────────────────────
  // Example 3: Multi-Sensor (ASIC)
  // ─────────────────────────────────────────────────────────────────────────
  console.log('🔧 Example 3: ASIC Multi-Sensor\n');

  const multiPacket = encoder.createPacket(
    ModelID.ASIC_MULTI,
    PayloadType.TELEMETRY,
    {
      device_id: 'ASIC-003',
      lab_id: 'LAB-HETZNER-01',
      sensors: [
        {
          type: 'temperature',
          unit: 'C',
          entries: [
            { ts: Math.floor(Date.now() / 1000), value: 23.5 },
          ],
        },
        {
          type: 'humidity',
          unit: '%',
          entries: [
            { ts: Math.floor(Date.now() / 1000), value: 45 },
          ],
        },
      ],
    },
    SecurityLevel.HIGH
  );

  const multiBuffer = encoder.serialize(multiPacket);
  console.log(`✅ Multi-sensor packet serialized (${multiBuffer.length} bytes)`);
  console.log(`   Hex: ${multiBuffer.toString('hex').substring(0, 64)}...\n`);

  const decodedMulti = decoder.deserialize(multiBuffer);
  const decodedMultiData = decoder.decodeWithProfile(decodedMulti);
  console.log(`✅ Multi-sensor packet deserialized:`);
  console.log(`   Type: ${decodedMultiData.type}`);
  console.log(`   Device: ${decodedMultiData.deviceId}`);
  console.log(`   Sensors: ${decodedMultiData.sensors.length}\n`);

  // ─────────────────────────────────────────────────────────────────────────
  // Profile Registry
  // ─────────────────────────────────────────────────────────────────────────
  console.log('📋 Profile Registry:\n');
  ProfileRegistry.getAllProfiles().forEach((profile) => {
    console.log(`   Model: 0x${profile.model_id.toString(16).padStart(2, '0').toUpperCase()}`);
    console.log(`   Name: ${profile.name}`);
    console.log(`   Profile: ${profile.payload_profile}`);
    console.log(`   Handler: ${profile.decode_handler}`);
    console.log(`   Security: ${SecurityLevel[profile.security_level]}\n`);
  });
}

// Export
export {
  NanogridataEncoder,
  NanogridataDecoder,
  ProfileRegistry,
  PayloadType,
  ModelID,
  SecurityLevel,
  demonstrateNanogridata,
};

export type {
  NanogridataHeader,
  NanogridataPacket,
  ModelProfile,
};

// Run demonstration
if (require.main === module) {
  demonstrateNanogridata();
}

