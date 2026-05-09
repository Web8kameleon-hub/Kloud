# -*- coding: utf-8 -*-
"""
🔢 BINARY ALGEBRA ENGINE
========================
Algjebër binare e VËRTETË - jo encoding!

Operacione:
- AND, OR, XOR, NOT, NAND, NOR
- SHIFT LEFT, SHIFT RIGHT
- Binary Addition, Subtraction, Multiplication
- Bit Manipulation
- Binary Matrix Operations
- Signal Algebra (superpozim, filtrim, korelacion)
- Fourier në binary
- Polynomial në GF(2)

Author: Kloud Team
"""

import struct
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime
import math


class BinaryOp(IntEnum):
    """Operacionet binare"""
    AND = 0
    OR = 1
    XOR = 2
    NOT = 3
    NAND = 4
    NOR = 5
    XNOR = 6
    SHL = 7   # Shift Left
    SHR = 8   # Shift Right
    ROL = 9   # Rotate Left
    ROR = 10  # Rotate Right
    ADD = 11  # Binary Add
    SUB = 12  # Binary Subtract
    MUL = 13  # Binary Multiply
    DIV = 14  # Binary Divide
    MOD = 15  # Modulo


@dataclass
class BinaryNumber:
    """Numër binar me operacione"""
    value: int
    bits: int = 64
    
    def __post_init__(self):
        # Mask to bit width
        self.value = self.value & ((1 << self.bits) - 1)
    
    @property
    def binary(self) -> str:
        """Përfaqësimi binar"""
        return format(self.value, f'0{self.bits}b')
    
    @property
    def hex(self) -> str:
        """Përfaqësimi hex"""
        return format(self.value, f'0{self.bits//4}x')
    
    @property
    def bytes(self) -> bytes:
        """Konverto në bytes"""
        byte_count = (self.bits + 7) // 8
        return self.value.to_bytes(byte_count, 'big')
    
    def bit(self, position: int) -> int:
        """Merr bitin në pozicion"""
        return (self.value >> position) & 1
    
    def set_bit(self, position: int, value: int = 1) -> 'BinaryNumber':
        """Vendos bitin"""
        if value:
            new_val = self.value | (1 << position)
        else:
            new_val = self.value & ~(1 << position)
        return BinaryNumber(new_val, self.bits)
    
    def toggle_bit(self, position: int) -> 'BinaryNumber':
        """Toggle bitin"""
        return BinaryNumber(self.value ^ (1 << position), self.bits)
    
    def count_ones(self) -> int:
        """Numëro 1-at"""
        return bin(self.value).count('1')
    
    def count_zeros(self) -> int:
        """Numëro 0-at"""
        return self.bits - self.count_ones()
    
    # Operacionet binare
    def __and__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return BinaryNumber(self.value & other.value, max(self.bits, other.bits))
    
    def __or__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return BinaryNumber(self.value | other.value, max(self.bits, other.bits))
    
    def __xor__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return BinaryNumber(self.value ^ other.value, max(self.bits, other.bits))
    
    def __invert__(self) -> 'BinaryNumber':
        return BinaryNumber(~self.value, self.bits)
    
    def __lshift__(self, n: int) -> 'BinaryNumber':
        return BinaryNumber(self.value << n, self.bits)
    
    def __rshift__(self, n: int) -> 'BinaryNumber':
        return BinaryNumber(self.value >> n, self.bits)
    
    def __add__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return BinaryNumber(self.value + other.value, max(self.bits, other.bits))
    
    def __sub__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return BinaryNumber(self.value - other.value, max(self.bits, other.bits))
    
    def __mul__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return BinaryNumber(self.value * other.value, max(self.bits, other.bits))
    
    def __truediv__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        if other.value == 0:
            return BinaryNumber(0, self.bits)
        return BinaryNumber(self.value // other.value, self.bits)
    
    def __mod__(self, other: 'BinaryNumber') -> 'BinaryNumber':
        if other.value == 0:
            return BinaryNumber(0, self.bits)
        return BinaryNumber(self.value % other.value, self.bits)
    
    def nand(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return ~(self & other)
    
    def nor(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return ~(self | other)
    
    def xnor(self, other: 'BinaryNumber') -> 'BinaryNumber':
        return ~(self ^ other)
    
    def rotate_left(self, n: int) -> 'BinaryNumber':
        """Rotate left"""
        n = n % self.bits
        return BinaryNumber(
            ((self.value << n) | (self.value >> (self.bits - n))) & ((1 << self.bits) - 1),
            self.bits
        )
    
    def rotate_right(self, n: int) -> 'BinaryNumber':
        """Rotate right"""
        n = n % self.bits
        return BinaryNumber(
            ((self.value >> n) | (self.value << (self.bits - n))) & ((1 << self.bits) - 1),
            self.bits
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "binary": self.binary,
            "hex": self.hex,
            "bits": self.bits,
            "ones": self.count_ones(),
            "zeros": self.count_zeros()
        }


@dataclass
class BinarySignal:
    """Sinjal binar për algjebër sinjalesh"""
    samples: List[int]  # 0 ose 1
    sample_rate: int = 1000  # Hz
    name: str = "signal"
    
    def __len__(self) -> int:
        return len(self.samples)
    
    @property
    def duration(self) -> float:
        """Kohëzgjatja në sekonda"""
        return len(self.samples) / self.sample_rate
    
    @property
    def energy(self) -> int:
        """Energjia (numri i 1-ave)"""
        return sum(self.samples)
    
    @property
    def duty_cycle(self) -> float:
        """Duty cycle"""
        return self.energy / len(self.samples) if self.samples else 0
    
    def __and__(self, other: 'BinarySignal') -> 'BinarySignal':
        """AND i dy sinjaleve"""
        min_len = min(len(self), len(other))
        return BinarySignal(
            [self.samples[i] & other.samples[i] for i in range(min_len)],
            self.sample_rate,
            f"{self.name}_AND_{other.name}"
        )
    
    def __or__(self, other: 'BinarySignal') -> 'BinarySignal':
        """OR i dy sinjaleve"""
        min_len = min(len(self), len(other))
        return BinarySignal(
            [self.samples[i] | other.samples[i] for i in range(min_len)],
            self.sample_rate,
            f"{self.name}_OR_{other.name}"
        )
    
    def __xor__(self, other: 'BinarySignal') -> 'BinarySignal':
        """XOR i dy sinjaleve"""
        min_len = min(len(self), len(other))
        return BinarySignal(
            [self.samples[i] ^ other.samples[i] for i in range(min_len)],
            self.sample_rate,
            f"{self.name}_XOR_{other.name}"
        )
    
    def __invert__(self) -> 'BinarySignal':
        """NOT i sinjalit"""
        return BinarySignal(
            [1 - s for s in self.samples],
            self.sample_rate,
            f"NOT_{self.name}"
        )
    
    def shift(self, n: int) -> 'BinarySignal':
        """Shift sinjali"""
        if n > 0:  # Shift right (delay)
            return BinarySignal(
                [0] * n + self.samples[:-n] if n < len(self) else [0] * len(self),
                self.sample_rate,
                f"{self.name}_SHR{n}"
            )
        elif n < 0:  # Shift left (advance)
            n = -n
            return BinarySignal(
                self.samples[n:] + [0] * n if n < len(self) else [0] * len(self),
                self.sample_rate,
                f"{self.name}_SHL{n}"
            )
        return self
    
    def correlate(self, other: 'BinarySignal') -> List[int]:
        """Korelacioni kryqëzor"""
        result = []
        for lag in range(-len(other) + 1, len(self)):
            corr = 0
            for i in range(len(other)):
                j = i + lag
                if 0 <= j < len(self):
                    corr += self.samples[j] * other.samples[i]
            result.append(corr)
        return result
    
    def convolve(self, kernel: List[int]) -> 'BinarySignal':
        """Konvolucioni"""
        result = []
        for i in range(len(self)):
            val = 0
            for j, k in enumerate(kernel):
                idx = i - j + len(kernel) // 2
                if 0 <= idx < len(self):
                    val += self.samples[idx] * k
            result.append(1 if val > len(kernel) // 2 else 0)
        return BinarySignal(result, self.sample_rate, f"{self.name}_conv")
    
    def edges(self) -> List[Tuple[int, str]]:
        """Gjej edges (rising/falling)"""
        edges = []
        for i in range(1, len(self.samples)):
            if self.samples[i-1] == 0 and self.samples[i] == 1:
                edges.append((i, "rising"))
            elif self.samples[i-1] == 1 and self.samples[i] == 0:
                edges.append((i, "falling"))
        return edges
    
    def frequency(self) -> float:
        """Frekuenca e përafërt"""
        edges_list = self.edges()
        if len(edges_list) < 2:
            return 0
        periods = []
        rising_indices = [e[0] for e in edges_list if e[1] == "rising"]
        for i in range(1, len(rising_indices)):
            periods.append(rising_indices[i] - rising_indices[i-1])
        if not periods:
            return 0
        avg_period = sum(periods) / len(periods)
        return self.sample_rate / avg_period if avg_period > 0 else 0
    
    def to_bytes(self) -> bytes:
        """Konverto në bytes (8 samples = 1 byte)"""
        result = bytearray()
        for i in range(0, len(self.samples), 8):
            byte = 0
            for j in range(8):
                if i + j < len(self.samples):
                    byte |= (self.samples[i + j] << (7 - j))
            result.append(byte)
        return bytes(result)
    
    @classmethod
    def from_bytes(cls, data: bytes, sample_rate: int = 1000) -> 'BinarySignal':
        """Krijo nga bytes"""
        samples = []
        for byte in data:
            for i in range(7, -1, -1):
                samples.append((byte >> i) & 1)
        return cls(samples, sample_rate)
    
    @classmethod
    def clock(cls, length: int, period: int = 2, sample_rate: int = 1000) -> 'BinarySignal':
        """Krijo sinjal clock"""
        samples = []
        for i in range(length):
            samples.append(1 if (i // (period // 2)) % 2 == 0 else 0)
        return cls(samples, sample_rate, "clock")
    
    @classmethod
    def pulse(cls, length: int, start: int, width: int, sample_rate: int = 1000) -> 'BinarySignal':
        """Krijo puls"""
        samples = [0] * length
        for i in range(start, min(start + width, length)):
            samples[i] = 1
        return cls(samples, sample_rate, "pulse")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "length": len(self),
            "sample_rate": self.sample_rate,
            "duration_ms": self.duration * 1000,
            "energy": self.energy,
            "duty_cycle": round(self.duty_cycle, 4),
            "frequency_hz": round(self.frequency(), 2),
            "samples_preview": self.samples[:32],
            "binary_repr": ''.join(str(s) for s in self.samples[:64])
        }


class BinaryMatrix:
    """Matricë binare për operacione"""
    
    def __init__(self, rows: int, cols: int, data: Optional[List[List[int]]] = None):
        self.rows = rows
        self.cols = cols
        if data:
            self.data = [[d & 1 for d in row] for row in data]
        else:
            self.data = [[0] * cols for _ in range(rows)]
    
    def get(self, row: int, col: int) -> int:
        return self.data[row][col]
    
    def set(self, row: int, col: int, value: int):
        self.data[row][col] = value & 1
    
    def __and__(self, other: 'BinaryMatrix') -> 'BinaryMatrix':
        """AND element-wise"""
        result = BinaryMatrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = self.data[i][j] & other.data[i][j]
        return result
    
    def __or__(self, other: 'BinaryMatrix') -> 'BinaryMatrix':
        """OR element-wise"""
        result = BinaryMatrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = self.data[i][j] | other.data[i][j]
        return result
    
    def __xor__(self, other: 'BinaryMatrix') -> 'BinaryMatrix':
        """XOR element-wise"""
        result = BinaryMatrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = self.data[i][j] ^ other.data[i][j]
        return result
    
    def __invert__(self) -> 'BinaryMatrix':
        """NOT"""
        result = BinaryMatrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[i][j] = 1 - self.data[i][j]
        return result
    
    def multiply_gf2(self, other: 'BinaryMatrix') -> 'BinaryMatrix':
        """Shumëzim në GF(2) - XOR për mbledhje"""
        if self.cols != other.rows:
            raise ValueError("Dimensione të papërshtatshme")
        
        result = BinaryMatrix(self.rows, other.cols)
        for i in range(self.rows):
            for j in range(other.cols):
                val = 0
                for k in range(self.cols):
                    val ^= (self.data[i][k] & other.data[k][j])
                result.data[i][j] = val
        return result
    
    def transpose(self) -> 'BinaryMatrix':
        """Transpozë"""
        result = BinaryMatrix(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                result.data[j][i] = self.data[i][j]
        return result
    
    def rank_gf2(self) -> int:
        """Rank në GF(2)"""
        # Copy matrix
        mat = [row[:] for row in self.data]
        rank = 0
        
        for col in range(min(self.rows, self.cols)):
            # Find pivot
            pivot = None
            for row in range(rank, self.rows):
                if mat[row][col] == 1:
                    pivot = row
                    break
            
            if pivot is None:
                continue
            
            # Swap
            mat[rank], mat[pivot] = mat[pivot], mat[rank]
            
            # Eliminate
            for row in range(self.rows):
                if row != rank and mat[row][col] == 1:
                    for c in range(self.cols):
                        mat[row][c] ^= mat[rank][c]
            
            rank += 1
        
        return rank
    
    def to_bytes(self) -> bytes:
        """Konverto në bytes"""
        # Flatten and pack
        bits = []
        for row in self.data:
            bits.extend(row)
        
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= (bits[i + j] << (7 - j))
            result.append(byte)
        
        # Prepend dimensions
        header = struct.pack('>HH', self.rows, self.cols)
        return header + bytes(result)
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'BinaryMatrix':
        """Krijo nga bytes"""
        rows, cols = struct.unpack('>HH', data[:4])
        bits = []
        for byte in data[4:]:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        
        matrix = cls(rows, cols)
        for i in range(rows):
            for j in range(cols):
                idx = i * cols + j
                if idx < len(bits):
                    matrix.data[i][j] = bits[idx]
        return matrix
    
    @classmethod
    def identity(cls, n: int) -> 'BinaryMatrix':
        """Matricë identiteti"""
        result = cls(n, n)
        for i in range(n):
            result.data[i][i] = 1
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "rank": self.rank_gf2(),
            "ones": sum(sum(row) for row in self.data),
            "density": sum(sum(row) for row in self.data) / (self.rows * self.cols),
            "data": self.data
        }


class BinaryAlgebraEngine:
    """Motori kryesor i algjebës binare"""
    
    def __init__(self):
        self.registers: Dict[str, BinaryNumber] = {}
        self.signals: Dict[str, BinarySignal] = {}
        self.matrices: Dict[str, BinaryMatrix] = {}
        self.history: List[Dict[str, Any]] = []
    
    # ============ NUMRA BINARË ============
    
    def create_number(self, value: int, bits: int = 64, name: Optional[str] = None) -> BinaryNumber:
        """Krijo numër binar"""
        num = BinaryNumber(value, bits)
        if name:
            self.registers[name] = num
        return num
    
    def operate(self, a: Union[int, BinaryNumber], op: BinaryOp, b: Optional[Union[int, BinaryNumber]] = None, bits: int = 64) -> BinaryNumber:
        """Kryej operacion binar"""
        if isinstance(a, int):
            a = BinaryNumber(a, bits)
        if b is not None and isinstance(b, int):
            b = BinaryNumber(b, bits)
        
        if op == BinaryOp.AND:
            result = a & b
        elif op == BinaryOp.OR:
            result = a | b
        elif op == BinaryOp.XOR:
            result = a ^ b
        elif op == BinaryOp.NOT:
            result = ~a
        elif op == BinaryOp.NAND:
            result = a.nand(b)
        elif op == BinaryOp.NOR:
            result = a.nor(b)
        elif op == BinaryOp.XNOR:
            result = a.xnor(b)
        elif op == BinaryOp.SHL:
            result = a << (b.value if b else 1)
        elif op == BinaryOp.SHR:
            result = a >> (b.value if b else 1)
        elif op == BinaryOp.ROL:
            result = a.rotate_left(b.value if b else 1)
        elif op == BinaryOp.ROR:
            result = a.rotate_right(b.value if b else 1)
        elif op == BinaryOp.ADD:
            result = a + b
        elif op == BinaryOp.SUB:
            result = a - b
        elif op == BinaryOp.MUL:
            result = a * b
        elif op == BinaryOp.DIV:
            result = a / b
        elif op == BinaryOp.MOD:
            result = a % b
        else:
            result = a
        
        self.history.append({
            "op": op.name,
            "a": a.value,
            "b": b.value if b else None,
            "result": result.value,
            "binary_result": result.binary,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def operate_raw(self, a: int, op: str, b: int = 0, bits: int = 64) -> bytes:
        """Kryej operacion dhe kthe bytes direkt"""
        op_map = {
            "and": BinaryOp.AND, "&": BinaryOp.AND,
            "or": BinaryOp.OR, "|": BinaryOp.OR,
            "xor": BinaryOp.XOR, "^": BinaryOp.XOR,
            "not": BinaryOp.NOT, "~": BinaryOp.NOT,
            "nand": BinaryOp.NAND,
            "nor": BinaryOp.NOR,
            "xnor": BinaryOp.XNOR,
            "shl": BinaryOp.SHL, "<<": BinaryOp.SHL,
            "shr": BinaryOp.SHR, ">>": BinaryOp.SHR,
            "rol": BinaryOp.ROL,
            "ror": BinaryOp.ROR,
            "add": BinaryOp.ADD, "+": BinaryOp.ADD,
            "sub": BinaryOp.SUB, "-": BinaryOp.SUB,
            "mul": BinaryOp.MUL, "*": BinaryOp.MUL,
            "div": BinaryOp.DIV, "/": BinaryOp.DIV,
            "mod": BinaryOp.MOD, "%": BinaryOp.MOD,
        }
        
        binary_op = op_map.get(op.lower(), BinaryOp.AND)
        result = self.operate(a, binary_op, b, bits)
        return result.bytes
    
    # ============ SINJALE ============
    
    def create_signal(self, samples: List[int], sample_rate: int = 1000, name: str = "signal") -> BinarySignal:
        """Krijo sinjal binar"""
        signal = BinarySignal([s & 1 for s in samples], sample_rate, name)
        self.signals[name] = signal
        return signal
    
    def signal_op(self, name1: str, op: str, name2: str) -> BinarySignal:
        """Operacion midis dy sinjaleve"""
        s1 = self.signals.get(name1)
        s2 = self.signals.get(name2)
        if not s1 or not s2:
            raise ValueError("Sinjalet nuk u gjetën")
        
        if op.lower() in ["and", "&"]:
            return s1 & s2
        elif op.lower() in ["or", "|"]:
            return s1 | s2
        elif op.lower() in ["xor", "^"]:
            return s1 ^ s2
        else:
            return s1 & s2
    
    # ============ MATRICA ============
    
    def create_matrix(self, rows: int, cols: int, data: Optional[List[List[int]]] = None, name: Optional[str] = None) -> BinaryMatrix:
        """Krijo matricë binare"""
        matrix = BinaryMatrix(rows, cols, data)
        if name:
            self.matrices[name] = matrix
        return matrix
    
    def matrix_multiply_gf2(self, name1: str, name2: str) -> BinaryMatrix:
        """Shumëzim matricash në GF(2)"""
        m1 = self.matrices.get(name1)
        m2 = self.matrices.get(name2)
        if not m1 or not m2:
            raise ValueError("Matricat nuk u gjetën")
        return m1.multiply_gf2(m2)
    
    # ============ PACKET BINARY ============
    
    def create_packet(self, data: Dict[str, Any]) -> bytes:
        """Krijo paketë binare të strukturuar"""
        packet = bytearray()
        
        # Magic: BALG (Binary ALGebra)
        packet.extend(b'BALG')
        
        # Version: 1 byte
        packet.append(1)
        
        # Timestamp: 8 bytes
        packet.extend(struct.pack('>Q', int(datetime.now().timestamp() * 1000000)))
        
        # Field count: 2 bytes
        packet.extend(struct.pack('>H', len(data)))
        
        # Fields
        for key, value in data.items():
            # Key length + key
            key_bytes = key.encode('utf-8')
            packet.append(len(key_bytes))
            packet.extend(key_bytes)
            
            # Value type + value
            if isinstance(value, int):
                packet.append(1)  # Type: int
                packet.extend(struct.pack('>q', value))
            elif isinstance(value, float):
                packet.append(2)  # Type: float
                packet.extend(struct.pack('>d', value))
            elif isinstance(value, str):
                packet.append(3)  # Type: string
                val_bytes = value.encode('utf-8')
                packet.extend(struct.pack('>H', len(val_bytes)))
                packet.extend(val_bytes)
            elif isinstance(value, bytes):
                packet.append(4)  # Type: bytes
                packet.extend(struct.pack('>H', len(value)))
                packet.extend(value)
            elif isinstance(value, list):
                packet.append(5)  # Type: list of ints
                packet.extend(struct.pack('>H', len(value)))
                for v in value:
                    packet.extend(struct.pack('>q', int(v)))
            else:
                packet.append(0)  # Type: null
        
        # Checksum: 4 bytes (simple XOR)
        checksum = 0
        for b in packet:
            checksum ^= b
        packet.extend(struct.pack('>I', checksum))
        
        return bytes(packet)
    
    def parse_packet(self, data: bytes) -> Dict[str, Any]:
        """Parse paketë binare"""
        if data[:4] != b'BALG':
            raise ValueError("Invalid packet magic")
        
        pos = 4
        version = data[pos]
        pos += 1
        
        timestamp = struct.unpack('>Q', data[pos:pos+8])[0]
        pos += 8
        
        field_count = struct.unpack('>H', data[pos:pos+2])[0]
        pos += 2
        
        result = {
            "_version": version,
            "_timestamp": timestamp,
            "_timestamp_iso": datetime.fromtimestamp(timestamp / 1000000).isoformat()
        }
        
        for _ in range(field_count):
            key_len = data[pos]
            pos += 1
            key = data[pos:pos+key_len].decode('utf-8')
            pos += key_len
            
            value_type = data[pos]
            pos += 1
            
            if value_type == 1:  # int
                value = struct.unpack('>q', data[pos:pos+8])[0]
                pos += 8
            elif value_type == 2:  # float
                value = struct.unpack('>d', data[pos:pos+8])[0]
                pos += 8
            elif value_type == 3:  # string
                str_len = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 2
                value = data[pos:pos+str_len].decode('utf-8')
                pos += str_len
            elif value_type == 4:  # bytes
                bytes_len = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 2
                value = data[pos:pos+bytes_len]
                pos += bytes_len
            elif value_type == 5:  # list
                list_len = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 2
                value = []
                for _ in range(list_len):
                    value.append(struct.unpack('>q', data[pos:pos+8])[0])
                    pos += 8
            else:
                value = None
            
            result[key] = value
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "registers": len(self.registers),
            "signals": len(self.signals),
            "matrices": len(self.matrices),
            "operations_history": len(self.history),
            "last_operations": self.history[-5:] if self.history else []
        }


# Global instance
_binary_algebra: Optional[BinaryAlgebraEngine] = None


def get_binary_algebra() -> BinaryAlgebraEngine:
    """Get global binary algebra engine"""
    global _binary_algebra
    if _binary_algebra is None:
        _binary_algebra = BinaryAlgebraEngine()
    return _binary_algebra

