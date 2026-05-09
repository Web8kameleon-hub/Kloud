# -*- coding: utf-8 -*-
"""
🔷 KLOUD BINARY PROTOCOL (CBP)
=================================
Protokoll i plotë binar për Kloud.

Frame Layout:
┌──────────┬─────────┬───────┬────────────────┬─────────────┐
│ Magic(4) │ Ver(1)  │Flags(1│ PayloadLen(2)  │ Payload(N)  │
│ "CLSN"   │ 0x01    │       │ uint16 BE      │ binary      │
└──────────┴─────────┴───────┴────────────────┴─────────────┘

Flags:
- bit 0: compressed (zlib)
- bit 1: encrypted (AES-GCM)
- bit 2: chunked
- bit 3: error frame
- bit 4: last chunk
- bit 5-7: reserved

Features:
- Schema Registry
- Binary Request/Response
- Streaming
- Compression
- Encryption (optional)
- Schema validation

Author: Kloud Team
"""

import struct
import zlib
import os
try:
    import yaml
except ImportError:
    yaml = None  # Will use simple parser
try:
    from .cbp_encryption import get_encryption, CbpEncryption
    HAS_ENCRYPTION = True
except ImportError:
    HAS_ENCRYPTION = False
from typing import Dict, Any, List, Optional, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import IntEnum, IntFlag
from datetime import datetime
from pathlib import Path
import io


# ============ CONSTANTS ============

MAGIC_CLSN = b'CLSN'
MAGIC_BALG = b'BALG'
PROTOCOL_VERSION = 1
HEADER_SIZE = 8  # magic(4) + version(1) + flags(1) + payload_len(2)


class FrameFlags(IntFlag):
    """Frame flags"""
    NONE = 0x00
    COMPRESSED = 0x01      # bit 0
    ENCRYPTED = 0x02       # bit 1
    CHUNKED = 0x04         # bit 2
    ERROR = 0x08           # bit 3
    LAST_CHUNK = 0x10      # bit 4
    HAS_CHECKSUM = 0x20    # bit 5
    # bits 6-7 reserved


class MessageType(IntEnum):
    """Message types"""
    UNKNOWN = 0x00
    CALCULATE = 0x01
    CHAT = 0x02
    TIME = 0x03
    STATUS = 0x04
    SIGNAL = 0x10
    STREAM = 0x20
    ALGEBRA = 0x30
    ERROR = 0xFF


class DataType(IntEnum):
    """Field data types"""
    NULL = 0
    UINT8 = 1
    UINT16 = 2
    UINT32 = 3
    UINT64 = 4
    INT8 = 5
    INT16 = 6
    INT32 = 7
    INT64 = 8
    FLOAT = 9
    DOUBLE = 10
    STRING = 11
    BYTES = 12
    BOOL = 13
    ARRAY = 14
    MAP = 15


# ============ SCHEMA ============

@dataclass
class SchemaField:
    """Field definition in schema"""
    name: str
    dtype: DataType
    offset: int = -1  # -1 = dynamic
    length_field: Optional[str] = None
    description: str = ""
    default: Any = None


@dataclass 
class Schema:
    """Binary schema definition"""
    name: str
    version: int
    type_id: int
    fields: List[SchemaField]
    
    def get_field(self, name: str) -> Optional[SchemaField]:
        for f in self.fields:
            if f.name == name:
                return f
        return None


class SchemaRegistry:
    """Registry for .clsn schemas"""
    
    def __init__(self, schema_dir: Optional[str] = None):
        self.schemas: Dict[str, Schema] = {}
        self.type_map: Dict[int, Schema] = {}
        
        if schema_dir:
            self.load_directory(schema_dir)
    
    def load_directory(self, path: str):
        """Load all .clsn files from directory"""
        p = Path(path)
        if p.exists():
            for f in p.glob("*.clsn"):
                self.load_file(str(f))
    
    def load_file(self, path: str):
        """Load single .clsn file"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            # Parse YAML-like format
            if yaml:
                data = yaml.safe_load(content)
            else:
                data = self._simple_parse(content)
            
            if not data:
                return
            
            # Build schema
            fields = []
            for fd in data.get('fields', []):
                dtype = self._parse_type(fd.get('type', 'bytes'))
                fields.append(SchemaField(
                    name=fd.get('name', ''),
                    dtype=dtype,
                    offset=fd.get('offset', -1) if fd.get('offset') != 'dynamic' else -1,
                    length_field=fd.get('length_field'),
                    description=fd.get('description', '')
                ))
            
            schema = Schema(
                name=data.get('name', ''),
                version=data.get('version', 1),
                type_id=int(str(data.get('type_id', '0')), 0),
                fields=fields
            )
            
            self.schemas[schema.name] = schema
            self.type_map[schema.type_id] = schema
            
        except Exception as e:
            print(f"Error loading schema {path}: {e}")
    
    def _parse_type(self, type_str: str) -> DataType:
        """Parse type string to DataType"""
        type_map = {
            'uint8': DataType.UINT8,
            'uint16': DataType.UINT16,
            'uint32': DataType.UINT32,
            'uint64': DataType.UINT64,
            'int8': DataType.INT8,
            'int16': DataType.INT16,
            'int32': DataType.INT32,
            'int64': DataType.INT64,
            'float': DataType.FLOAT,
            'double': DataType.DOUBLE,
            'string': DataType.STRING,
            'bytes': DataType.BYTES,
            'bool': DataType.BOOL,
        }
        return type_map.get(type_str.lower(), DataType.BYTES)
    
    def _simple_parse(self, content: str) -> Dict[str, Any]:
        """Simple YAML-like parser for .clsn files"""
        result = {}
        current_list = None
        current_item = None
        
        for line in content.split('\n'):
            line = line.rstrip()
            if not line or line.startswith('#'):
                continue
            
            # Check indentation
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            
            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                if indent == 0:
                    if value:
                        result[key] = value
                    else:
                        result[key] = []
                        current_list = result[key]
                elif indent >= 2 and stripped.startswith('- '):
                    # List item
                    item_str = stripped[2:]
                    if ':' in item_str:
                        k, v = item_str.split(':', 1)
                        current_item = {k.strip(): v.strip().strip('"')}
                        if current_list is not None:
                            current_list.append(current_item)
                elif current_item is not None:
                    current_item[key] = value
        
        return result
    
    def get(self, name: str) -> Optional[Schema]:
        return self.schemas.get(name)
    
    def get_by_type(self, type_id: int) -> Optional[Schema]:
        return self.type_map.get(type_id)


# ============ FRAME ============

@dataclass
class Frame:
    """Binary frame"""
    magic: bytes = MAGIC_CLSN
    version: int = PROTOCOL_VERSION
    flags: FrameFlags = FrameFlags.NONE
    payload: bytes = b''
    checksum: Optional[int] = None
    encryption_key: Optional[bytes] = None  # For encryption support
    
    @property
    def payload_len(self) -> int:
        return len(self.payload)
    
    def to_bytes(self, encrypt_key: Optional[bytes] = None) -> bytes:
        """Serialize frame to bytes"""
        # Add checksum if requested
        payload = self.payload
        flags = self.flags
        
        # Encrypt first if requested
        if FrameFlags.ENCRYPTED in flags and (encrypt_key or self.encryption_key):
            if HAS_ENCRYPTION:
                key = encrypt_key or self.encryption_key
                encryptor = get_encryption(key)
                # Build header for AAD
                header = self.magic + bytes([self.version, int(flags)])
                payload = encryptor.encrypt(payload, associated_data=header)
            else:
                # Remove encrypted flag if no encryption available
                flags = flags & ~FrameFlags.ENCRYPTED
        
        if FrameFlags.COMPRESSED in flags:
            payload = zlib.compress(payload)
        
        if FrameFlags.HAS_CHECKSUM in flags:
            checksum = zlib.crc32(payload) & 0xFFFFFFFF
            payload = payload + struct.pack('>I', checksum)
        
        # Build frame
        frame = bytearray()
        frame.extend(self.magic)
        frame.append(self.version)
        frame.append(int(flags))
        frame.extend(struct.pack('>H', len(payload)))
        frame.extend(payload)
        
        return bytes(frame)
    
    @classmethod
    def from_bytes(cls, data: bytes, decrypt_key: Optional[bytes] = None) -> 'Frame':
        """Deserialize frame from bytes"""
        if len(data) < HEADER_SIZE:
            raise ValueError(f"Frame too short: {len(data)} < {HEADER_SIZE}")
        
        magic = data[0:4]
        version = data[4]
        flags = FrameFlags(data[5])
        payload_len = struct.unpack('>H', data[6:8])[0]
        payload = data[8:8+payload_len]
        
        # Verify checksum if present
        checksum = None
        if FrameFlags.HAS_CHECKSUM in flags:
            checksum = struct.unpack('>I', payload[-4:])[0]
            payload = payload[:-4]
            actual = zlib.crc32(payload) & 0xFFFFFFFF
            if actual != checksum:
                raise ValueError(f"Checksum mismatch: {actual} != {checksum}")
        
        # Decompress if needed
        if FrameFlags.COMPRESSED in flags:
            payload = zlib.decompress(payload)
        
        # Decrypt if needed
        if FrameFlags.ENCRYPTED in flags and decrypt_key:
            if HAS_ENCRYPTION:
                decryptor = get_encryption(decrypt_key)
                # Build header for AAD
                header = magic + bytes([version, int(flags)])
                payload = decryptor.decrypt(payload, associated_data=header)
        
        return cls(
            magic=magic,
            version=version,
            flags=flags,
            payload=payload,
            checksum=checksum
        )


# ============ ENCODER/DECODER ============

class BinaryEncoder:
    """Encode Python objects to binary"""
    
    def __init__(self, registry: Optional[SchemaRegistry] = None):
        self.registry = registry
    
    def encode(self, data: Dict[str, Any], schema_name: Optional[str] = None) -> bytes:
        """Encode dict to binary payload"""
        buf = io.BytesIO()
        
        for key, value in data.items():
            self._encode_field(buf, key, value)
        
        return buf.getvalue()
    
    def _encode_field(self, buf: BinaryIO, key: str, value: Any):
        """Encode single field"""
        # Key: length + bytes
        key_bytes = key.encode('utf-8')
        buf.write(struct.pack('B', len(key_bytes)))
        buf.write(key_bytes)
        
        # Value: type + data
        if value is None:
            buf.write(struct.pack('B', DataType.NULL))
        elif isinstance(value, bool):
            buf.write(struct.pack('BB', DataType.BOOL, 1 if value else 0))
        elif isinstance(value, int):
            if -128 <= value <= 127:
                buf.write(struct.pack('>Bb', DataType.INT8, value))
            elif -32768 <= value <= 32767:
                buf.write(struct.pack('>Bh', DataType.INT16, value))
            elif -2147483648 <= value <= 2147483647:
                buf.write(struct.pack('>Bi', DataType.INT32, value))
            else:
                buf.write(struct.pack('>Bq', DataType.INT64, value))
        elif isinstance(value, float):
            buf.write(struct.pack('>Bd', DataType.DOUBLE, value))
        elif isinstance(value, str):
            val_bytes = value.encode('utf-8')
            buf.write(struct.pack('>BH', DataType.STRING, len(val_bytes)))
            buf.write(val_bytes)
        elif isinstance(value, bytes):
            buf.write(struct.pack('>BH', DataType.BYTES, len(value)))
            buf.write(value)
        elif isinstance(value, list):
            buf.write(struct.pack('>BH', DataType.ARRAY, len(value)))
            for item in value:
                self._encode_field(buf, '', item)
        elif isinstance(value, dict):
            buf.write(struct.pack('>BH', DataType.MAP, len(value)))
            for k, v in value.items():
                self._encode_field(buf, k, v)
        else:
            # Fallback: convert to string
            val_bytes = str(value).encode('utf-8')
            buf.write(struct.pack('>BH', DataType.STRING, len(val_bytes)))
            buf.write(val_bytes)
    
    def decode(self, data: bytes) -> Dict[str, Any]:
        """Decode binary payload to dict"""
        buf = io.BytesIO(data)
        result = {}
        
        while buf.tell() < len(data):
            try:
                key, value = self._decode_field(buf)
                if key:
                    result[key] = value
            except:
                break
        
        return result
    
    def _decode_field(self, buf: BinaryIO) -> Tuple[str, Any]:
        """Decode single field"""
        # Key
        key_len = struct.unpack('B', buf.read(1))[0]
        key = buf.read(key_len).decode('utf-8') if key_len > 0 else ''
        
        # Type
        dtype = DataType(struct.unpack('B', buf.read(1))[0])
        
        # Value
        if dtype == DataType.NULL:
            return key, None
        elif dtype == DataType.BOOL:
            return key, struct.unpack('B', buf.read(1))[0] != 0
        elif dtype == DataType.INT8:
            return key, struct.unpack('b', buf.read(1))[0]
        elif dtype == DataType.INT16:
            return key, struct.unpack('>h', buf.read(2))[0]
        elif dtype == DataType.INT32:
            return key, struct.unpack('>i', buf.read(4))[0]
        elif dtype == DataType.INT64:
            return key, struct.unpack('>q', buf.read(8))[0]
        elif dtype == DataType.UINT8:
            return key, struct.unpack('B', buf.read(1))[0]
        elif dtype == DataType.UINT16:
            return key, struct.unpack('>H', buf.read(2))[0]
        elif dtype == DataType.UINT32:
            return key, struct.unpack('>I', buf.read(4))[0]
        elif dtype == DataType.UINT64:
            return key, struct.unpack('>Q', buf.read(8))[0]
        elif dtype == DataType.FLOAT:
            return key, struct.unpack('>f', buf.read(4))[0]
        elif dtype == DataType.DOUBLE:
            return key, struct.unpack('>d', buf.read(8))[0]
        elif dtype == DataType.STRING:
            length = struct.unpack('>H', buf.read(2))[0]
            return key, buf.read(length).decode('utf-8')
        elif dtype == DataType.BYTES:
            length = struct.unpack('>H', buf.read(2))[0]
            return key, buf.read(length)
        elif dtype == DataType.ARRAY:
            length = struct.unpack('>H', buf.read(2))[0]
            items = []
            for _ in range(length):
                _, val = self._decode_field(buf)
                items.append(val)
            return key, items
        elif dtype == DataType.MAP:
            length = struct.unpack('>H', buf.read(2))[0]
            items = {}
            for _ in range(length):
                k, v = self._decode_field(buf)
                items[k] = v
            return key, items
        else:
            return key, None


# ============ STREAMING ============

@dataclass
class StreamFrame:
    """Frame for streaming data"""
    stream_id: int
    sequence: int
    payload: bytes
    flags: FrameFlags = FrameFlags.NONE
    
    def to_bytes(self) -> bytes:
        """Serialize stream frame"""
        buf = bytearray()
        buf.extend(MAGIC_CLSN)
        buf.append(PROTOCOL_VERSION)
        buf.append(int(self.flags | FrameFlags.CHUNKED))
        buf.extend(struct.pack('>H', len(self.payload) + 6))  # +6 for stream_id + seq
        buf.extend(struct.pack('>H', self.stream_id))
        buf.extend(struct.pack('>I', self.sequence))
        buf.extend(self.payload)
        return bytes(buf)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'StreamFrame':
        """Deserialize stream frame"""
        frame = Frame.from_bytes(data)
        if FrameFlags.CHUNKED not in frame.flags:
            raise ValueError("Not a stream frame")
        
        stream_id = struct.unpack('>H', frame.payload[0:2])[0]
        sequence = struct.unpack('>I', frame.payload[2:6])[0]
        payload = frame.payload[6:]
        
        return cls(
            stream_id=stream_id,
            sequence=sequence,
            payload=payload,
            flags=frame.flags
        )


class BinaryStream:
    """Binary streaming handler"""
    
    def __init__(self, stream_id: int = 0, chunk_size: int = 1024):
        self.stream_id = stream_id
        self.chunk_size = chunk_size
        self.sequence = 0
        self.buffer = bytearray()
    
    def write(self, data: bytes) -> List[StreamFrame]:
        """Write data and return frames"""
        frames = []
        self.buffer.extend(data)
        
        while len(self.buffer) >= self.chunk_size:
            chunk = bytes(self.buffer[:self.chunk_size])
            self.buffer = self.buffer[self.chunk_size:]
            
            frame = StreamFrame(
                stream_id=self.stream_id,
                sequence=self.sequence,
                payload=chunk
            )
            frames.append(frame)
            self.sequence += 1
        
        return frames
    
    def flush(self) -> Optional[StreamFrame]:
        """Flush remaining data"""
        if self.buffer:
            chunk = bytes(self.buffer)
            self.buffer.clear()
            
            frame = StreamFrame(
                stream_id=self.stream_id,
                sequence=self.sequence,
                payload=chunk,
                flags=FrameFlags.LAST_CHUNK
            )
            self.sequence += 1
            return frame
        return None
    
    def read(self, frames: List[StreamFrame]) -> bytes:
        """Reconstruct data from frames"""
        # Sort by sequence
        sorted_frames = sorted(frames, key=lambda f: f.sequence)
        return b''.join(f.payload for f in sorted_frames)


# ============ PROTOCOL ============

class KloudProtocol:
    """Main protocol handler"""
    
    def __init__(self, schema_dir: Optional[str] = None):
        self.registry = SchemaRegistry(schema_dir)
        self.encoder = BinaryEncoder(self.registry)
        self.streams: Dict[int, BinaryStream] = {}
    
    def encode_message(self, 
                       data: Dict[str, Any],
                       msg_type: MessageType = MessageType.UNKNOWN,
                       compress: bool = False,
                       checksum: bool = True) -> bytes:
        """Encode message to binary frame"""
        # Build payload
        payload = bytearray()
        payload.append(int(msg_type))
        payload.extend(self.encoder.encode(data))
        
        # Build flags
        flags = FrameFlags.NONE
        if compress:
            flags |= FrameFlags.COMPRESSED
        if checksum:
            flags |= FrameFlags.HAS_CHECKSUM
        
        # Build frame
        frame = Frame(
            magic=MAGIC_CLSN,
            version=PROTOCOL_VERSION,
            flags=flags,
            payload=bytes(payload)
        )
        
        return frame.to_bytes()
    
    def decode_message(self, data: bytes) -> Tuple[MessageType, Dict[str, Any]]:
        """Decode binary frame to message"""
        frame = Frame.from_bytes(data)
        
        if len(frame.payload) < 1:
            return MessageType.UNKNOWN, {}
        
        msg_type = MessageType(frame.payload[0])
        payload_data = frame.payload[1:]
        
        decoded = self.encoder.decode(payload_data)
        
        return msg_type, decoded
    
    def create_stream(self, stream_id: int = 0, chunk_size: int = 1024) -> BinaryStream:
        """Create new stream"""
        stream = BinaryStream(stream_id, chunk_size)
        self.streams[stream_id] = stream
        return stream
    
    def encode_request(self, data: Dict[str, Any]) -> bytes:
        """Encode request body to binary"""
        return self.encode_message(data, MessageType.UNKNOWN)
    
    def decode_request(self, data: bytes) -> Dict[str, Any]:
        """Decode binary request body"""
        _, payload = self.decode_message(data)
        return payload
    
    def create_error_frame(self, code: int, message: str) -> bytes:
        """Create error frame"""
        return self.encode_message(
            {"code": code, "message": message},
            MessageType.ERROR
        )


# ============ CLI TOOLS ============

def read_clsn_file(path: str) -> Dict[str, Any]:
    """Read and parse .clsn binary file"""
    with open(path, 'rb') as f:
        data = f.read()
    
    protocol = KloudProtocol()
    msg_type, payload = protocol.decode_message(data)
    
    return {
        "file": path,
        "size": len(data),
        "message_type": msg_type.name,
        "payload": payload
    }


def write_clsn_file(path: str, data: Dict[str, Any], msg_type: MessageType = MessageType.UNKNOWN):
    """Write data to .clsn binary file"""
    protocol = KloudProtocol()
    binary = protocol.encode_message(data, msg_type)
    
    with open(path, 'wb') as f:
        f.write(binary)
    
    return len(binary)


def dump_frame(data: bytes) -> Dict[str, Any]:
    """Dump frame structure for debugging"""
    if len(data) < HEADER_SIZE:
        return {"error": "Too short"}
    
    magic = data[0:4]
    version = data[4]
    flags = FrameFlags(data[5])
    payload_len = struct.unpack('>H', data[6:8])[0]
    
    flag_names = []
    for f in FrameFlags:
        if f in flags and f != FrameFlags.NONE:
            flag_names.append(f.name)
    
    result = {
        "magic": magic.decode('ascii', errors='replace'),
        "magic_hex": magic.hex(),
        "version": version,
        "flags": int(flags),
        "flags_names": flag_names,
        "payload_length": payload_len,
        "total_size": len(data)
    }
    
    if len(data) > HEADER_SIZE:
        payload = data[HEADER_SIZE:HEADER_SIZE+payload_len]
        result["payload_hex"] = payload[:64].hex()
        if len(payload) > 1:
            result["message_type"] = MessageType(payload[0]).name
    
    return result


# ============ GLOBAL ============

_protocol: Optional[KloudProtocol] = None
_schema_dir = os.path.join(os.path.dirname(__file__), 'schemas')


def get_protocol() -> KloudProtocol:
    """Get global protocol instance"""
    global _protocol
    if _protocol is None:
        _protocol = KloudProtocol(_schema_dir)
    return _protocol


def get_schema_registry() -> SchemaRegistry:
    """Get schema registry"""
    return get_protocol().registry

