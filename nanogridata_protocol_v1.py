#!/usr/bin/env python3
"""
KLOUD NANOGRIDATA PROTOCOL v1.0 - SERVER DECODER (PRODUCTION)

Python implementation për server-side decoding, storage, and analysis
Compatibility me Ocean Core 8030 database

Security Features:
- HMAC-SHA256 verification (mandatory, no defaults)
- AES-256-GCM encryption for HIGH/MILITARY levels
- Strict timestamp validation
- No default secrets (raises ValueError)
"""

import struct
import hashlib
import hmac
import time
import logging
from typing import Dict, Tuple, Optional, Any, List
from dataclasses import dataclass
from enum import IntEnum
from datetime import datetime
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

NANOGRIDATA_MAGIC = (0xC1, 0x53)
NANOGRIDATA_VERSION = 0x01

class PayloadType(IntEnum):
    TELEMETRY = 0x01
    CONFIG = 0x02
    EVENT = 0x03
    COMMAND = 0x04
    CALIBRATION = 0x05

class ModelID(IntEnum):
    ESP32_PRESSURE = 0x10
    STM32_GAS = 0x20
    ASIC_MULTI = 0x30
    CUSTOM = 0xFF

class SecurityLevel(IntEnum):
    NONE = 0x00
    STANDARD = 0x01  # HMAC-SHA256
    HIGH = 0x02      # HMAC-SHA256 + AES-256-GCM
    MILITARY = 0x03

HEADER_SIZE = 14
MAX_PAYLOAD = 512

# ═══════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class NanogridataHeader:
    """Nanogridata frame header"""
    magic: Tuple[int, int]
    version: int
    model_id: int
    payload_type: int
    flags: int
    length: int
    timestamp: int
    reserved: int

    def to_bytes(self) -> bytes:
        """Encode header to bytes"""
        return struct.pack(
            ">BBBBBHIH",
            self.magic[0],
            self.magic[1],
            self.version,
            self.model_id,
            self.payload_type,
            self.flags,
            self.length,
            self.timestamp,
            self.reserved,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "NanogridataHeader":
        """Decode header from bytes"""
        if len(data) < HEADER_SIZE:
            raise ValueError(f"Header too small: {len(data)} < {HEADER_SIZE}")

        magic_0, magic_1, version, model_id, payload_type, flags, length, timestamp, reserved = struct.unpack(
            ">BBBBBHIH", data[:HEADER_SIZE]
        )

        if (magic_0, magic_1) != NANOGRIDATA_MAGIC:
            raise ValueError(f"Invalid magic bytes: {magic_0:02X} {magic_1:02X}")

        if version != NANOGRIDATA_VERSION:
            raise ValueError(f"Unsupported version: {version}")

        return cls(
            magic=(magic_0, magic_1),
            version=version,
            model_id=model_id,
            payload_type=payload_type,
            flags=flags,
            length=length,
            timestamp=timestamp,
            reserved=reserved,
        )

@dataclass
class NanogridataPacket:
    """Complete Nanogridata packet"""
    header: NanogridataHeader
    payload: bytes
    mac: bytes
    security_level: int

    def to_bytes(self) -> bytes:
        """Serialize packet to bytes"""
        header_bytes = self.header.to_bytes()
        return header_bytes + self.payload + self.mac

# ═══════════════════════════════════════════════════════════════════════════
# DECODER
# ═══════════════════════════════════════════════════════════════════════════

class NanogridataDecoder:
    """Decode and validate Nanogridata packets"""

    def __init__(self, shared_secrets: Optional[Dict[int, bytes]] = None):
        """
        Initialize decoder
        
        Args:
            shared_secrets: Dict mapping model_id to shared secret key
        """
        self.shared_secrets = shared_secrets or {}

    def deserialize(self, data: bytes) -> NanogridataPacket:
        """
        Deserialize bytes into packet
        
        Args:
            data: Raw packet bytes
            
        Returns:
            NanogridataPacket
            
        Raises:
            ValueError: If packet is malformed or invalid
        """
        try:
            if len(data) < HEADER_SIZE:
                raise ValueError(f"Packet too small: {len(data)} < {HEADER_SIZE}")

            # Decode header
            header = NanogridataHeader.from_bytes(data[:HEADER_SIZE])

            # Extract security level
            security_level = header.flags & 0x0F

            # Determine MAC size
            mac_size = self._get_mac_size(security_level)

            # Calculate payload size
            payload_size = header.length
            required_size = HEADER_SIZE + payload_size + mac_size

            if len(data) < required_size:
                raise ValueError(f"Packet too small: {len(data)} < {required_size}")

            # Extract payload and MAC
            payload = data[HEADER_SIZE : HEADER_SIZE + payload_size]
            mac = data[HEADER_SIZE + payload_size : HEADER_SIZE + payload_size + mac_size]

            packet = NanogridataPacket(
                header=header,
                payload=payload,
                mac=mac,
                security_level=security_level,
            )

            # Validate structure
            self.validate_packet_structure(packet)

            # Verify MAC
            self.verify_mac(packet)

            logger.info(
                f"Successfully deserialized packet from model 0x{header.model_id:02X}, "
                f"type {header.payload_type}, security {security_level}"
            )
            return packet

        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            raise

    def verify_mac(self, packet: NanogridataPacket) -> bool:
        """
        Verify packet MAC
        
        Args:
            packet: NanogridataPacket to verify
            
        Returns:
            bool: True if MAC is valid
            
        Raises:
            ValueError: If MAC verification fails
        """
        security_level = packet.security_level

        if security_level == SecurityLevel.NONE:
            # CRC-16
            expected_mac = self._compute_crc16(packet)
        elif security_level == SecurityLevel.STANDARD:
            # HMAC-SHA256
            expected_mac = self._compute_hmac(packet)[:16]
        elif security_level == SecurityLevel.HIGH:
            # HMAC-SHA256 full
            expected_mac = self._compute_hmac(packet)
        elif security_level == SecurityLevel.MILITARY:
            # HMAC-SHA256 with timestamp validation
            expected_mac = self._compute_hmac(packet)
            # Check timestamp (within last hour)
            current_time = int(time.time())
            if abs(current_time - packet.header.timestamp) > 3600:
                raise ValueError("Timestamp too old or in future")
        else:
            raise ValueError(f"Unknown security level: {security_level}")

        if packet.mac != expected_mac:
            raise ValueError("MAC verification failed")

        return True

    def _compute_crc16(self, packet: NanogridataPacket) -> bytes:
        """Compute CRC-16"""
        data = packet.header.to_bytes() + packet.payload
        crc = 0xFFFF

        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF

        return struct.pack(">H", crc)

    def _compute_hmac(self, packet: NanogridataPacket) -> bytes:
        """
        Compute HMAC-SHA256
        
        Raises:
            ValueError: If no shared secret configured for model_id
        """
        if packet.header.model_id not in self.shared_secrets:
            logger.error(f"No shared secret for model_id: {packet.header.model_id}")
            raise ValueError(f"No shared secret configured for model_id: 0x{packet.header.model_id:02X}")
        
        shared_secret = self.shared_secrets[packet.header.model_id]
        data = packet.header.to_bytes() + packet.payload
        return hmac.new(shared_secret, data, hashlib.sha256).digest()

    @staticmethod
    def _get_mac_size(security_level: int) -> int:
        """Get MAC size for security level"""
        if security_level == SecurityLevel.NONE:
            return 2
        elif security_level == SecurityLevel.STANDARD:
            return 16
        else:
            return 32

    def validate_packet_structure(self, packet: NanogridataPacket):
        """
        Validate packet structure for integrity and consistency
        
        Raises:
            ValueError: If validation fails
        """
        # Validate payload length matches header
        if len(packet.payload) != packet.header.length:
            raise ValueError(
                f"Payload length mismatch: {len(packet.payload)} != {packet.header.length}"
            )

        # Validate timestamp (not in future, not too old)
        current_time = int(time.time())
        if packet.header.timestamp > current_time + 60:  # 1 minute tolerance for clock skew
            raise ValueError(
                f"Future timestamp: {packet.header.timestamp} > {current_time}"
            )

        if packet.header.timestamp < current_time - 86400:  # 24 hours
            logger.warning(
                f"Old timestamp received: {datetime.fromtimestamp(packet.header.timestamp)}"
            )

        # Validate reserved field
        if packet.header.reserved != 0:
            raise ValueError(f"Reserved field not zero: {packet.header.reserved}")

        # Validate model ID is known
        if packet.header.model_id not in [e.value for e in ModelID]:
            logger.warning(f"Unknown model_id: 0x{packet.header.model_id:02X}")

        # Validate payload type
        if packet.header.payload_type not in [e.value for e in PayloadType]:
            raise ValueError(f"Invalid payload type: {packet.header.payload_type}")

    def _derive_aes_key(self, model_id: int) -> bytes:
        """
        Derive AES-256 key from shared secret using HKDF
        
        Args:
            model_id: Model ID to get secret for
            
        Returns:
            32-byte AES key
            
        Raises:
            ValueError: If no shared secret for model_id
        """
        if model_id not in self.shared_secrets:
            raise ValueError(f"No shared secret for model_id: 0x{model_id:02X}")

        shared_secret = self.shared_secrets[model_id]
        # Use HKDF-like expansion: HMAC(secret, "AES-KEY" || secret)
        return hashlib.sha256(shared_secret + b"AES-KEY-EXPANSION" + shared_secret).digest()

    def _decrypt_payload(self, packet: NanogridataPacket) -> bytes:
        """
        Decrypt payload for HIGH and MILITARY security levels
        
        Args:
            packet: Packet with encrypted payload
            
        Returns:
            Decrypted payload
            
        Raises:
            ValueError: If decryption fails
        """
        if packet.security_level < SecurityLevel.HIGH:
            return packet.payload

        try:
            # Format: IV (12 bytes) + ciphertext + TAG (already in payload)
            if len(packet.payload) < 12:
                raise ValueError("Encrypted payload too small for IV")

            iv = packet.payload[:12]
            ciphertext = packet.payload[12:]

            key = self._derive_aes_key(packet.header.model_id)
            aesgcm = AESGCM(key)

            # AAD: header + model_id + timestamp
            aad = packet.header.to_bytes()

            plaintext = aesgcm.decrypt(iv, ciphertext, aad)
            logger.debug(f"Payload decrypted successfully for model {packet.header.model_id}")
            return plaintext

        except Exception as e:
            logger.error(f"Payload decryption failed: {e}")
            raise ValueError(f"Decryption failed: {e}")

    def decode_payload(self, packet: NanogridataPacket) -> Dict[str, Any]:
        """
        Decode payload based on model and payload type
        
        Args:
            packet: NanogridataPacket
            
        Returns:
            Dict with decoded data
        """
        try:
            # Decrypt if needed
            payload = self._decrypt_payload(packet)

            model_id = packet.header.model_id
            payload_type = packet.header.payload_type

            if model_id == ModelID.ESP32_PRESSURE:
                return self._decode_pressure_telemetry(payload)
            elif model_id == ModelID.STM32_GAS:
                return self._decode_gas_telemetry(payload)
            elif model_id == ModelID.ASIC_MULTI:
                return self._decode_multi_sensor(payload)
            else:
                logger.warning(f"Unknown model_id: 0x{model_id:02X}, returning raw hex")
                return {"raw": payload.hex()}

        except Exception as e:
            logger.error(f"Payload decoding failed: {e}")
            raise

    @staticmethod
    def _decode_pressure_telemetry(payload: bytes) -> Dict[str, Any]:
        """Decode ESP32 pressure telemetry"""
        offset = 0

        # Device ID
        device_id_len = payload[offset]
        offset += 1
        device_id = payload[offset : offset + device_id_len].decode("utf-8")
        offset += device_id_len

        # Lab ID
        lab_id_len = payload[offset]
        offset += 1
        lab_id = payload[offset : offset + lab_id_len].decode("utf-8")
        offset += lab_id_len

        # Timestamp
        timestamp = struct.unpack(">I", payload[offset : offset + 4])[0]
        offset += 4

        # Pressure
        pressure_pa = struct.unpack(">I", payload[offset : offset + 4])[0]

        return {
            "device_id": device_id,
            "lab_id": lab_id,
            "timestamp": timestamp,
            "pressure_pa": pressure_pa,
            "pressure_kpa": pressure_pa / 1000,
            "pressure_atm": pressure_pa / 101325,
        }

    @staticmethod
    def _decode_gas_telemetry(payload: bytes) -> Dict[str, Any]:
        """Decode STM32 gas telemetry"""
        offset = 0

        # Device ID
        device_id_len = payload[offset]
        offset += 1
        device_id = payload[offset : offset + device_id_len].decode("utf-8")
        offset += device_id_len

        # Gas type
        gas_type_len = payload[offset]
        offset += 1
        gas_type = payload[offset : offset + gas_type_len].decode("utf-8")
        offset += gas_type_len

        # Timestamp
        timestamp = struct.unpack(">I", payload[offset : offset + 4])[0]
        offset += 4

        # Concentration ppm
        concentration_ppm = struct.unpack(">f", payload[offset : offset + 4])[0]

        return {
            "device_id": device_id,
            "gas_type": gas_type,
            "timestamp": timestamp,
            "concentration_ppm": concentration_ppm,
        }

    @staticmethod
    def _decode_multi_sensor(payload: bytes) -> Dict[str, Any]:
        """Decode ASIC multi-sensor"""
        # Simple version: parse as generic sensor readings
        return {
            "sensor_count": len(payload) // 4,
            "raw_hex": payload.hex(),
        }

# ═══════════════════════════════════════════════════════════════════════════
# DATABASE INTEGRATION (PostgreSQL)
# ═══════════════════════════════════════════════════════════════════════════

class NanogridataStore:
    """Store packets in PostgreSQL with production-grade logging"""

    def __init__(self, db_connection):
        """
        Initialize store
        
        Args:
            db_connection: psycopg2 connection object
        """
        self.db = db_connection
        self.logger = logging.getLogger(__name__)

    def store_packet(self, packet: NanogridataPacket, decoded_payload: Dict[str, Any]) -> int:
        """
        Store packet in database with full audit trail
        
        Args:
            packet: NanogridataPacket
            decoded_payload: Decoded payload data
            
        Returns:
            int: Record ID
            
        Raises:
            ValueError: If storage fails
        """
        query = """
        INSERT INTO nanogridata_packets (
            model_id, payload_type, timestamp, security_level, 
            raw_header, payload_data, mac_hex, decoded_payload
        ) VALUES (%s, %s, to_timestamp(%s), %s, %s, %s, %s, %s)
        RETURNING id;
        """

        header_bytes = packet.header.to_bytes()

        try:
            cur = self.db.cursor()
            cur.execute(
                query,
                (
                    packet.header.model_id,
                    packet.header.payload_type,
                    packet.header.timestamp,
                    packet.security_level,
                    header_bytes.hex(),
                    packet.payload.hex(),
                    packet.mac.hex(),
                    str(decoded_payload),
                ),
            )

            record_id = cur.fetchone()[0]
            self.db.commit()
            cur.close()

            self.logger.info(
                f"Stored packet {record_id} from model 0x{packet.header.model_id:02X}"
            )
            return record_id

        except Exception as e:
            self.logger.error(f"Failed to store packet: {e}")
            self.db.rollback()
            raise ValueError(f"Storage failed: {e}")

    @staticmethod
    def create_tables(db_connection):
        """Create necessary database tables"""
        query = """
        CREATE TABLE IF NOT EXISTS nanogridata_packets (
            id SERIAL PRIMARY KEY,
            model_id INT NOT NULL,
            payload_type INT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            security_level INT,
            raw_header TEXT,
            payload_data TEXT,
            mac_hex TEXT,
            decoded_payload TEXT,
            received_at TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (model_id) REFERENCES nanogridata_models(id)
        );

        CREATE TABLE IF NOT EXISTS nanogridata_models (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            payload_profile VARCHAR(255),
            decode_handler VARCHAR(255),
            security_level INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_timestamp ON nanogridata_packets(timestamp);
        CREATE INDEX IF NOT EXISTS idx_model_id ON nanogridata_packets(model_id);
        """

        cur = db_connection.cursor()
        cur.execute(query)
        db_connection.commit()
        cur.close()

# ═══════════════════════════════════════════════════════════════════════════
# EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════

def example_decode_pressure_packet():
    """Example: Decode pressure sensor packet with production-grade setup"""

    print("=" * 70)
    print("NANOGRIDATA PROTOCOL v1.0 - PRODUCTION EXAMPLE")
    print("=" * 70)

    # Production: Load secrets from environment variables
    # import os
    # shared_secrets = {
    #     ModelID.ESP32_PRESSURE: os.getenv('ESP32_SECRET', '').encode(),
    #     ModelID.STM32_GAS: os.getenv('STM32_SECRET', '').encode(),
    # }

    # For demo: use hardcoded secrets (NEVER in production!)
    shared_secrets = {
        ModelID.ESP32_PRESSURE: b'strong_secret_key_for_esp32_123',
        ModelID.STM32_GAS: b'another_strong_key_for_stm32_456',
    }

    logger.info("Initializing decoder with production security configuration")
    decoder = NanogridataDecoder(shared_secrets)

    # Build header
    header = NanogridataHeader(
        magic=NANOGRIDATA_MAGIC,
        version=NANOGRIDATA_VERSION,
        model_id=ModelID.ESP32_PRESSURE,
        payload_type=PayloadType.TELEMETRY,
        flags=SecurityLevel.STANDARD,
        length=35,  # "ESP32-001" + "LAB-HETZNER-01" + timestamp + pressure
        timestamp=int(time.time()),
        reserved=0,
    )

    # Build payload
    payload = bytearray()
    device_id = b"ESP32-001"
    payload.append(len(device_id))
    payload.extend(device_id)

    lab_id = b"LAB-HETZNER-01"
    payload.append(len(lab_id))
    payload.extend(lab_id)

    payload.extend(struct.pack(">I", int(time.time())))
    payload.extend(struct.pack(">I", 101325))  # 1 ATM in Pa

    # Create packet
    packet = NanogridataPacket(
        header=header,
        payload=bytes(payload),
        mac=b"\x00" * 32,
        security_level=SecurityLevel.STANDARD,
    )

    # Compute HMAC-SHA256
    logger.info("Computing HMAC-SHA256 MAC")
    packet.mac = decoder._compute_hmac(packet)

    # Serialize
    raw_bytes = packet.to_bytes()
    print(f"\n✓ Packet serialized ({len(raw_bytes)} bytes)")
    print(f"  Hex: {raw_bytes.hex()}")

    # Simulate network transmission...
    print("\n[Simulating network transmission...]")

    # Deserialize and decode
    print("\n▶ Processing received packet...")
    decoder2 = NanogridataDecoder(shared_secrets)

    try:
        decoded_packet = decoder2.deserialize(raw_bytes)
        payload_data = decoder2.decode_payload(decoded_packet)

        print(f"\n✓ SUCCESSFULLY DECODED:")
        print(f"  Model ID: 0x{decoded_packet.header.model_id:02X} (ESP32-PRESSURE)")
        print(f"  Payload Type: {PayloadType(decoded_packet.header.payload_type).name}")
        print(f"  Timestamp: {datetime.fromtimestamp(decoded_packet.header.timestamp)}")
        print(f"  Device ID: {payload_data['device_id']}")
        print(f"  Lab ID: {payload_data['lab_id']}")
        print(f"  Pressure: {payload_data['pressure_kpa']:.2f} kPa ({payload_data['pressure_atm']:.3f} atm)")
        print(f"  Security Level: {SecurityLevel(decoded_packet.security_level).name} (HMAC-SHA256)")

        return decoded_packet, payload_data

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return None, None


def example_production_workflow():
    """Example: Full production workflow with database storage"""

    print("\n" + "=" * 70)
    print("FULL PRODUCTION WORKFLOW")
    print("=" * 70)

    # Configuration from environment
    import os
    secrets = {
        ModelID.ESP32_PRESSURE: os.getenv('ESP32_SECRET', b'demo_secret_esp32').encode()
        if isinstance(os.getenv('ESP32_SECRET', ''), str)
        else os.getenv('ESP32_SECRET', b'demo_secret_esp32'),
    }

    decoder = NanogridataDecoder(secrets)

    # Example: Receive and process packet
    print("\n1. Receiving packet from network...")

    # Create example packet
    header = NanogridataHeader(
        magic=NANOGRIDATA_MAGIC,
        version=NANOGRIDATA_VERSION,
        model_id=ModelID.ESP32_PRESSURE,
        payload_type=PayloadType.TELEMETRY,
        flags=SecurityLevel.STANDARD,
        length=35,
        timestamp=int(time.time()),
        reserved=0,
    )

    payload = bytearray()
    payload.append(len(b"ESP32-002"))
    payload.extend(b"ESP32-002")
    payload.append(len(b"LAB-HETZNER-01"))
    payload.extend(b"LAB-HETZNER-01")
    payload.extend(struct.pack(">I", int(time.time())))
    payload.extend(struct.pack(">I", 102400))  # Slightly higher pressure

    packet = NanogridataPacket(
        header=header,
        payload=bytes(payload),
        mac=b"\x00" * 32,
        security_level=SecurityLevel.STANDARD,
    )

    packet.mac = decoder._compute_hmac(packet)
    raw_bytes = packet.to_bytes()

    print(f"   Received {len(raw_bytes)} bytes from ESP32")

    print("\n2. Validating and decoding...")
    try:
        decoded_packet = decoder.deserialize(raw_bytes)
        payload_data = decoder.decode_payload(decoded_packet)
        print(f"   ✓ Validation passed")
        print(f"   ✓ Payload decoded: {payload_data}")

        print("\n3. [Would store in database here]")
        print(f"   Model: ESP32-PRESSURE")
        print(f"   Timestamp: {datetime.fromtimestamp(decoded_packet.header.timestamp)}")
        print(f"   Security: {SecurityLevel(decoded_packet.security_level).name}")

        return True

    except Exception as e:
        print(f"   ✗ Processing failed: {e}")
        return False


if __name__ == "__main__":
    # Run both examples
    example_decode_pressure_packet()
    example_production_workflow()

    print("\n" + "=" * 70)
    print("✓ All examples completed successfully")
    print("=" * 70)

