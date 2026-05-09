# -*- coding: utf-8 -*-
"""
🔷 KLOUD BINARY MESSAGE SYSTEM
==================================
Full binary message encoding/decoding - NO JSON for messages.
Uses CBOR2 as primary format, MessagePack as fallback.

Message Format:
┌──────────┬─────────┬───────────┬────────────┬─────────────┐
│ Magic(4) │ Ver(1)  │ Type(1)   │ Len(4)     │ Payload(N)  │
│ "CMSG"   │ 0x01    │ MsgType   │ uint32 BE  │ CBOR2       │
└──────────┴─────────┴───────────┴────────────┴─────────────┘

Optional Checksum (if HAS_CHECKSUM flag set):
┌─────────────┬──────────┐
│ Payload     │ CRC32(4) │
└─────────────┴──────────┘

Author: Kloud Team
"""

import struct
import zlib
import io
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import IntEnum, IntFlag
from datetime import datetime

# Binary libraries
try:
    import cbor2
    HAS_CBOR2 = True
except ImportError:
    HAS_CBOR2 = False

try:
    import msgpack
    HAS_MSGPACK = True
except ImportError:
    HAS_MSGPACK = False


# ============ CONSTANTS ============

MAGIC_CMSG = b'CMSG'  # Kloud Message
MAGIC_CBIN = b'CBIN'  # Kloud Binary
MSG_VERSION = 1
MSG_HEADER_SIZE = 10  # magic(4) + version(1) + type(1) + len(4)


class MsgType(IntEnum):
    """Message types"""
    UNKNOWN = 0x00
    REQUEST = 0x01
    RESPONSE = 0x02
    ERROR = 0x03
    STREAM_START = 0x10
    STREAM_DATA = 0x11
    STREAM_END = 0x12
    SIGNAL = 0x20
    SIGNAL_BATCH = 0x21
    CHAT_QUERY = 0x30
    CHAT_RESPONSE = 0x31
    ALGEBRA_EXPR = 0x40
    ALGEBRA_RESULT = 0x41
    LEARN_DATA = 0x50
    LEARN_ACK = 0x51
    PING = 0xFE
    PONG = 0xFF


class MsgFlags(IntFlag):
    """Message flags (in reserved byte)"""
    NONE = 0x00
    COMPRESSED = 0x01
    ENCRYPTED = 0x02
    HAS_CHECKSUM = 0x04
    CHUNKED = 0x08
    LAST_CHUNK = 0x10


# ============ CBOR ENCODER ============

class CborEncoder:
    """
    Pure-Python CBOR encoder - NO JSON dependency.
    Implements RFC 8949 subset for Kloud messages.
    """
    
    @staticmethod
    def encode(value: Any) -> bytes:
        """Encode any Python value to CBOR binary"""
        if HAS_CBOR2:
            return cbor2.dumps(value)
        return CborEncoder._encode_fallback(value)
    
    @staticmethod
    def decode(data: bytes) -> Any:
        """Decode CBOR binary to Python value"""
        if HAS_CBOR2:
            return cbor2.loads(data)
        return CborEncoder._decode_fallback(data)
    
    @staticmethod
    def _encode_fallback(value: Any) -> bytes:
        """Fallback CBOR encoding without library"""
        buffer = io.BytesIO()
        CborEncoder._write_value(buffer, value)
        return buffer.getvalue()
    
    @staticmethod
    def _write_value(buf: io.BytesIO, value: Any):
        """Write a value in CBOR format"""
        if value is None:
            buf.write(b'\xf6')  # null
        elif isinstance(value, bool):
            buf.write(b'\xf5' if value else b'\xf4')
        elif isinstance(value, int):
            CborEncoder._write_int(buf, value)
        elif isinstance(value, float):
            buf.write(b'\xfb')
            buf.write(struct.pack('>d', value))
        elif isinstance(value, str):
            encoded = value.encode('utf-8')
            CborEncoder._write_type_len(buf, 3, len(encoded))  # Major type 3: text string
            buf.write(encoded)
        elif isinstance(value, bytes):
            CborEncoder._write_type_len(buf, 2, len(value))  # Major type 2: byte string
            buf.write(value)
        elif isinstance(value, (list, tuple)):
            CborEncoder._write_type_len(buf, 4, len(value))  # Major type 4: array
            for item in value:
                CborEncoder._write_value(buf, item)
        elif isinstance(value, dict):
            CborEncoder._write_type_len(buf, 5, len(value))  # Major type 5: map
            for k, v in value.items():
                CborEncoder._write_value(buf, str(k))
                CborEncoder._write_value(buf, v)
        elif isinstance(value, datetime):
            # Tag 0: Standard date/time string
            buf.write(b'\xc0')
            CborEncoder._write_value(buf, value.isoformat())
        else:
            CborEncoder._write_value(buf, str(value))
    
    @staticmethod
    def _write_int(buf: io.BytesIO, value: int):
        """Write integer in CBOR format"""
        if value >= 0:
            CborEncoder._write_type_len(buf, 0, value)  # Major type 0: positive int
        else:
            CborEncoder._write_type_len(buf, 1, -1 - value)  # Major type 1: negative int
    
    @staticmethod
    def _write_type_len(buf: io.BytesIO, major_type: int, length: int):
        """Write CBOR type and length"""
        if length <= 23:
            buf.write(bytes([major_type << 5 | length]))
        elif length <= 0xFF:
            buf.write(bytes([major_type << 5 | 24]))
            buf.write(struct.pack('B', length))
        elif length <= 0xFFFF:
            buf.write(bytes([major_type << 5 | 25]))
            buf.write(struct.pack('>H', length))
        elif length <= 0xFFFFFFFF:
            buf.write(bytes([major_type << 5 | 26]))
            buf.write(struct.pack('>I', length))
        else:
            buf.write(bytes([major_type << 5 | 27]))
            buf.write(struct.pack('>Q', length))
    
    @staticmethod
    def _decode_fallback(data: bytes) -> Any:
        """Fallback CBOR decoding without library"""
        buf = io.BytesIO(data)
        return CborEncoder._read_value(buf)
    
    @staticmethod
    def _read_value(buf: io.BytesIO) -> Any:
        """Read a CBOR value"""
        byte = buf.read(1)
        if not byte:
            return None
        
        b = byte[0]
        major_type = b >> 5
        additional = b & 0x1f
        
        # Simple values
        if b == 0xf4:
            return False
        elif b == 0xf5:
            return True
        elif b == 0xf6:
            return None
        elif b == 0xfb:
            return struct.unpack('>d', buf.read(8))[0]
        
        # Get length
        length = CborEncoder._read_length(buf, additional)
        
        # Decode based on major type
        if major_type == 0:  # Positive integer
            return length
        elif major_type == 1:  # Negative integer
            return -1 - length
        elif major_type == 2:  # Byte string
            return buf.read(length)
        elif major_type == 3:  # Text string
            return buf.read(length).decode('utf-8')
        elif major_type == 4:  # Array
            return [CborEncoder._read_value(buf) for _ in range(length)]
        elif major_type == 5:  # Map
            result = {}
            for _ in range(length):
                key = CborEncoder._read_value(buf)
                val = CborEncoder._read_value(buf)
                result[key] = val
            return result
        elif major_type == 6:  # Tag
            return CborEncoder._read_value(buf)  # Just return tagged value
        
        return None
    
    @staticmethod
    def _read_length(buf: io.BytesIO, additional: int) -> int:
        """Read CBOR length from additional info"""
        if additional <= 23:
            return additional
        elif additional == 24:
            return struct.unpack('B', buf.read(1))[0]
        elif additional == 25:
            return struct.unpack('>H', buf.read(2))[0]
        elif additional == 26:
            return struct.unpack('>I', buf.read(4))[0]
        elif additional == 27:
            return struct.unpack('>Q', buf.read(8))[0]
        return 0


# ============ MESSAGE CLASS ============

@dataclass
class BinaryMessage:
    """
    Binary message container - NO JSON.
    All payloads encoded in CBOR2.
    """
    msg_type: MsgType
    payload: Dict[str, Any]
    flags: MsgFlags = MsgFlags.NONE
    version: int = MSG_VERSION
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_bytes(self) -> bytes:
        """Serialize message to binary"""
        # Encode payload with CBOR2
        payload_bytes = CborEncoder.encode(self.payload)
        
        # Compress if requested
        if self.flags & MsgFlags.COMPRESSED:
            payload_bytes = zlib.compress(payload_bytes, level=6)
        
        # Build header
        header = struct.pack(
            '>4sBBBI',
            MAGIC_CMSG,
            self.version,
            self.msg_type,
            self.flags,
            len(payload_bytes)
        )
        
        result = header + payload_bytes
        
        # Add checksum if requested
        if self.flags & MsgFlags.HAS_CHECKSUM:
            crc = zlib.crc32(payload_bytes) & 0xFFFFFFFF
            result += struct.pack('>I', crc)
        
        return result
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'BinaryMessage':
        """Deserialize message from binary"""
        if len(data) < MSG_HEADER_SIZE + 1:
            raise ValueError(f"Message too short: {len(data)} bytes")
        
        # Parse header
        magic, version, msg_type, flags, payload_len = struct.unpack(
            '>4sBBBI', data[:MSG_HEADER_SIZE + 1]
        )
        
        if magic != MAGIC_CMSG:
            raise ValueError(f"Invalid magic: {magic}")
        
        # Extract payload
        payload_start = MSG_HEADER_SIZE + 1
        payload_end = payload_start + payload_len
        payload_bytes = data[payload_start:payload_end]
        
        # Verify checksum if present
        flags_enum = MsgFlags(flags)
        if flags_enum & MsgFlags.HAS_CHECKSUM:
            expected_crc = struct.unpack('>I', data[payload_end:payload_end + 4])[0]
            actual_crc = zlib.crc32(payload_bytes) & 0xFFFFFFFF
            if expected_crc != actual_crc:
                raise ValueError(f"Checksum mismatch: {expected_crc} != {actual_crc}")
        
        # Decompress if compressed
        if flags_enum & MsgFlags.COMPRESSED:
            payload_bytes = zlib.decompress(payload_bytes)
        
        # Decode payload with CBOR2
        payload = CborEncoder.decode(payload_bytes)
        
        return cls(
            msg_type=MsgType(msg_type),
            payload=payload,
            flags=flags_enum,
            version=version
        )


# ============ SPECIALIZED MESSAGES ============

@dataclass
class ChatMessage(BinaryMessage):
    """Chat query/response message - binary only"""
    
    @classmethod
    def query(cls, text: str, context: Optional[Dict] = None) -> 'ChatMessage':
        """Create chat query message"""
        return cls(
            msg_type=MsgType.CHAT_QUERY,
            payload={
                'query': text,
                'context': context or {},
                'ts': datetime.now().timestamp()
            }
        )
    
    @classmethod
    def response(cls, answer: str, source: str, confidence: float) -> 'ChatMessage':
        """Create chat response message"""
        return cls(
            msg_type=MsgType.CHAT_RESPONSE,
            payload={
                'answer': answer,
                'source': source,
                'confidence': confidence,
                'ts': datetime.now().timestamp()
            }
        )


@dataclass
class AlgebraMessage(BinaryMessage):
    """Algebra expression/result message - binary only"""
    
    @classmethod
    def expression(cls, expr: str, variables: Optional[Dict[str, float]] = None) -> 'AlgebraMessage':
        """Create algebra expression message"""
        return cls(
            msg_type=MsgType.ALGEBRA_EXPR,
            payload={
                'expression': expr,
                'variables': variables or {},
                'ts': datetime.now().timestamp()
            }
        )
    
    @classmethod
    def result(cls, expr: str, result: float, steps: Optional[List[str]] = None) -> 'AlgebraMessage':
        """Create algebra result message"""
        return cls(
            msg_type=MsgType.ALGEBRA_RESULT,
            payload={
                'expression': expr,
                'result': result,
                'steps': steps or [],
                'ts': datetime.now().timestamp()
            }
        )


@dataclass
class SignalMessage(BinaryMessage):
    """Signal message - binary only"""
    
    @classmethod
    def single(cls, signal_id: int, value: Any, source: str) -> 'SignalMessage':
        """Create single signal message"""
        return cls(
            msg_type=MsgType.SIGNAL,
            payload={
                'id': signal_id,
                'value': value,
                'source': source,
                'ts': datetime.now().timestamp()
            }
        )
    
    @classmethod
    def batch(cls, signals: List[Dict]) -> 'SignalMessage':
        """Create batch signal message"""
        return cls(
            msg_type=MsgType.SIGNAL_BATCH,
            payload={
                'signals': signals,
                'count': len(signals),
                'ts': datetime.now().timestamp()
            },
            flags=MsgFlags.COMPRESSED  # Compress batches
        )


# ============ MESSAGE FACTORY ============

class MessageFactory:
    """Factory for creating binary messages"""
    
    @staticmethod
    def request(action: str, data: Dict[str, Any]) -> BinaryMessage:
        """Create request message"""
        return BinaryMessage(
            msg_type=MsgType.REQUEST,
            payload={
                'action': action,
                'data': data,
                'ts': datetime.now().timestamp()
            }
        )
    
    @staticmethod
    def response(success: bool, data: Any, error: Optional[str] = None) -> BinaryMessage:
        """Create response message"""
        return BinaryMessage(
            msg_type=MsgType.RESPONSE if success else MsgType.ERROR,
            payload={
                'success': success,
                'data': data,
                'error': error,
                'ts': datetime.now().timestamp()
            }
        )
    
    @staticmethod
    def error(code: int, message: str) -> BinaryMessage:
        """Create error message"""
        return BinaryMessage(
            msg_type=MsgType.ERROR,
            payload={
                'code': code,
                'message': message,
                'ts': datetime.now().timestamp()
            }
        )
    
    @staticmethod
    def ping() -> BinaryMessage:
        """Create ping message"""
        return BinaryMessage(
            msg_type=MsgType.PING,
            payload={'ts': datetime.now().timestamp()}
        )
    
    @staticmethod
    def pong(ping_ts: float) -> BinaryMessage:
        """Create pong message"""
        now = datetime.now().timestamp()
        return BinaryMessage(
            msg_type=MsgType.PONG,
            payload={
                'ts': now,
                'ping_ts': ping_ts,
                'latency_ms': (now - ping_ts) * 1000
            }
        )


# ============ BINARY STREAM ============

class BinaryStream:
    """Binary message stream handler"""
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.messages: List[BinaryMessage] = []
    
    def write(self, msg: BinaryMessage) -> int:
        """Write message to stream"""
        data = msg.to_bytes()
        self.buffer.write(data)
        self.messages.append(msg)
        return len(data)
    
    def read_all(self) -> List[BinaryMessage]:
        """Read all messages from buffer"""
        self.buffer.seek(0)
        messages = []
        while True:
            pos = self.buffer.tell()
            data = self.buffer.read(MSG_HEADER_SIZE + 1)
            if len(data) < MSG_HEADER_SIZE + 1:
                break
            
            # Parse header to get payload length
            _, _, _, _, payload_len = struct.unpack('>4sBBBI', data)
            
            # Read rest of message
            self.buffer.seek(pos)
            full_msg = self.buffer.read(MSG_HEADER_SIZE + 1 + payload_len + 4)  # +4 for possible checksum
            
            try:
                msg = BinaryMessage.from_bytes(full_msg)
                messages.append(msg)
            except ValueError:
                break
        
        return messages
    
    def get_bytes(self) -> bytes:
        """Get all bytes from buffer"""
        self.buffer.seek(0)
        return self.buffer.read()
    
    def clear(self):
        """Clear buffer"""
        self.buffer = io.BytesIO()
        self.messages.clear()


# ============ UTILITY FUNCTIONS ============

def encode_message(msg_type: MsgType, payload: Dict[str, Any], 
                   compress: bool = False, checksum: bool = True) -> bytes:
    """Quick encode a message to binary"""
    flags = MsgFlags.NONE
    if compress:
        flags |= MsgFlags.COMPRESSED
    if checksum:
        flags |= MsgFlags.HAS_CHECKSUM
    
    msg = BinaryMessage(
        msg_type=msg_type,
        payload=payload,
        flags=flags
    )
    return msg.to_bytes()


def decode_message(data: bytes) -> Tuple[MsgType, Dict[str, Any]]:
    """Quick decode a message from binary"""
    msg = BinaryMessage.from_bytes(data)
    return msg.msg_type, msg.payload


def cbor_encode(value: Any) -> bytes:
    """Encode value to CBOR binary"""
    return CborEncoder.encode(value)


def cbor_decode(data: bytes) -> Any:
    """Decode CBOR binary to value"""
    return CborEncoder.decode(data)


# ============ STATISTICS ============

def get_binary_stats() -> Dict[str, Any]:
    """Get binary message system statistics"""
    return {
        'format': 'CBOR2',
        'has_cbor2_lib': HAS_CBOR2,
        'has_msgpack_lib': HAS_MSGPACK,
        'msg_version': MSG_VERSION,
        'header_size': MSG_HEADER_SIZE,
        'magic': MAGIC_CMSG.decode('ascii'),
        'msg_types': {t.name: t.value for t in MsgType},
        'flags': {f.name: f.value for f in MsgFlags if f.value > 0}
    }


# ============ TEST ============

def _test_binary_messages():
    """Test binary message encoding/decoding"""
    print("🔷 Testing Binary Message System...")
    
    # Test basic message
    msg = MessageFactory.request('calculate', {'expr': '5+3'})
    data = msg.to_bytes()
    decoded = BinaryMessage.from_bytes(data)
    assert decoded.payload['data']['expr'] == '5+3'
    print(f"  ✅ Basic message: {len(data)} bytes")
    
    # Test chat message
    chat = ChatMessage.query("What is AI?")
    data = chat.to_bytes()
    decoded = BinaryMessage.from_bytes(data)
    assert decoded.payload['query'] == "What is AI?"
    print(f"  ✅ Chat message: {len(data)} bytes")
    
    # Test algebra message
    algebra = AlgebraMessage.expression("x^2 + 5", {'x': 3})
    data = algebra.to_bytes()
    decoded = BinaryMessage.from_bytes(data)
    assert decoded.payload['variables']['x'] == 3
    print(f"  ✅ Algebra message: {len(data)} bytes")
    
    # Test compressed message
    signals = SignalMessage.batch([{'id': i, 'val': i*2} for i in range(100)])
    data = signals.to_bytes()
    print(f"  ✅ Compressed batch: {len(data)} bytes (100 signals)")
    
    # Test stream
    stream = BinaryStream()
    stream.write(MessageFactory.ping())
    stream.write(ChatMessage.query("Hello"))
    stream.write(AlgebraMessage.expression("2+2"))
    all_bytes = stream.get_bytes()
    print(f"  ✅ Stream: {len(all_bytes)} bytes (3 messages)")
    
    print(f"\n📊 Binary System Stats:")
    for k, v in get_binary_stats().items():
        print(f"    {k}: {v}")
    
    print("\n✅ All tests passed - NO JSON!")


if __name__ == '__main__':
    _test_binary_messages()

