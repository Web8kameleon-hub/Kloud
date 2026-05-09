/**
 * 🔷 KLOUD BINARY PROTOCOL (CBP) - C SDK
 * ==========================================
 * 
 * Header-only C library for Kloud Binary Protocol.
 * 
 * Frame Layout:
 *   Offset | Size | Field
 *   -------|------|-------------------------
 *   0      | 4    | Magic "CLSN"
 *   4      | 1    | Version
 *   5      | 1    | Flags
 *   6      | 2    | Payload length (uint16)
 *   8      | N    | Payload (binary struct)
 * 
 * Author: Kloud Team
 * License: MIT
 */

#ifndef KLOUD_CBP_H
#define KLOUD_CBP_H

/* Standard types - with fallback for environments without stdint.h */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
    #include <stdint.h>
#elif defined(_MSC_VER)
    /* MSVC */
    typedef unsigned __int8  uint8_t;
    typedef unsigned __int16 uint16_t;
    typedef unsigned __int32 uint32_t;
    typedef unsigned __int64 uint64_t;
    typedef signed __int8    int8_t;
    typedef signed __int16   int16_t;
    typedef signed __int32   int32_t;
    typedef signed __int64   int64_t;
#else
    /* Fallback for other compilers */
    typedef unsigned char      uint8_t;
    typedef unsigned short     uint16_t;
    typedef unsigned int       uint32_t;
    typedef unsigned long long uint64_t;
    typedef signed char        int8_t;
    typedef signed short       int16_t;
    typedef signed int         int32_t;
    typedef signed long long   int64_t;
#endif

/* size_t and NULL definition with fallback */
#ifndef _SIZE_T_DEFINED
    #define _SIZE_T_DEFINED
    #if defined(_MSC_VER)
        #ifdef _WIN64
            typedef unsigned __int64 size_t;
        #else
            typedef unsigned int size_t;
        #endif
    #elif defined(__SIZEOF_POINTER__) && __SIZEOF_POINTER__ == 8
        typedef unsigned long long size_t;
    #else
        typedef unsigned long size_t;
    #endif
#endif

#ifndef NULL
    #ifdef __cplusplus
        #define NULL 0
    #else
        #define NULL ((void*)0)
    #endif
#endif

#include <string.h>

/* Boolean type */
#ifndef __cplusplus
    #if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
        #include <stdbool.h>
    #else
        typedef int bool;
        #define true 1
        #define false 0
    #endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== CONSTANTS ==================== */

#define CBP_MAGIC           "CLSN"
#define CBP_MAGIC_SIZE      4
#define CBP_VERSION         1
#define CBP_HEADER_SIZE     8
#define CBP_MAX_PAYLOAD     65535

/* ==================== FLAGS ==================== */

typedef enum {
    CBP_FLAG_NONE        = 0x00,
    CBP_FLAG_COMPRESSED  = 0x01,  /* bit 0: zlib compressed */
    CBP_FLAG_ENCRYPTED   = 0x02,  /* bit 1: AES-GCM encrypted */
    CBP_FLAG_CHUNKED     = 0x04,  /* bit 2: chunked transfer */
    CBP_FLAG_ERROR       = 0x08,  /* bit 3: error frame */
    CBP_FLAG_LAST_CHUNK  = 0x10,  /* bit 4: last chunk marker */
    CBP_FLAG_HAS_CHECKSUM = 0x20  /* bit 5: has CRC32 checksum */
} cbp_flags_t;

/* ==================== MESSAGE TYPES ==================== */

typedef enum {
    CBP_TYPE_UNKNOWN   = 0x00,
    CBP_TYPE_CALCULATE = 0x01,
    CBP_TYPE_CHAT      = 0x02,
    CBP_TYPE_TIME      = 0x03,
    CBP_TYPE_STATUS    = 0x04,
    CBP_TYPE_SIGNAL    = 0x10,
    CBP_TYPE_STREAM    = 0x20,
    CBP_TYPE_ALGEBRA   = 0x30,
    CBP_TYPE_ERROR     = 0xFF
} cbp_message_type_t;

/* ==================== FRAME STRUCTURE ==================== */

#pragma pack(push, 1)

typedef struct {
    char     magic[4];       /* "CLSN" */
    uint8_t  version;        /* Protocol version */
    uint8_t  flags;          /* Frame flags */
    uint16_t payload_len;    /* Payload length (big-endian) */
} cbp_header_t;

typedef struct {
    cbp_header_t header;
    uint8_t      payload[CBP_MAX_PAYLOAD];
} cbp_frame_t;

/* ==================== RESPONSE STRUCTURES ==================== */

typedef struct {
    uint8_t  type;           /* 0x01 */
    double   result;         /* Calculation result */
    uint32_t duration_us;    /* Duration in microseconds */
    uint16_t expr_len;       /* Expression length */
    /* followed by: char expression[expr_len] */
} cbp_calculate_response_t;

typedef struct {
    uint8_t  type;           /* 0x02 */
    uint8_t  intent;         /* Intent type */
    float    confidence;     /* Confidence score */
    uint16_t response_len;   /* Response text length */
    /* followed by: char response[response_len] */
} cbp_chat_response_t;

typedef struct {
    uint8_t  type;           /* 0x03 */
    uint64_t timestamp;      /* Unix timestamp */
    uint16_t year;
    uint8_t  month;
    uint8_t  day;
    uint8_t  hour;
    uint8_t  minute;
    uint8_t  second;
    uint32_t microsecond;
} cbp_time_response_t;

typedef struct {
    uint8_t  type;           /* 0x30 */
    uint8_t  operation;      /* AND=1, OR=2, XOR=3, NOT=4, SHL=5, SHR=6 */
    uint64_t operand_a;
    uint64_t operand_b;
    uint64_t result;
    uint8_t  bits;
} cbp_algebra_response_t;

typedef struct {
    uint8_t  type;           /* 0x20 */
    uint32_t stream_id;
    uint32_t sequence;
    uint16_t payload_len;
    /* followed by: uint8_t payload[payload_len] */
} cbp_stream_frame_t;

#pragma pack(pop)

/* ==================== ERROR CODES ==================== */

typedef enum {
    CBP_OK = 0,
    CBP_ERR_INVALID_MAGIC,
    CBP_ERR_INVALID_VERSION,
    CBP_ERR_BUFFER_TOO_SMALL,
    CBP_ERR_PAYLOAD_TOO_LARGE,
    CBP_ERR_CHECKSUM_MISMATCH,
    CBP_ERR_DECRYPTION_FAILED,
    CBP_ERR_DECOMPRESSION_FAILED
} cbp_error_t;

/* ==================== UTILITY FUNCTIONS ==================== */

/**
 * Convert uint16_t to big-endian
 */
static inline uint16_t cbp_htons(uint16_t val) {
    return ((val & 0xFF) << 8) | ((val >> 8) & 0xFF);
}

/**
 * Convert big-endian uint16_t to host order
 */
static inline uint16_t cbp_ntohs(uint16_t val) {
    return cbp_htons(val);  /* Same operation */
}

/**
 * Simple CRC32 implementation
 */
static inline uint32_t cbp_crc32(const uint8_t* data, size_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* ==================== FRAME FUNCTIONS ==================== */

/**
 * Initialize a CBP header
 */
static inline void cbp_header_init(cbp_header_t* header, uint8_t flags, uint16_t payload_len) {
    memcpy(header->magic, CBP_MAGIC, CBP_MAGIC_SIZE);
    header->version = CBP_VERSION;
    header->flags = flags;
    header->payload_len = cbp_htons(payload_len);
}

/**
 * Validate a CBP header
 */
static inline cbp_error_t cbp_header_validate(const cbp_header_t* header) {
    if (memcmp(header->magic, CBP_MAGIC, CBP_MAGIC_SIZE) != 0) {
        return CBP_ERR_INVALID_MAGIC;
    }
    if (header->version != CBP_VERSION) {
        return CBP_ERR_INVALID_VERSION;
    }
    return CBP_OK;
}

/**
 * Get payload length from header
 */
static inline uint16_t cbp_header_payload_len(const cbp_header_t* header) {
    return cbp_ntohs(header->payload_len);
}

/**
 * Check if frame has specific flag
 */
static inline bool cbp_header_has_flag(const cbp_header_t* header, cbp_flags_t flag) {
    return (header->flags & flag) != 0;
}

/**
 * Encode a frame to buffer
 * Returns total bytes written, or 0 on error
 */
static inline size_t cbp_frame_encode(
    uint8_t* buffer,
    size_t buffer_size,
    uint8_t flags,
    const uint8_t* payload,
    uint16_t payload_len
) {
    size_t total_size = CBP_HEADER_SIZE + payload_len;
    
    /* Check for checksum */
    if (flags & CBP_FLAG_HAS_CHECKSUM) {
        total_size += 4;
    }
    
    if (buffer_size < total_size) {
        return 0;
    }
    
    /* Write header */
    cbp_header_t* header = (cbp_header_t*)buffer;
    cbp_header_init(header, flags, payload_len);
    
    /* Write payload */
    if (payload && payload_len > 0) {
        memcpy(buffer + CBP_HEADER_SIZE, payload, payload_len);
    }
    
    /* Write checksum if needed */
    if (flags & CBP_FLAG_HAS_CHECKSUM) {
        uint32_t crc = cbp_crc32(payload, payload_len);
        memcpy(buffer + CBP_HEADER_SIZE + payload_len, &crc, 4);
    }
    
    return total_size;
}

/**
 * Decode a frame from buffer
 * Returns CBP_OK on success
 */
static inline cbp_error_t cbp_frame_decode(
    const uint8_t* buffer,
    size_t buffer_size,
    cbp_header_t* header_out,
    const uint8_t** payload_out,
    uint16_t* payload_len_out
) {
    if (buffer_size < CBP_HEADER_SIZE) {
        return CBP_ERR_BUFFER_TOO_SMALL;
    }
    
    /* Parse header */
    const cbp_header_t* header = (const cbp_header_t*)buffer;
    
    cbp_error_t err = cbp_header_validate(header);
    if (err != CBP_OK) {
        return err;
    }
    
    uint16_t payload_len = cbp_header_payload_len(header);
    
    if (buffer_size < CBP_HEADER_SIZE + payload_len) {
        return CBP_ERR_BUFFER_TOO_SMALL;
    }
    
    /* Verify checksum if present */
    if (cbp_header_has_flag(header, CBP_FLAG_HAS_CHECKSUM)) {
        if (buffer_size < CBP_HEADER_SIZE + payload_len + 4) {
            return CBP_ERR_BUFFER_TOO_SMALL;
        }
        
        uint32_t stored_crc;
        memcpy(&stored_crc, buffer + CBP_HEADER_SIZE + payload_len, 4);
        
        uint32_t calc_crc = cbp_crc32(buffer + CBP_HEADER_SIZE, payload_len);
        
        if (stored_crc != calc_crc) {
            return CBP_ERR_CHECKSUM_MISMATCH;
        }
    }
    
    /* Output results */
    if (header_out) {
        memcpy(header_out, header, sizeof(cbp_header_t));
    }
    if (payload_out) {
        *payload_out = buffer + CBP_HEADER_SIZE;
    }
    if (payload_len_out) {
        *payload_len_out = payload_len;
    }
    
    return CBP_OK;
}

/**
 * Get message type from payload
 */
static inline cbp_message_type_t cbp_payload_get_type(const uint8_t* payload) {
    if (payload == NULL) return CBP_TYPE_UNKNOWN;
    return (cbp_message_type_t)payload[0];
}

/* ==================== CONVENIENCE MACROS ==================== */

#define CBP_FRAME_TOTAL_SIZE(payload_len) (CBP_HEADER_SIZE + (payload_len))
#define CBP_FRAME_MAX_SIZE (CBP_HEADER_SIZE + CBP_MAX_PAYLOAD + 4)

/* ==================== EXAMPLE USAGE ==================== */

/*
 * // Encode example:
 * uint8_t buffer[256];
 * uint8_t payload[] = {0x01, 0x00, 0x00, 0x00};  // type + result
 * size_t len = cbp_frame_encode(buffer, sizeof(buffer), 
 *                               CBP_FLAG_HAS_CHECKSUM, 
 *                               payload, sizeof(payload));
 * 
 * // Decode example:
 * cbp_header_t header;
 * const uint8_t* payload;
 * uint16_t payload_len;
 * cbp_error_t err = cbp_frame_decode(buffer, len, &header, &payload, &payload_len);
 * if (err == CBP_OK) {
 *     cbp_message_type_t type = cbp_payload_get_type(payload);
 *     // Handle message...
 * }
 */

#ifdef __cplusplus
}
#endif

#endif /* KLOUD_CBP_H */

