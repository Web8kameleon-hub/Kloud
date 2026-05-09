"""
Binary Protocols Module - CBOR2, MessagePack - ONLY REAL BINARY
Kloud Cloud - Full Binary Support - NO FALLBACKS
"""

import struct
import zlib
import hashlib
import base64
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from datetime import datetime
import io

# REQUIRED: Binary serialization libraries - NO FALLBACK
import cbor2
import msgpack


class BinaryFormat(IntEnum):
    """Supported binary formats - CBOR2 is default (0)"""
    CBOR2 = 0
    MSGPACK = 1
    CUSTOM_BINARY = 2
    COMPRESSED_CBOR = 3


class DataType(IntEnum):
    """Data types for custom binary protocol"""
    NULL = 0
    BOOL = 1
    INT8 = 2
    INT16 = 3
    INT32 = 4
    INT64 = 5
    FLOAT32 = 6
    FLOAT64 = 7
    STRING = 8
    BYTES = 9
    ARRAY = 10
    MAP = 11
    TIMESTAMP = 12
    SIGNAL = 13
    ALGEBRA = 14
    EXPRESSION = 15


@dataclass
class BinaryMessage:
    """Binary message container"""
    format: BinaryFormat
    version: int = 1
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    checksum: str = ""
    compressed: bool = False
    payload: bytes = b""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_bytes(self) -> bytes:
        """Serialize message to bytes"""
        header = struct.pack(
            '>BBIQB',  # Big-endian: format, version, timestamp(double as int), compressed
            self.format,
            self.version,
            int(self.timestamp * 1000000),  # Microseconds
            len(self.payload),
            1 if self.compressed else 0
        )
        return header + self.payload
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'BinaryMessage':
        """Deserialize message from bytes"""
        header_size = struct.calcsize('>BBIQB')
        format_id, version, ts_micro, payload_len, compressed = struct.unpack(
            '>BBIQB', data[:header_size]
        )
        payload = data[header_size:header_size + payload_len]
        return cls(
            format=BinaryFormat(format_id),
            version=version,
            timestamp=ts_micro / 1000000,
            compressed=bool(compressed),
            payload=payload
        )


@dataclass 
class SignalPacket:
    """Binary signal packet for streaming"""
    signal_id: int
    signal_type: int
    source_hash: int
    value_type: DataType
    value: Any
    timestamp: float
    parent_id: int = 0
    children_count: int = 0
    
    def to_bytes(self) -> bytes:
        """Pack signal to binary"""
        # Header: id(4), type(2), source(4), value_type(1), parent(4), children(2), timestamp(8)
        header = struct.pack(
            '>IHIHIBQ',
            self.signal_id,
            self.signal_type,
            self.source_hash,
            self.value_type,
            self.parent_id,
            self.children_count,
            int(self.timestamp * 1000000)
        )
        
        # Value encoding based on type
        value_bytes = self._encode_value()
        value_len = struct.pack('>I', len(value_bytes))
        
        return header + value_len + value_bytes
    
    def _encode_value(self) -> bytes:
        """Encode value based on type"""
        if self.value_type == DataType.NULL:
            return b''
        elif self.value_type == DataType.BOOL:
            return struct.pack('B', 1 if self.value else 0)
        elif self.value_type == DataType.INT32:
            return struct.pack('>i', self.value)
        elif self.value_type == DataType.INT64:
            return struct.pack('>q', self.value)
        elif self.value_type == DataType.FLOAT64:
            return struct.pack('>d', self.value)
        elif self.value_type == DataType.STRING:
            encoded = self.value.encode('utf-8')
            return struct.pack('>I', len(encoded)) + encoded
        elif self.value_type == DataType.BYTES:
            return struct.pack('>I', len(self.value)) + self.value
        elif self.value_type in (DataType.ARRAY, DataType.MAP):
            # CBOR2 ONLY - no fallback
            binary_data = cbor2.dumps(self.value)
            return struct.pack('>I', len(binary_data)) + binary_data
        else:
            # Default: CBOR2 encode
            binary_data = cbor2.dumps(self.value)
            return struct.pack('>I', len(binary_data)) + binary_data


@dataclass
class AlgebraPacket:
    """Binary algebra expression packet"""
    expression_id: int
    operator: int  # 0=add, 1=sub, 2=mul, 3=div, 4=pow, 5=mod, 6=eq
    operand_a: float
    operand_b: float
    result: float
    variables: Dict[str, float] = field(default_factory=dict)
    
    OPERATORS = {
        '+': 0, '-': 1, '*': 2, '/': 3, '^': 4, '%': 5, '=': 6,
        'add': 0, 'sub': 1, 'mul': 2, 'div': 3, 'pow': 4, 'mod': 5, 'eq': 6
    }
    
    def to_bytes(self) -> bytes:
        """Pack algebra expression to binary"""
        # Fixed part: id(4), op(1), a(8), b(8), result(8)
        header = struct.pack(
            '>IBddd',
            self.expression_id,
            self.operator,
            self.operand_a,
            self.operand_b,
            self.result
        )
        
        # Variable part: count(2), then name_len(2)+name+value(8) for each
        var_count = len(self.variables)
        var_bytes = struct.pack('>H', var_count)
        for name, value in self.variables.items():
            name_encoded = name.encode('utf-8')
            var_bytes += struct.pack('>H', len(name_encoded))
            var_bytes += name_encoded
            var_bytes += struct.pack('>d', value)
        
        return header + var_bytes
    
    @classmethod
    def from_expression(cls, expr: str, expr_id: int = 0) -> 'AlgebraPacket':
        """Create packet from expression string like '5+3' or 'x=5'"""
        import re
        
        # Find operator
        for op_char, op_code in cls.OPERATORS.items():
            if len(op_char) == 1 and op_char in expr:
                parts = expr.split(op_char, 1)
                if len(parts) == 2:
                    try:
                        a = float(parts[0].strip())
                        b = float(parts[1].strip())
                        
                        # Calculate result
                        if op_code == 0:  # add
                            result = a + b
                        elif op_code == 1:  # sub
                            result = a - b
                        elif op_code == 2:  # mul
                            result = a * b
                        elif op_code == 3:  # div
                            result = a / b if b != 0 else float('inf')
                        elif op_code == 4:  # pow
                            result = a ** b
                        elif op_code == 5:  # mod
                            result = a % b if b != 0 else 0
                        else:
                            result = a
                        
                        return cls(
                            expression_id=expr_id,
                            operator=op_code,
                            operand_a=a,
                            operand_b=b,
                            result=result
                        )
                    except ValueError:
                        pass
        
        # If parsing failed, return empty
        return cls(expression_id=expr_id, operator=6, operand_a=0, operand_b=0, result=0)


class BinaryBuffer:
    """Streaming binary buffer for real-time data"""
    
    def __init__(self, capacity: int = 1024 * 1024):  # 1MB default
        self.capacity = capacity
        self.buffer = io.BytesIO()
        self.read_position = 0
        self.write_position = 0
        self.packet_count = 0
    
    def write(self, data: bytes) -> int:
        """Write data to buffer, returns bytes written"""
        self.buffer.seek(self.write_position)
        written = self.buffer.write(data)
        self.write_position += written
        return written
    
    def write_packet(self, packet: Union[SignalPacket, AlgebraPacket, BinaryMessage]) -> int:
        """Write a packet to buffer"""
        data = packet.to_bytes()
        # Prefix with length
        length_prefix = struct.pack('>I', len(data))
        self.write(length_prefix + data)
        self.packet_count += 1
        return len(data) + 4
    
    def read(self, size: int) -> bytes:
        """Read data from buffer"""
        self.buffer.seek(self.read_position)
        data = self.buffer.read(size)
        self.read_position += len(data)
        return data
    
    def read_packet(self) -> Optional[bytes]:
        """Read next packet from buffer"""
        if self.read_position >= self.write_position:
            return None
        
        self.buffer.seek(self.read_position)
        length_bytes = self.buffer.read(4)
        if len(length_bytes) < 4:
            return None
        
        length = struct.unpack('>I', length_bytes)[0]
        data = self.buffer.read(length)
        if len(data) < length:
            return None
        
        self.read_position += 4 + length
        return data
    
    def available(self) -> int:
        """Bytes available to read"""
        return self.write_position - self.read_position
    
    def reset(self):
        """Reset buffer"""
        self.buffer = io.BytesIO()
        self.read_position = 0
        self.write_position = 0
        self.packet_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics"""
        return {
            "capacity": self.capacity,
            "write_position": self.write_position,
            "read_position": self.read_position,
            "available_bytes": self.available(),
            "packet_count": self.packet_count,
            "utilization": self.write_position / self.capacity if self.capacity > 0 else 0
        }


class BinaryEncoder:
    """Universal binary encoder supporting multiple formats"""
    
    def __init__(self, default_format: BinaryFormat = BinaryFormat.CUSTOM_BINARY):
        self.default_format = default_format
        self.stats = {
            "encoded_count": 0,
            "decoded_count": 0,
            "bytes_encoded": 0,
            "bytes_decoded": 0
        }
    
    def encode(self, data: Any, format: Optional[BinaryFormat] = None) -> bytes:
        """Encode data to binary format - REAL ONLY"""
        fmt = format or self.default_format
        
        if fmt == BinaryFormat.CBOR2:
            result = cbor2.dumps(data)
        
        elif fmt == BinaryFormat.MSGPACK:
            result = msgpack.packb(data, use_bin_type=True)
        
        elif fmt == BinaryFormat.CUSTOM_BINARY:
            result = self._encode_custom(data)
        
        elif fmt == BinaryFormat.COMPRESSED_CBOR:
            cbor_bytes = cbor2.dumps(data)
            result = zlib.compress(cbor_bytes, level=6)
        
        else:
            # Default: CBOR2
            result = cbor2.dumps(data)
        
        self.stats["encoded_count"] += 1
        self.stats["bytes_encoded"] += len(result)
        return result
    
    def decode(self, data: bytes, format: Optional[BinaryFormat] = None) -> Any:
        """Decode data from binary format - REAL ONLY"""
        fmt = format or self.default_format
        
        if fmt == BinaryFormat.CBOR2:
            result = cbor2.loads(data)
        
        elif fmt == BinaryFormat.MSGPACK:
            result = msgpack.unpackb(data, raw=False)
        
        elif fmt == BinaryFormat.CUSTOM_BINARY:
            result = self._decode_custom(data)
        
        elif fmt == BinaryFormat.COMPRESSED_CBOR:
            cbor_bytes = zlib.decompress(data)
            result = cbor2.loads(cbor_bytes)
        
        else:
            # Default: CBOR2
            result = cbor2.loads(data)
        
        self.stats["decoded_count"] += 1
        self.stats["bytes_decoded"] += len(data)
        return result
    
    def _encode_custom(self, data: Any) -> bytes:
        """Custom binary encoding optimized for Kloud"""
        buffer = io.BytesIO()
        
        # Magic header
        buffer.write(b'CLSN')  # Kloud magic
        buffer.write(struct.pack('>B', 1))  # Version
        
        # Encode data
        self._write_custom_value(buffer, data)
        
        # Checksum
        content = buffer.getvalue()
        checksum = zlib.crc32(content) & 0xffffffff
        buffer.write(struct.pack('>I', checksum))
        
        return buffer.getvalue()
    
    def _write_custom_value(self, buffer: io.BytesIO, value: Any):
        """Write custom binary value"""
        if value is None:
            buffer.write(struct.pack('>B', DataType.NULL))
        elif isinstance(value, bool):
            buffer.write(struct.pack('>BB', DataType.BOOL, 1 if value else 0))
        elif isinstance(value, int):
            if -128 <= value <= 127:
                buffer.write(struct.pack('>Bb', DataType.INT8, value))
            elif -32768 <= value <= 32767:
                buffer.write(struct.pack('>Bh', DataType.INT16, value))
            elif -2147483648 <= value <= 2147483647:
                buffer.write(struct.pack('>Bi', DataType.INT32, value))
            else:
                buffer.write(struct.pack('>Bq', DataType.INT64, value))
        elif isinstance(value, float):
            buffer.write(struct.pack('>Bd', DataType.FLOAT64, value))
        elif isinstance(value, str):
            encoded = value.encode('utf-8')
            buffer.write(struct.pack('>BI', DataType.STRING, len(encoded)))
            buffer.write(encoded)
        elif isinstance(value, bytes):
            buffer.write(struct.pack('>BI', DataType.BYTES, len(value)))
            buffer.write(value)
        elif isinstance(value, (list, tuple)):
            buffer.write(struct.pack('>BI', DataType.ARRAY, len(value)))
            for item in value:
                self._write_custom_value(buffer, item)
        elif isinstance(value, dict):
            buffer.write(struct.pack('>BI', DataType.MAP, len(value)))
            for k, v in value.items():
                self._write_custom_value(buffer, str(k))
                self._write_custom_value(buffer, v)
        else:
            self._write_custom_value(buffer, str(value))
    
    def _decode_custom(self, data: bytes) -> Any:
        """Decode custom binary format"""
        buffer = io.BytesIO(data)
        
        # Verify magic
        magic = buffer.read(4)
        if magic != b'CLSN':
            raise ValueError("Invalid Kloud binary format")
        
        version = struct.unpack('>B', buffer.read(1))[0]
        if version != 1:
            raise ValueError(f"Unsupported version: {version}")
        
        return self._read_custom_value(buffer)
    
    def _read_custom_value(self, buffer: io.BytesIO) -> Any:
        """Read custom binary value"""
        type_byte = buffer.read(1)
        if not type_byte:
            return None
        
        data_type = struct.unpack('>B', type_byte)[0]
        
        if data_type == DataType.NULL:
            return None
        elif data_type == DataType.BOOL:
            return struct.unpack('>B', buffer.read(1))[0] == 1
        elif data_type == DataType.INT8:
            return struct.unpack('>b', buffer.read(1))[0]
        elif data_type == DataType.INT16:
            return struct.unpack('>h', buffer.read(2))[0]
        elif data_type == DataType.INT32:
            return struct.unpack('>i', buffer.read(4))[0]
        elif data_type == DataType.INT64:
            return struct.unpack('>q', buffer.read(8))[0]
        elif data_type == DataType.FLOAT32:
            return struct.unpack('>f', buffer.read(4))[0]
        elif data_type == DataType.FLOAT64:
            return struct.unpack('>d', buffer.read(8))[0]
        elif data_type == DataType.STRING:
            length = struct.unpack('>I', buffer.read(4))[0]
            return buffer.read(length).decode('utf-8')
        elif data_type == DataType.BYTES:
            length = struct.unpack('>I', buffer.read(4))[0]
            return buffer.read(length)
        elif data_type == DataType.ARRAY:
            length = struct.unpack('>I', buffer.read(4))[0]
            return [self._read_custom_value(buffer) for _ in range(length)]
        elif data_type == DataType.MAP:
            length = struct.unpack('>I', buffer.read(4))[0]
            return {self._read_custom_value(buffer): self._read_custom_value(buffer) for _ in range(length)}
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get encoder statistics"""
        return {
            **self.stats,
            "cbor2": True,
            "msgpack": True,
            "default_format": self.default_format.name,
            "compression_ratio": (
                self.stats["bytes_decoded"] / self.stats["bytes_encoded"]
                if self.stats["bytes_encoded"] > 0 else 0
            )
        }


class SmartCalculator:
    """Smart calculator that understands natural language and expressions"""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        self.variables: Dict[str, float] = {}
        self.encoder = BinaryEncoder(BinaryFormat.CUSTOM_BINARY)
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Calculate expression and return result"""
        import re
        import math
        
        # Clean expression
        expr = expression.strip()
        
        # Check for natural language patterns
        patterns = [
            # Albanian patterns
            (r'sa\s+b[eë]jn[eë]\s+(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) + float(m.group(2)), '+'),
            (r'sa\s+b[eë]jn[eë]\s+(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) - float(m.group(2)), '-'),
            (r'sa\s+b[eë]jn[eë]\s+(\d+(?:\.\d+)?)\s*[x*×]\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) * float(m.group(2)), '*'),
            (r'sa\s+b[eë]jn[eë]\s+(\d+(?:\.\d+)?)\s*[:/÷]\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) / float(m.group(2)) if float(m.group(2)) != 0 else float('inf'), '/'),
            
            # English patterns
            (r'what\s+is\s+(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) + float(m.group(2)), '+'),
            (r'what\s+is\s+(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) - float(m.group(2)), '-'),
            (r'what\s+is\s+(\d+(?:\.\d+)?)\s*[x*×]\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) * float(m.group(2)), '*'),
            (r'what\s+is\s+(\d+(?:\.\d+)?)\s*[:/÷]\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) / float(m.group(2)) if float(m.group(2)) != 0 else float('inf'), '/'),
            
            # Calculate patterns
            (r'calculate\s+(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) + float(m.group(2)), '+'),
            (r'llogarit\s+(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', lambda m: float(m.group(1)) + float(m.group(2)), '+'),
        ]
        
        # Try natural language patterns
        for pattern, calc_func, op in patterns:
            match = re.search(pattern, expr.lower())
            if match:
                result = calc_func(match)
                return self._create_result(expr, result, op, match.groups())
        
        # Try direct expression parsing
        result = self._parse_expression(expr)
        if result is not None:
            return result
        
        # Try eval with safe environment
        try:
            safe_dict = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'sqrt': math.sqrt,
                'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
                'log': math.log, 'log10': math.log10, 'exp': math.exp,
                'pi': math.pi, 'e': math.e,
                **self.variables
            }
            
            # Extract just the math part
            math_expr = re.sub(r'[^\d\+\-\*/\^\(\)\.\s]', '', expr)
            math_expr = math_expr.replace('^', '**')
            
            if math_expr.strip():
                calc_result = eval(math_expr, {"__builtins__": {}}, safe_dict)
                return self._create_result(expr, calc_result, 'eval', [math_expr])
        except:
            pass
        
        return {
            "success": False,
            "expression": expr,
            "error": "Could not parse expression",
            "hint": "Try: '5+3' or 'sa bëjnë 5+3'"
        }
    
    def _parse_expression(self, expr: str) -> Optional[Dict[str, Any]]:
        """Parse simple expression like '5+3'"""
        import re
        
        operators = [
            (r'^(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)$', lambda a, b: a + b, '+'),
            (r'^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$', lambda a, b: a - b, '-'),
            (r'^(\d+(?:\.\d+)?)\s*\*\s*(\d+(?:\.\d+)?)$', lambda a, b: a * b, '*'),
            (r'^(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)$', lambda a, b: a / b if b != 0 else float('inf'), '/'),
            (r'^(\d+(?:\.\d+)?)\s*\^\s*(\d+(?:\.\d+)?)$', lambda a, b: a ** b, '^'),
            (r'^(\d+(?:\.\d+)?)\s*%\s*(\d+(?:\.\d+)?)$', lambda a, b: a % b if b != 0 else 0, '%'),
        ]
        
        for pattern, calc_func, op in operators:
            match = re.match(pattern, expr.strip())
            if match:
                a, b = float(match.group(1)), float(match.group(2))
                result = calc_func(a, b)
                return self._create_result(expr, result, op, [a, b])
        
        return None
    
    def _create_result(self, expr: str, result: float, operator: str, operands: tuple) -> Dict[str, Any]:
        """Create result dictionary"""
        entry = {
            "success": True,
            "expression": expr,
            "result": result,
            "operator": operator,
            "operands": list(operands),
            "formatted": f"{expr} = {result}",
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.append(entry)
        
        # Create binary packet
        if len(operands) >= 2:
            try:
                packet = AlgebraPacket(
                    expression_id=len(self.history),
                    operator=AlgebraPacket.OPERATORS.get(operator, 6),
                    operand_a=float(operands[0]) if isinstance(operands[0], (int, float, str)) else 0,
                    operand_b=float(operands[1]) if isinstance(operands[1], (int, float, str)) else 0,
                    result=result
                )
                entry["binary_packet"] = base64.b64encode(packet.to_bytes()).decode('ascii')
            except:
                pass
        
        return entry
    
    def set_variable(self, name: str, value: float):
        """Set a variable"""
        self.variables[name] = value
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get calculation history"""
        return self.history
    
    def clear_history(self):
        """Clear history"""
        self.history = []


class BinaryProtocolService:
    """Main service for binary protocols"""
    
    def __init__(self):
        self.encoder = BinaryEncoder()
        self.buffer = BinaryBuffer()
        self.calculator = SmartCalculator()
        self.signal_buffer = BinaryBuffer()
    
    def encode_response(self, data: Any, format: BinaryFormat = BinaryFormat.CUSTOM_BINARY) -> bytes:
        """Encode API response to binary"""
        return self.encoder.encode(data, format)
    
    def decode_request(self, data: bytes, format: BinaryFormat = BinaryFormat.CUSTOM_BINARY) -> Any:
        """Decode API request from binary"""
        return self.encoder.decode(data, format)
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Calculate expression"""
        return self.calculator.calculate(expression)
    
    def stream_signal(self, signal: SignalPacket) -> int:
        """Add signal to stream buffer"""
        return self.signal_buffer.write_packet(signal)
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "status": "operational",
            "formats": [f.name for f in BinaryFormat],
            "cbor2": True,
            "msgpack": True,
            "encoder_stats": self.encoder.get_stats(),
            "buffer_stats": self.buffer.get_stats(),
            "signal_buffer_stats": self.signal_buffer.get_stats(),
            "calculator_history_count": len(self.calculator.history),
            "calculator_variables": self.calculator.variables
        }


# Global service instance
binary_service = BinaryProtocolService()


def get_binary_service() -> BinaryProtocolService:
    """Get global binary service"""
    return binary_service

