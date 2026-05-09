//! 🔷 KLOUD BINARY PROTOCOL (CBP) - Rust SDK
//! =============================================
//!
//! Rust library for Kloud Binary Protocol.
//!
//! # Frame Layout
//! ```text
//! Offset | Size | Field
//! -------|------|-------------------------
//! 0      | 4    | Magic "CLSN"
//! 4      | 1    | Version
//! 5      | 1    | Flags
//! 6      | 2    | Payload length (big-endian)
//! 8      | N    | Payload
//! ```
//!
//! # Example
//! ```rust
//! use kloud_cbp::{Frame, Flags, MessageType};
//!
//! let frame = Frame::new(Flags::HAS_CHECKSUM, vec![0x01, 0x42]);
//! let encoded = frame.encode();
//! let decoded = Frame::decode(&encoded).unwrap();
//! ```

use std::io::{self, Read, Write};

/// Protocol magic bytes
pub const MAGIC: &[u8; 4] = b"CLSN";
pub const VERSION: u8 = 1;
pub const HEADER_SIZE: usize = 8;
pub const MAX_PAYLOAD: usize = 65535;

/// Frame flags
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum Flags {
    None = 0x00,
    Compressed = 0x01,
    Encrypted = 0x02,
    Chunked = 0x04,
    Error = 0x08,
    LastChunk = 0x10,
    HasChecksum = 0x20,
}

impl Flags {
    pub fn from_bits(bits: u8) -> Self {
        match bits & 0x3F {
            0x01 => Flags::Compressed,
            0x02 => Flags::Encrypted,
            0x04 => Flags::Chunked,
            0x08 => Flags::Error,
            0x10 => Flags::LastChunk,
            0x20 => Flags::HasChecksum,
            _ => Flags::None,
        }
    }
}

/// Message types
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum MessageType {
    Unknown = 0x00,
    Calculate = 0x01,
    Chat = 0x02,
    Time = 0x03,
    Status = 0x04,
    Signal = 0x10,
    Stream = 0x20,
    Algebra = 0x30,
    Error = 0xFF,
}

impl From<u8> for MessageType {
    fn from(val: u8) -> Self {
        match val {
            0x01 => MessageType::Calculate,
            0x02 => MessageType::Chat,
            0x03 => MessageType::Time,
            0x04 => MessageType::Status,
            0x10 => MessageType::Signal,
            0x20 => MessageType::Stream,
            0x30 => MessageType::Algebra,
            0xFF => MessageType::Error,
            _ => MessageType::Unknown,
        }
    }
}

/// Error types
#[derive(Debug, Clone)]
pub enum CbpError {
    InvalidMagic,
    InvalidVersion(u8),
    BufferTooSmall,
    PayloadTooLarge,
    ChecksumMismatch { expected: u32, got: u32 },
    DecryptionFailed,
    DecompressionFailed,
    IoError(String),
}

impl std::fmt::Display for CbpError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CbpError::InvalidMagic => write!(f, "Invalid magic bytes"),
            CbpError::InvalidVersion(v) => write!(f, "Invalid version: {}", v),
            CbpError::BufferTooSmall => write!(f, "Buffer too small"),
            CbpError::PayloadTooLarge => write!(f, "Payload too large"),
            CbpError::ChecksumMismatch { expected, got } => {
                write!(f, "Checksum mismatch: expected {:#x}, got {:#x}", expected, got)
            }
            CbpError::DecryptionFailed => write!(f, "Decryption failed"),
            CbpError::DecompressionFailed => write!(f, "Decompression failed"),
            CbpError::IoError(e) => write!(f, "IO error: {}", e),
        }
    }
}

impl std::error::Error for CbpError {}

pub type Result<T> = std::result::Result<T, CbpError>;

/// Frame header
#[derive(Debug, Clone)]
pub struct Header {
    pub magic: [u8; 4],
    pub version: u8,
    pub flags: u8,
    pub payload_len: u16,
}

impl Header {
    pub fn new(flags: u8, payload_len: u16) -> Self {
        Self {
            magic: *MAGIC,
            version: VERSION,
            flags,
            payload_len,
        }
    }

    pub fn encode(&self) -> [u8; HEADER_SIZE] {
        let mut buf = [0u8; HEADER_SIZE];
        buf[0..4].copy_from_slice(&self.magic);
        buf[4] = self.version;
        buf[5] = self.flags;
        buf[6..8].copy_from_slice(&self.payload_len.to_be_bytes());
        buf
    }

    pub fn decode(buf: &[u8]) -> Result<Self> {
        if buf.len() < HEADER_SIZE {
            return Err(CbpError::BufferTooSmall);
        }

        let magic: [u8; 4] = buf[0..4].try_into().unwrap();
        if &magic != MAGIC {
            return Err(CbpError::InvalidMagic);
        }

        let version = buf[4];
        if version != VERSION {
            return Err(CbpError::InvalidVersion(version));
        }

        let flags = buf[5];
        let payload_len = u16::from_be_bytes([buf[6], buf[7]]);

        Ok(Self {
            magic,
            version,
            flags,
            payload_len,
        })
    }

    pub fn has_flag(&self, flag: Flags) -> bool {
        (self.flags & flag as u8) != 0
    }
}

/// CBP Frame
#[derive(Debug, Clone)]
pub struct Frame {
    pub header: Header,
    pub payload: Vec<u8>,
    pub checksum: Option<u32>,
}

impl Frame {
    /// Create a new frame
    pub fn new(flags: Flags, payload: Vec<u8>) -> Self {
        let header = Header::new(flags as u8, payload.len() as u16);
        let checksum = if (flags as u8 & Flags::HasChecksum as u8) != 0 {
            Some(crc32(&payload))
        } else {
            None
        };
        Self {
            header,
            payload,
            checksum,
        }
    }

    /// Create frame with multiple flags
    pub fn with_flags(flags: u8, payload: Vec<u8>) -> Self {
        let header = Header::new(flags, payload.len() as u16);
        let checksum = if (flags & Flags::HasChecksum as u8) != 0 {
            Some(crc32(&payload))
        } else {
            None
        };
        Self {
            header,
            payload,
            checksum,
        }
    }

    /// Encode frame to bytes
    pub fn encode(&self) -> Vec<u8> {
        let mut buf = Vec::with_capacity(HEADER_SIZE + self.payload.len() + 4);
        buf.extend_from_slice(&self.header.encode());
        buf.extend_from_slice(&self.payload);
        if let Some(crc) = self.checksum {
            buf.extend_from_slice(&crc.to_le_bytes());
        }
        buf
    }

    /// Decode frame from bytes
    pub fn decode(buf: &[u8]) -> Result<Self> {
        let header = Header::decode(buf)?;
        let payload_start = HEADER_SIZE;
        let payload_end = payload_start + header.payload_len as usize;

        if buf.len() < payload_end {
            return Err(CbpError::BufferTooSmall);
        }

        let payload = buf[payload_start..payload_end].to_vec();

        let checksum = if header.has_flag(Flags::HasChecksum) {
            if buf.len() < payload_end + 4 {
                return Err(CbpError::BufferTooSmall);
            }
            let stored = u32::from_le_bytes([
                buf[payload_end],
                buf[payload_end + 1],
                buf[payload_end + 2],
                buf[payload_end + 3],
            ]);
            let calculated = crc32(&payload);
            if stored != calculated {
                return Err(CbpError::ChecksumMismatch {
                    expected: stored,
                    got: calculated,
                });
            }
            Some(stored)
        } else {
            None
        };

        Ok(Self {
            header,
            payload,
            checksum,
        })
    }

    /// Get message type from payload
    pub fn message_type(&self) -> MessageType {
        if self.payload.is_empty() {
            MessageType::Unknown
        } else {
            MessageType::from(self.payload[0])
        }
    }

    /// Check if frame has error flag
    pub fn is_error(&self) -> bool {
        self.header.has_flag(Flags::Error)
    }
}

/// CRC32 implementation
pub fn crc32(data: &[u8]) -> u32 {
    let mut crc: u32 = 0xFFFFFFFF;
    for byte in data {
        crc ^= *byte as u32;
        for _ in 0..8 {
            crc = if crc & 1 != 0 {
                (crc >> 1) ^ 0xEDB88320
            } else {
                crc >> 1
            };
        }
    }
    !crc
}

/// Calculate response
#[derive(Debug, Clone)]
pub struct CalculateResponse {
    pub result: f64,
    pub duration_us: u32,
    pub expression: String,
}

impl CalculateResponse {
    pub fn decode(payload: &[u8]) -> Result<Self> {
        if payload.len() < 15 {
            return Err(CbpError::BufferTooSmall);
        }
        let result = f64::from_le_bytes(payload[1..9].try_into().unwrap());
        let duration_us = u32::from_le_bytes(payload[9..13].try_into().unwrap());
        let expr_len = u16::from_le_bytes(payload[13..15].try_into().unwrap()) as usize;
        let expression = if payload.len() >= 15 + expr_len {
            String::from_utf8_lossy(&payload[15..15 + expr_len]).to_string()
        } else {
            String::new()
        };
        Ok(Self {
            result,
            duration_us,
            expression,
        })
    }
}

/// Algebra response
#[derive(Debug, Clone)]
pub struct AlgebraResponse {
    pub operation: u8,
    pub operand_a: u64,
    pub operand_b: u64,
    pub result: u64,
    pub bits: u8,
}

impl AlgebraResponse {
    pub fn decode(payload: &[u8]) -> Result<Self> {
        if payload.len() < 26 {
            return Err(CbpError::BufferTooSmall);
        }
        Ok(Self {
            operation: payload[1],
            operand_a: u64::from_le_bytes(payload[2..10].try_into().unwrap()),
            operand_b: u64::from_le_bytes(payload[10..18].try_into().unwrap()),
            result: u64::from_le_bytes(payload[18..26].try_into().unwrap()),
            bits: if payload.len() > 26 { payload[26] } else { 64 },
        })
    }
}

/// Stream frame
#[derive(Debug, Clone)]
pub struct StreamFrame {
    pub stream_id: u32,
    pub sequence: u32,
    pub payload: Vec<u8>,
}

impl StreamFrame {
    pub fn new(stream_id: u32, sequence: u32, payload: Vec<u8>) -> Self {
        Self {
            stream_id,
            sequence,
            payload,
        }
    }

    pub fn encode(&self) -> Vec<u8> {
        let mut buf = Vec::with_capacity(11 + self.payload.len());
        buf.push(MessageType::Stream as u8);
        buf.extend_from_slice(&self.stream_id.to_le_bytes());
        buf.extend_from_slice(&self.sequence.to_le_bytes());
        buf.extend_from_slice(&(self.payload.len() as u16).to_le_bytes());
        buf.extend_from_slice(&self.payload);
        buf
    }

    pub fn decode(data: &[u8]) -> Result<Self> {
        if data.len() < 11 {
            return Err(CbpError::BufferTooSmall);
        }
        let stream_id = u32::from_le_bytes(data[1..5].try_into().unwrap());
        let sequence = u32::from_le_bytes(data[5..9].try_into().unwrap());
        let payload_len = u16::from_le_bytes(data[9..11].try_into().unwrap()) as usize;
        let payload = data[11..11 + payload_len].to_vec();
        Ok(Self {
            stream_id,
            sequence,
            payload,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_frame_encode_decode() {
        let payload = vec![0x01, 0x42, 0x00, 0x00];
        let frame = Frame::new(Flags::HasChecksum, payload.clone());
        let encoded = frame.encode();
        
        assert_eq!(&encoded[0..4], MAGIC);
        assert_eq!(encoded[4], VERSION);
        
        let decoded = Frame::decode(&encoded).unwrap();
        assert_eq!(decoded.payload, payload);
        assert_eq!(decoded.message_type(), MessageType::Calculate);
    }

    #[test]
    fn test_crc32() {
        let data = b"hello";
        let crc = crc32(data);
        assert_eq!(crc, 0x3610A686);
    }

    #[test]
    fn test_stream_frame() {
        let sf = StreamFrame::new(123, 1, vec![1, 2, 3, 4]);
        let encoded = sf.encode();
        let decoded = StreamFrame::decode(&encoded).unwrap();
        
        assert_eq!(decoded.stream_id, 123);
        assert_eq!(decoded.sequence, 1);
        assert_eq!(decoded.payload, vec![1, 2, 3, 4]);
    }
}

