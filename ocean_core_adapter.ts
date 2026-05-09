/**
 * OCEAN CORE ADAPTER - NANOGRIDATA INTEGRATION
 * 
 * Integration layer between Nanogridata protocol and Ocean Core 8030
 * - Packet processing pipeline
 * - Profile-based validation and decoding
 * - InfluxDB/TimescaleDB storage
 * - Error handling and audit logging
 */

import { EventEmitter } from 'events';

export interface OceanConfig {
  influxUrl: string;
  influxToken: string;
  influxOrg: string;
  influxBucket: string;
  databaseUrl: string;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

export interface SensorProfile {
  modelId: number;
  name: string;
  unit: string;
  minValue?: number;
  maxValue?: number;
  calibrationRequired?: boolean;
  decodeFunction: (data: any) => any;
  validateFunction: (data: any) => { valid: boolean; error?: string };
}

export interface ProcessedData {
  deviceId: string;
  labId: string;
  timestamp: Date;
  modelId: number;
  profileName: string;
  unit: string;
  measurements: Array<{
    name: string;
    value: number;
    unit?: string;
  }>;
  rawData: any;
  status: 'ok' | 'warning' | 'error';
  metadata?: Record<string, any>;
}

// ═══════════════════════════════════════════════════════════════════════════
// PROFILE REGISTRY
// ═══════════════════════════════════════════════════════════════════════════

class ProfileRegistry extends EventEmitter {
  private profiles: Map<number, SensorProfile>;

  constructor() {
    super();
    this.profiles = new Map();
    this.initializeDefaultProfiles();
  }

  private initializeDefaultProfiles(): void {
    // ESP32 Pressure Profile
    this.registerProfile({
      modelId: 0x10,
      name: 'NANO-ESP32-PRESSURE',
      unit: 'Pa',
      minValue: 0,
      maxValue: 200000,
      calibrationRequired: true,
      validateFunction: (data: any) => {
        if (
          !data.device_id ||
          !data.lab_id ||
          typeof data.pressure_pa !== 'number'
        ) {
          return {
            valid: false,
            error: 'Missing required fields: device_id, lab_id, pressure_pa',
          };
        }

        if (data.pressure_pa < 0 || data.pressure_pa > 200000) {
          return {
            valid: false,
            error: `Pressure out of range: ${data.pressure_pa}`,
          };
        }

        return { valid: true };
      },
      decodeFunction: (data: any) => {
        return {
          device_id: data.device_id,
          lab_id: data.lab_id,
          pressure_pa: data.pressure_pa,
          pressure_kpa: data.pressure_pa / 1000,
          pressure_atm: data.pressure_pa / 101325,
          timestamp: new Date(data.timestamp * 1000),
        };
      },
    });

    // STM32 Gas Profile
    this.registerProfile({
      modelId: 0x20,
      name: 'NANO-STM32-GAS',
      unit: 'ppm',
      minValue: 0,
      maxValue: 10000,
      validateFunction: (data: any) => {
        if (
          !data.device_id ||
          !data.gas_type ||
          typeof data.concentration_ppm !== 'number'
        ) {
          return {
            valid: false,
            error: 'Missing required fields',
          };
        }

        return { valid: true };
      },
      decodeFunction: (data: any) => {
        return {
          device_id: data.device_id,
          gas_type: data.gas_type,
          concentration_ppm: data.concentration_ppm,
          timestamp: new Date(data.timestamp * 1000),
        };
      },
    });

    // ASIC Multi-Sensor Profile
    this.registerProfile({
      modelId: 0x30,
      name: 'NANO-ASIC-MULTI',
      unit: 'mixed',
      decodeFunction: (data: any) => data,
      validateFunction: (data: any) => {
        if (!Array.isArray(data.sensors) || data.sensors.length === 0) {
          return {
            valid: false,
            error: 'No sensor data',
          };
        }

        return { valid: true };
      },
    });
  }

  registerProfile(profile: SensorProfile): void {
    this.profiles.set(profile.modelId, profile);
    this.emit('profileRegistered', {
      modelId: profile.modelId,
      name: profile.name,
    });
  }

  getProfile(modelId: number): SensorProfile | undefined {
    return this.profiles.get(modelId);
  }

  getAllProfiles(): SensorProfile[] {
    return Array.from(this.profiles.values());
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// DATA VALIDATOR
// ═══════════════════════════════════════════════════════════════════════════

class DataValidator {
  private registry: ProfileRegistry;

  constructor(registry: ProfileRegistry) {
    this.registry = registry;
  }

  async validate(
    modelId: number,
    data: any
  ): Promise<{ valid: boolean; error?: string }> {
    const profile = this.registry.getProfile(modelId);

    if (!profile) {
      return {
        valid: false,
        error: `No profile found for model 0x${modelId.toString(16)}`,
      };
    }

    try {
      return profile.validateFunction(data);
    } catch (error) {
      return {
        valid: false,
        error: `Validation error: ${error}`,
      };
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// TIMESERIES STORAGE
// ═══════════════════════════════════════════════════════════════════════════

class TimeseriesStore {
  private influxUrl: string;
  private token: string;
  private org: string;
  private bucket: string;

  constructor(config: {
    influxUrl: string;
    influxToken: string;
    influxOrg: string;
    influxBucket: string;
  }) {
    this.influxUrl = config.influxUrl;
    this.token = config.influxToken;
    this.org = config.influxOrg;
    this.bucket = config.influxBucket;
  }

  /**
   * Store measurement in InfluxDB 2.x
   */
  async storeInInflux(data: ProcessedData): Promise<boolean> {
    try {
      const lineProtocol = this.buildLineProtocol(data);

      const response = await fetch(`${this.influxUrl}/api/v2/write`, {
        method: 'POST',
        headers: {
          Authorization: `Token ${this.token}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `org=${this.org}&bucket=${this.bucket}\n${lineProtocol}`,
      });

      if (!response.ok) {
        throw new Error(`InfluxDB error: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error(`InfluxDB storage failed: ${error}`);
      return false;
    }
  }

  /**
   * Build InfluxDB line protocol format
   */
  private buildLineProtocol(data: ProcessedData): string {
    const tags = [
      `device_id=${this.escapeTag(data.deviceId)}`,
      `lab_id=${this.escapeTag(data.labId)}`,
      `model=0x${data.modelId.toString(16)}`,
      `profile=${this.escapeTag(data.profileName)}`,
      `status=${data.status}`,
    ].join(',');

    const fields = data.measurements
      .map((m) => `${this.escapeField(m.name)}=${m.value}`)
      .join(',');

    const timestamp = data.timestamp.getTime() * 1_000_000; // nanoseconds

    return `nanogridata,${tags} ${fields} ${timestamp}`;
  }

  private escapeTag(value: string): string {
    return value.replace(/[, =]/g, '\\$&');
  }

  private escapeField(value: string): string {
    return value.replace(/[ ,]/g, '\\ ');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// PROCESSING PIPELINE
// ═══════════════════════════════════════════════════════════════════════════

class ProcessingPipeline extends EventEmitter {
  private registry: ProfileRegistry;
  private validator: DataValidator;
  private store: TimeseriesStore;
  private errorLog: Array<{
    timestamp: Date;
    error: string;
    rawData: Buffer;
  }>;

  constructor(registry: ProfileRegistry, store: TimeseriesStore) {
    super();
    this.registry = registry;
    this.validator = new DataValidator(registry);
    this.store = store;
    this.errorLog = [];
  }

  /**
   * Process incoming packet through full pipeline
   */
  async processPacket(
    packet: any, // NanogridataPacket
    decodedData: any
  ): Promise<ProcessedData | null> {
    try {
      const modelId = packet.header.modelId;
      const profile = this.registry.getProfile(modelId);

      if (!profile) {
        throw new Error(`No profile for model 0x${modelId.toString(16)}`);
      }

      // 1. Validate
      const validation = await this.validator.validate(modelId, decodedData);
      if (!validation.valid) {
        throw new Error(`Validation failed: ${validation.error}`);
      }

      // 2. Decode with profile
      const decoded = profile.decodeFunction(decodedData);

      // 3. Build ProcessedData
      const processed: ProcessedData = {
        deviceId: decoded.device_id || 'unknown',
        labId: decoded.lab_id || 'unknown',
        timestamp: new Date(
          decoded.timestamp
            ? decoded.timestamp.getTime()
            : packet.header.timestamp * 1000
        ),
        modelId,
        profileName: profile.name,
        unit: profile.unit,
        measurements: this.extractMeasurements(decoded, profile),
        rawData: decoded,
        status: this.determineStatus(decoded, profile),
      };

      // 4. Store in timeseries DB
      await this.store.storeInInflux(processed);

      // 5. Emit event
      this.emit('packetProcessed', processed);

      console.log(`✓ Processed: ${processed.deviceId} → ${processed.profileName}`);
      return processed;
    } catch (error) {
      console.error(`✗ Processing failed: ${error}`);
      this.errorLog.push({
        timestamp: new Date(),
        error: String(error),
        rawData: packet,
      });

      this.emit('processingError', {
        error,
        packet,
      });

      return null;
    }
  }

  private extractMeasurements(
    data: any,
    profile: SensorProfile
  ): ProcessedData['measurements'] {
    const measurements: ProcessedData['measurements'] = [];

    if (profile.modelId === 0x10) {
      // Pressure
      measurements.push({
        name: 'pressure_pa',
        value: data.pressure_pa,
        unit: 'Pa',
      });
      measurements.push({
        name: 'pressure_kpa',
        value: data.pressure_kpa,
        unit: 'kPa',
      });
    } else if (profile.modelId === 0x20) {
      // Gas
      measurements.push({
        name: 'concentration',
        value: data.concentration_ppm,
        unit: 'ppm',
      });
    }

    return measurements;
  }

    private determineStatus(data: any, profile: SensorProfile): 'ok' | 'warning' | 'error' {
        if (profile.minValue === undefined || profile.maxValue === undefined) {
      return 'ok';
    }

    // Find numeric value
    const value =
        data.pressure_pa ??
        data.concentration_ppm ??
        data.value ??
      (data.measurements && data.measurements[0]?.value);

        if (typeof value !== 'number') {
            return 'error';
    }

    if (value < profile.minValue || value > profile.maxValue) {
      return 'warning';
    }

    return 'ok';
  }

  getErrorLog(): Array<{ timestamp: Date; error: string }> {
    return this.errorLog.map(({ timestamp, error }) => ({
      timestamp,
      error,
    }));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN OCEAN CORE ADAPTER
// ═══════════════════════════════════════════════════════════════════════════

class OceanCoreAdapter extends EventEmitter {
  private config: OceanConfig;
  private registry: ProfileRegistry;
  private store: TimeseriesStore;
  private pipeline: ProcessingPipeline;

  constructor(config: OceanConfig) {
    super();
    this.config = config;
    this.registry = new ProfileRegistry();
    this.store = new TimeseriesStore({
      influxUrl: config.influxUrl,
      influxToken: config.influxToken,
      influxOrg: config.influxOrg,
      influxBucket: config.influxBucket,
    });
    this.pipeline = new ProcessingPipeline(this.registry, this.store);

    // Forward pipeline events
    this.pipeline.on('packetProcessed', (data) =>
      this.emit('packetProcessed', data)
    );
    this.pipeline.on('processingError', (error) =>
      this.emit('processingError', error)
    );
  }

  /**
   * Process incoming Nanogridata packet
   */
  async processPacket(
    packet: any, // NanogridataPacket
    decodedData: any
  ): Promise<ProcessedData | null> {
    return this.pipeline.processPacket(packet, decodedData);
  }

  /**
   * Register custom profile
   */
  registerProfile(profile: SensorProfile): void {
    this.registry.registerProfile(profile);
  }

  /**
   * Get all registered profiles
   */
  getProfiles(): SensorProfile[] {
    return this.registry.getAllProfiles();
  }

  /**
   * Get processing error log
   */
  getErrorLog(): Array<{ timestamp: Date; error: string }> {
    return this.pipeline.getErrorLog();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE USAGE
// ═══════════════════════════════════════════════════════════════════════════

async function exampleOceanIntegration() {
  console.log('═'.repeat(70));
  console.log('OCEAN CORE NANOGRIDATA INTEGRATION - EXAMPLE');
  console.log('═'.repeat(70));

  const adapter = new OceanCoreAdapter({
    influxUrl: process.env.INFLUX_URL || 'http://localhost:8086',
    influxToken: process.env.INFLUX_TOKEN || 'demo-token',
    influxOrg: 'Kloud',
    influxBucket: 'nanogridata',
    databaseUrl: process.env.DATABASE_URL || 'postgresql://localhost/nanogridata',
    logLevel: 'info',
  });

  // Listen to events
  adapter.on('packetProcessed', (data) => {
    console.log(`\n✓ Packet processed: ${data.deviceId}`);
    console.log(`  Profile: ${data.profileName}`);
    console.log(`  Measurements: ${data.measurements.length}`);
      data.measurements.forEach((m: { name: string; value: number; unit?: string }) => {
      console.log(`    ${m.name}: ${m.value} ${m.unit}`);
    });
  });

  adapter.on('processingError', ({ error, packet }) => {
    console.log(`\n✗ Error: ${error}`);
  });

  // Example: Simulate processed packet
  const exampleData: ProcessedData = {
    deviceId: 'ESP32-001',
    labId: 'LAB-HETZNER-01',
    timestamp: new Date(),
    modelId: 0x10,
    profileName: 'NANO-ESP32-PRESSURE',
    unit: 'Pa',
    measurements: [
      { name: 'pressure_pa', value: 101325, unit: 'Pa' },
      { name: 'pressure_kpa', value: 101.325, unit: 'kPa' },
    ],
    rawData: { device_id: 'ESP32-001', lab_id: 'LAB-HETZNER-01' },
    status: 'ok',
  };

  console.log('\n1. Registered profiles:');
  adapter.getProfiles().forEach((p) => {
    console.log(`   - ${p.name} (model: 0x${p.modelId.toString(16)})`);
  });

  console.log('\n2. Processing example packet...');
  const result = await adapter.processPacket({}, exampleData.rawData);

  if (result) {
    console.log('\n✓ Integration test successful!');
  }
}

// Export classes
export {
  OceanCoreAdapter,
  ProfileRegistry,
  DataValidator,
  TimeseriesStore,
  ProcessingPipeline,
};

