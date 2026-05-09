/**
 * KLOUD NANOGRIDATA PROTOCOL v1.0 - EMBEDDED CONFIGURATION
 * 
 * Compile-time configuration për ESP32, STM32, ASIC
 * 
 * Usage:
 *   - Define PLATFORM_ESP32 or PLATFORM_STM32 para sa target
 *   - #include "nanogridata_config.h"
 *   - #include "nanogridata_protocol_v1.c"
 */

#ifndef NANOGRIDATA_CONFIG_H
#define NANOGRIDATA_CONFIG_H

#include <stdint.h>

// ═══════════════════════════════════════════════════════════════════════════
// PLATFORM DETECTION
// ═══════════════════════════════════════════════════════════════════════════

#if defined(ESP32)
  #define PLATFORM_ESP32 1
#elif defined(STM32F4xx) || defined(STM32F7xx) || defined(STM32H7xx)
  #define PLATFORM_STM32 1
#elif defined(ASIC_CUSTOM)
  #define PLATFORM_ASIC 1
#else
  #define PLATFORM_GENERIC 1
#endif

// ═══════════════════════════════════════════════════════════════════════════
// MEMORY CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

#ifdef PLATFORM_ESP32
  // ESP32: 520 KB SRAM, generous memory
  #define NANOGRIDATA_MAX_PAYLOAD 512
  #define NANOGRIDATA_MAX_PACKETS 10
  #define NANOGRIDATA_RX_BUFFER_SIZE 1024
  #define NANOGRIDATA_TX_BUFFER_SIZE 1024
  #define NANOGRIDATA_USE_MALLOC 1

#elif defined(PLATFORM_STM32)
  // STM32: Limited SRAM, constrained
  #define NANOGRIDATA_MAX_PAYLOAD 256
  #define NANOGRIDATA_MAX_PACKETS 5
  #define NANOGRIDATA_RX_BUFFER_SIZE 512
  #define NANOGRIDATA_TX_BUFFER_SIZE 512
  #define NANOGRIDATA_USE_MALLOC 0  // Use static allocation

#elif defined(PLATFORM_ASIC)
  // Custom ASIC: Optimized for specific use case
  #define NANOGRIDATA_MAX_PAYLOAD 384
  #define NANOGRIDATA_MAX_PACKETS 8
  #define NANOGRIDATA_RX_BUFFER_SIZE 768
  #define NANOGRIDATA_TX_BUFFER_SIZE 768
  #define NANOGRIDATA_USE_MALLOC 1

#else
  // Generic fallback
  #define NANOGRIDATA_MAX_PAYLOAD 256
  #define NANOGRIDATA_MAX_PACKETS 5
  #define NANOGRIDATA_RX_BUFFER_SIZE 512
  #define NANOGRIDATA_TX_BUFFER_SIZE 512
  #define NANOGRIDATA_USE_MALLOC 1
#endif

// ═══════════════════════════════════════════════════════════════════════════
// COMMUNICATION INTERFACE
// ═══════════════════════════════════════════════════════════════════════════

#ifdef PLATFORM_ESP32
  #define NANOGRIDATA_USE_UART 1
  #define NANOGRIDATA_USE_WIFI 1
  #define NANOGRIDATA_USE_BLE 1
  #define NANOGRIDATA_USE_LORA 0
  #define NANOGRIDATA_UART_BAUD 115200

#elif defined(PLATFORM_STM32)
  #define NANOGRIDATA_USE_UART 1
  #define NANOGRIDATA_USE_WIFI 0
  #define NANOGRIDATA_USE_BLE 0
  #define NANOGRIDATA_USE_LORA 1
  #define NANOGRIDATA_USE_DMA 1
  #define NANOGRIDATA_UART_BAUD 9600

#elif defined(PLATFORM_ASIC)
  #define NANOGRIDATA_USE_UART 1
  #define NANOGRIDATA_USE_WIFI 0
  #define NANOGRIDATA_USE_BLE 0
  #define NANOGRIDATA_USE_LORA 1
  #define NANOGRIDATA_USE_DMA 1
  #define NANOGRIDATA_UART_BAUD 19200
#endif

// ═══════════════════════════════════════════════════════════════════════════
// SECURITY CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

// Default security level (can be overridden per-packet)
#define NANOGRIDATA_SECURITY_LEVEL_DEFAULT 0x01  // STANDARD (HMAC-SHA256)

// Security features
#define NANOGRIDATA_ENABLE_CRC 1
#define NANOGRIDATA_ENABLE_HMAC 1
#define NANOGRIDATA_ENABLE_TIMESTAMP_VALIDATION 1

// Timestamp drift tolerance (seconds)
#define NANOGRIDATA_TIMESTAMP_MAX_DRIFT 3600

// Replay attack protection (0 = disabled, 1 = enabled)
#define NANOGRIDATA_ENABLE_REPLAY_PROTECTION 1
#define NANOGRIDATA_REPLAY_CACHE_SIZE 10

// ═══════════════════════════════════════════════════════════════════════════
// DEBUGGING & LOGGING
// ═══════════════════════════════════════════════════════════════════════════

// Logging level: 0=none, 1=error, 2=warn, 3=info, 4=debug
#define NANOGRIDATA_LOG_LEVEL 3

#if NANOGRIDATA_LOG_LEVEL > 0
  #include <stdio.h>
  #define NANO_LOG_ERROR(fmt, ...) printf("[NANO ERROR] " fmt "\n", ##__VA_ARGS__)
#else
  #define NANO_LOG_ERROR(fmt, ...)
#endif

#if NANOGRIDATA_LOG_LEVEL > 2
  #define NANO_LOG_INFO(fmt, ...) printf("[NANO INFO] " fmt "\n", ##__VA_ARGS__)
#else
  #define NANO_LOG_INFO(fmt, ...)
#endif

#if NANOGRIDATA_LOG_LEVEL > 3
  #define NANO_LOG_DEBUG(fmt, ...) printf("[NANO DEBUG] " fmt "\n", ##__VA_ARGS__)
#else
  #define NANO_LOG_DEBUG(fmt, ...)
#endif

// ═══════════════════════════════════════════════════════════════════════════
// PERFORMANCE OPTIMIZATION
// ═══════════════════════════════════════════════════════════════════════════

#ifdef PLATFORM_STM32
  // Use DMA for faster transfers
  #define NANOGRIDATA_USE_DMA 1
  #define NANOGRIDATA_DMA_CHANNEL 7
#endif

// Inline CRC calculation for performance
#define NANOGRIDATA_INLINE_CRC 1

// Cache last received model_id for faster profile lookup
#define NANOGRIDATA_CACHE_MODEL_ID 1

// ═══════════════════════════════════════════════════════════════════════════
// FEATURE FLAGS
// ═══════════════════════════════════════════════════════════════════════════

// Enable packet compression (gzip-like)
#define NANOGRIDATA_ENABLE_COMPRESSION 0

// Enable encryption support (AES-256-GCM)
#define NANOGRIDATA_ENABLE_ENCRYPTION 0

// Enable sensor calibration mode
#define NANOGRIDATA_ENABLE_CALIBRATION 1

// Maximum supported model IDs
#define NANOGRIDATA_MAX_MODEL_IDS 5

// ═══════════════════════════════════════════════════════════════════════════
// PLATFORM-SPECIFIC HARDWARE DRIVERS
// ═══════════════════════════════════════════════════════════════════════════

#ifdef PLATFORM_ESP32
  // ESP32 UART configuration
  #include "driver/uart.h"
  #define NANOGRIDATA_UART_NUM UART_NUM_0
  #define NANOGRIDATA_UART_TX_PIN 1
  #define NANOGRIDATA_UART_RX_PIN 3

  // ESP32 has WiFi, so add NTP support
  #define NANOGRIDATA_ENABLE_NTP 1

#elif defined(PLATFORM_STM32)
  // STM32 UART HAL
  extern UART_HandleTypeDef huart1;
  #define NANOGRIDATA_UART_HANDLE (&huart1)

  // STM32 has RTC
  #define NANOGRIDATA_ENABLE_RTC 1

#endif

// ═══════════════════════════════════════════════════════════════════════════
// TIMING & WATCHDOG
// ═══════════════════════════════════════════════════════════════════════════

// Packet RX timeout (milliseconds)
#define NANOGRIDATA_RX_TIMEOUT_MS 1000

// Packet TX timeout
#define NANOGRIDATA_TX_TIMEOUT_MS 500

// Watchdog enabled
#define NANOGRIDATA_ENABLE_WATCHDOG 1
#define NANOGRIDATA_WATCHDOG_TIMEOUT_MS 30000

// ═══════════════════════════════════════════════════════════════════════════
// VALIDATION
// ═══════════════════════════════════════════════════════════════════════════

#if !defined(NANOGRIDATA_MAX_PAYLOAD) || \
    !defined(NANOGRIDATA_MAX_PACKETS) || \
    !defined(NANOGRIDATA_SECURITY_LEVEL_DEFAULT)
  #error "Required configuration not defined"
#endif

// Calculate derived values
#define NANOGRIDATA_TOTAL_BUFFER_SIZE \
  (NANOGRIDATA_MAX_PACKETS * (NANOGRIDATA_MAX_PAYLOAD + 32))

#endif  // NANOGRIDATA_CONFIG_H

