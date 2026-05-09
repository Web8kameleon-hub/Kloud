/**
 * KLOUD NANOGRIDATA PROTOCOL v1.0 - CHIP FIRMWARE
 * 
 * C Implementation për ESP32, STM32, etj.
 * 
 * Lightweight, optimized për embedded systems
 * Frame binar i përbashkët, payload CBOR
 */

#include <stdint.h>
#include <string.h>
#include <time.h>

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════

#define NANOGRIDATA_MAGIC_0 0xC1
#define NANOGRIDATA_MAGIC_1 0x53
#define NANOGRIDATA_VERSION 0x01

// Payload Types
#define PAYLOAD_TYPE_TELEMETRY 0x01
#define PAYLOAD_TYPE_CONFIG    0x02
#define PAYLOAD_TYPE_EVENT     0x03
#define PAYLOAD_TYPE_COMMAND   0x04
#define PAYLOAD_TYPE_CALIBRATION 0x05

// Model IDs
#define MODEL_ESP32_PRESSURE   0x10
#define MODEL_STM32_GAS        0x20
#define MODEL_ASIC_MULTI       0x30

// Security Levels
#define SECURITY_NONE          0x00
#define SECURITY_STANDARD      0x01  // HMAC-SHA256
#define SECURITY_HIGH          0x02  // HMAC + AES-256
#define SECURITY_MILITARY      0x03

#define NANOGRIDATA_HEADER_SIZE 14
#define NANOGRIDATA_MAX_PAYLOAD 512
#define NANOGRIDATA_CRC16_SIZE  2
#define NANOGRIDATA_MAC_SIZE    16

// ═══════════════════════════════════════════════════════════════════════════
// STRUCTURES
// ═══════════════════════════════════════════════════════════════════════════

typedef struct {
  uint8_t magic[2];        // 0xC1 0x53
  uint8_t version;         // 0x01
  uint8_t model_id;        // Chip ID
  uint8_t payload_type;    // Telemetry, Config, etc.
  uint8_t flags;           // Security level, compression
  uint16_t length;         // Payload length (big-endian)
  uint32_t timestamp;      // Unix timestamp (big-endian)
  uint16_t reserved;       // Future use (big-endian)
} nanogridata_header_t;

typedef struct {
  nanogridata_header_t header;
  uint8_t payload[NANOGRIDATA_MAX_PAYLOAD];
  uint8_t mac[NANOGRIDATA_MAC_SIZE];
  uint16_t payload_size;
  uint16_t mac_size;
} nanogridata_packet_t;

// ═══════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * CRC-16 CCITT calculation
 */
uint16_t crc16_ccitt(const uint8_t *data, uint16_t length) {
  uint16_t crc = 0xFFFF;
  for (uint16_t i = 0; i < length; i++) {
    crc ^= data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x8000) {
        crc = (crc << 1) ^ 0x1021;
      } else {
        crc = crc << 1;
      }
      crc &= 0xFFFF;
    }
  }
  return crc;
}

/**
 * Big-endian write utilities
 */
void write_be16(uint8_t *buffer, uint16_t value) {
  buffer[0] = (value >> 8) & 0xFF;
  buffer[1] = value & 0xFF;
}

void write_be32(uint8_t *buffer, uint32_t value) {
  buffer[0] = (value >> 24) & 0xFF;
  buffer[1] = (value >> 16) & 0xFF;
  buffer[2] = (value >> 8) & 0xFF;
  buffer[3] = value & 0xFF;
}

uint16_t read_be16(const uint8_t *buffer) {
  return ((uint16_t)buffer[0] << 8) | buffer[1];
}

uint32_t read_be32(const uint8_t *buffer) {
  return ((uint32_t)buffer[0] << 24) | ((uint32_t)buffer[1] << 16) |
         ((uint32_t)buffer[2] << 8) | buffer[3];
}

// ═══════════════════════════════════════════════════════════════════════════
// ENCODER
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Inicializoni header-in
 */
void nanogridata_init_header(nanogridata_header_t *header, uint8_t model_id,
                              uint8_t payload_type, uint16_t payload_size,
                              uint8_t security_level) {
  header->magic[0] = NANOGRIDATA_MAGIC_0;
  header->magic[1] = NANOGRIDATA_MAGIC_1;
  header->version = NANOGRIDATA_VERSION;
  header->model_id = model_id;
  header->payload_type = payload_type;
  header->flags = security_level & 0x0F;
  header->length = payload_size;
  header->timestamp = (uint32_t)time(NULL);
  header->reserved = 0;
}

/**
 * Enkodoni header-in në bytes
 */
void nanogridata_encode_header(const nanogridata_header_t *header,
                                uint8_t *buffer) {
  int offset = 0;

  buffer[offset++] = header->magic[0];
  buffer[offset++] = header->magic[1];
  buffer[offset++] = header->version;
  buffer[offset++] = header->model_id;
  buffer[offset++] = header->payload_type;
  buffer[offset++] = header->flags;

  write_be16(&buffer[offset], header->length);
  offset += 2;

  write_be32(&buffer[offset], header->timestamp);
  offset += 4;

  write_be16(&buffer[offset], header->reserved);
}

/**
 * Krijoni packet-in me payload
 */
void nanogridata_create_packet(nanogridata_packet_t *packet, uint8_t model_id,
                                uint8_t payload_type, const uint8_t *payload,
                                uint16_t payload_size, uint8_t security_level,
                                const uint8_t *shared_secret,
                                uint16_t secret_size) {
  // Initialize header
  nanogridata_init_header(&packet->header, model_id, payload_type, payload_size,
                          security_level);

  // Copy payload
  memcpy(packet->payload, payload, payload_size);
  packet->payload_size = payload_size;

  // Encode header
  uint8_t header_buffer[NANOGRIDATA_HEADER_SIZE];
  nanogridata_encode_header(&packet->header, header_buffer);

  // Calculate CRC/MAC based on security level
  if (security_level == SECURITY_NONE) {
    // CRC-16
    uint16_t crc = crc16_ccitt(header_buffer, NANOGRIDATA_HEADER_SIZE);
    crc ^= crc16_ccitt(payload, payload_size);

    write_be16(packet->mac, crc);
    packet->mac_size = 2;
  } else {
    // HMAC-SHA256 (placeholder, requires crypto library)
    // For now, use CRC-16 extended
    uint16_t crc = crc16_ccitt(header_buffer, NANOGRIDATA_HEADER_SIZE);
    crc ^= crc16_ccitt(payload, payload_size);
    if (shared_secret) {
      crc ^= crc16_ccitt(shared_secret, secret_size);
    }

    write_be16(packet->mac, crc);
    packet->mac_size = (security_level == SECURITY_STANDARD) ? 16 : 32;
  }
}

/**
 * Serializoni packet-in në bytes (për transmisim)
 */
uint16_t nanogridata_serialize(const nanogridata_packet_t *packet,
                                uint8_t *buffer, uint16_t buffer_size) {
  uint16_t required_size =
      NANOGRIDATA_HEADER_SIZE + packet->payload_size + packet->mac_size;

  if (buffer_size < required_size) {
    return 0; // Buffer too small
  }

  int offset = 0;

  // Encode header
  nanogridata_encode_header(&packet->header, &buffer[offset]);
  offset += NANOGRIDATA_HEADER_SIZE;

  // Copy payload
  memcpy(&buffer[offset], packet->payload, packet->payload_size);
  offset += packet->payload_size;

  // Copy MAC
  memcpy(&buffer[offset], packet->mac, packet->mac_size);
  offset += packet->mac_size;

  return offset;
}

// ═══════════════════════════════════════════════════════════════════════════
// DECODER
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Dekodoni header-in mula sa bytes
 */
int nanogridata_decode_header(const uint8_t *buffer, uint16_t buffer_size,
                               nanogridata_header_t *header) {
  if (buffer_size < NANOGRIDATA_HEADER_SIZE) {
    return -1; // Buffer too small
  }

  int offset = 0;

  header->magic[0] = buffer[offset++];
  header->magic[1] = buffer[offset++];

  if (header->magic[0] != NANOGRIDATA_MAGIC_0 ||
      header->magic[1] != NANOGRIDATA_MAGIC_1) {
    return -2; // Invalid magic
  }

  header->version = buffer[offset++];
  if (header->version != NANOGRIDATA_VERSION) {
    return -3; // Unsupported version
  }

  header->model_id = buffer[offset++];
  header->payload_type = buffer[offset++];
  header->flags = buffer[offset++];

  header->length = read_be16(&buffer[offset]);
  offset += 2;

  header->timestamp = read_be32(&buffer[offset]);
  offset += 4;

  header->reserved = read_be16(&buffer[offset]);

  return 0; // Success
}

/**
 * Dekodoni packet-in mula sa bytes
 */
int nanogridata_deserialize(const uint8_t *buffer, uint16_t buffer_size,
                             nanogridata_packet_t *packet) {
  // Decode header
  int ret = nanogridata_decode_header(buffer, buffer_size, &packet->header);
  if (ret != 0) {
    return ret;
  }

  uint16_t payload_size = packet->header.length;
  if (NANOGRIDATA_HEADER_SIZE + payload_size > buffer_size) {
    return -4; // Buffer too small for payload
  }

  // Copy payload
  memcpy(packet->payload, &buffer[NANOGRIDATA_HEADER_SIZE], payload_size);
  packet->payload_size = payload_size;

  // Extract MAC
  uint8_t security_level = packet->header.flags & 0x0F;
  uint16_t mac_size = 2;
  if (security_level == SECURITY_STANDARD) {
    mac_size = 16;
  } else if (security_level == SECURITY_HIGH ||
             security_level == SECURITY_MILITARY) {
    mac_size = 32;
  }

  uint16_t mac_offset = NANOGRIDATA_HEADER_SIZE + payload_size;
  if (mac_offset + mac_size > buffer_size) {
    return -5; // MAC overflow
  }

  memcpy(packet->mac, &buffer[mac_offset], mac_size);
  packet->mac_size = mac_size;

  return 0; // Success
}

// ═══════════════════════════════════════════════════════════════════════════
// PAYLOAD HELPERS (CBOR-like simple format)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Simple telemetry payload builder (not full CBOR, but compact)
 * Format: device_id (string) | lab_id (string) | timestamp | value
 */
uint16_t build_pressure_telemetry(uint8_t *payload, const char *device_id,
                                   const char *lab_id, uint32_t timestamp,
                                   uint32_t pressure_pa) {
  int offset = 0;

  // Device ID (length + string)
  uint8_t device_id_len = strlen(device_id);
  payload[offset++] = device_id_len;
  memcpy(&payload[offset], device_id, device_id_len);
  offset += device_id_len;

  // Lab ID (length + string)
  uint8_t lab_id_len = strlen(lab_id);
  payload[offset++] = lab_id_len;
  memcpy(&payload[offset], lab_id, lab_id_len);
  offset += lab_id_len;

  // Timestamp
  write_be32(&payload[offset], timestamp);
  offset += 4;

  // Pressure value
  write_be32(&payload[offset], pressure_pa);
  offset += 4;

  return offset;
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE: ESP32 PRESSURE SENSOR
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Simulasyon ng ESP32 pressure sensor packet creation
 */
void example_esp32_pressure(void) {
  // Create packet
  nanogridata_packet_t packet;
  uint8_t payload[NANOGRIDATA_MAX_PAYLOAD];

  // Build telemetry payload
  uint16_t payload_size = build_pressure_telemetry(
      payload, "ESP32-001", "LAB-HETZNER-01", time(NULL), 101325);

  // Create packet with standard security
  uint8_t shared_secret[] = {0xAA, 0xBB, 0xCC, 0xDD}; // Example secret
  nanogridata_create_packet(&packet, MODEL_ESP32_PRESSURE,
                             PAYLOAD_TYPE_TELEMETRY, payload, payload_size,
                             SECURITY_STANDARD, shared_secret, 4);

  // Serialize for transmission
  uint8_t tx_buffer[NANOGRIDATA_MAX_PAYLOAD + NANOGRIDATA_HEADER_SIZE +
                    NANOGRIDATA_MAC_SIZE];
  uint16_t tx_size =
      nanogridata_serialize(&packet, tx_buffer, sizeof(tx_buffer));

  // Print hex
  printf("ESP32 Pressure Packet (%d bytes):\n", tx_size);
  printf("Header: ");
  for (int i = 0; i < NANOGRIDATA_HEADER_SIZE; i++) {
    printf("%02X ", tx_buffer[i]);
  }
  printf("\nPayload: ");
  for (int i = 0; i < payload_size; i++) {
    printf("%02X ", tx_buffer[NANOGRIDATA_HEADER_SIZE + i]);
  }
  printf("\nMAC: ");
  for (int i = 0; i < packet.mac_size; i++) {
    printf("%02X ", packet.mac[i]);
  }
  printf("\n\n");
}

// ═══════════════════════════════════════════════════════════════════════════
// INITIALIZATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Inicializoni Nanogridata protokolin për chip-in
 */
void nanogridata_init(void) {
  // Setup interrupt, timers, sensors, etc.
  // Configure transmission parameters
  // Register callbacks for incoming packets
}

/**
 * Main loop example
 */
void nanogridata_main_loop(void) {
  // while (1) {
  //   // Read sensor
  //   uint32_t pressure = read_pressure_sensor();
  //
  //   // Create packet
  //   nanogridata_packet_t packet;
  //   uint8_t payload[NANOGRIDATA_MAX_PAYLOAD];
  //   uint16_t payload_size = build_pressure_telemetry(
  //       payload, "ESP32-001", "LAB-HETZNER-01", time(NULL), pressure);
  //
  //   // Create packet
  //   nanogridata_create_packet(&packet, MODEL_ESP32_PRESSURE,
  //                              PAYLOAD_TYPE_TELEMETRY, payload,
  //                              payload_size, SECURITY_STANDARD, NULL, 0);
  //
  //   // Serialize and transmit
  //   uint8_t tx_buffer[NANOGRIDATA_MAX_PAYLOAD + 50];
  //   uint16_t tx_size =
  //       nanogridata_serialize(&packet, tx_buffer, sizeof(tx_buffer));
  //
  //   // Send via UART/LoRa/WiFi
  //   uart_write(tx_buffer, tx_size);
  //
  //   // Sleep
  //   delay(5000); // 5 seconds
  // }
}

