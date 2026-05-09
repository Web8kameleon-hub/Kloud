// 🔷 KLOUD BINARY PROTOCOL (CBP) - Go SDK
// ===========================================
//
// Go library for Kloud Binary Protocol.
//
// Frame Layout:
//   Offset | Size | Field
//   -------|------|-------------------------
//   0      | 4    | Magic "CLSN"
//   4      | 1    | Version
//   5      | 1    | Flags
//   6      | 2    | Payload length (big-endian)
//   8      | N    | Payload
//
// Author: Kloud Team
// License: MIT

package cbp

import (
	"bytes"
	"encoding/binary"
	"errors"
	"hash/crc32"
)

// Constants
const (
	Magic      = "CLSN"
	Version    = 1
	HeaderSize = 8
	MaxPayload = 65535
)

// Flags
const (
	FlagNone        uint8 = 0x00
	FlagCompressed  uint8 = 0x01
	FlagEncrypted   uint8 = 0x02
	FlagChunked     uint8 = 0x04
	FlagError       uint8 = 0x08
	FlagLastChunk   uint8 = 0x10
	FlagHasChecksum uint8 = 0x20
)

// MessageType represents CBP message types
type MessageType uint8

const (
	TypeUnknown   MessageType = 0x00
	TypeCalculate MessageType = 0x01
	TypeChat      MessageType = 0x02
	TypeTime      MessageType = 0x03
	TypeStatus    MessageType = 0x04
	TypeSignal    MessageType = 0x10
	TypeStream    MessageType = 0x20
	TypeAlgebra   MessageType = 0x30
	TypeError     MessageType = 0xFF
)

func (t MessageType) String() string {
	switch t {
	case TypeCalculate:
		return "CALCULATE"
	case TypeChat:
		return "CHAT"
	case TypeTime:
		return "TIME"
	case TypeStatus:
		return "STATUS"
	case TypeSignal:
		return "SIGNAL"
	case TypeStream:
		return "STREAM"
	case TypeAlgebra:
		return "ALGEBRA"
	case TypeError:
		return "ERROR"
	default:
		return "UNKNOWN"
	}
}

// Errors
var (
	ErrInvalidMagic      = errors.New("cbp: invalid magic bytes")
	ErrInvalidVersion    = errors.New("cbp: invalid version")
	ErrBufferTooSmall    = errors.New("cbp: buffer too small")
	ErrPayloadTooLarge   = errors.New("cbp: payload too large")
	ErrChecksumMismatch  = errors.New("cbp: checksum mismatch")
	ErrDecryptionFailed  = errors.New("cbp: decryption failed")
	ErrDecompressionFailed = errors.New("cbp: decompression failed")
)

// Header represents a CBP frame header
type Header struct {
	Magic      [4]byte
	Version    uint8
	Flags      uint8
	PayloadLen uint16
}

// NewHeader creates a new header
func NewHeader(flags uint8, payloadLen uint16) *Header {
	h := &Header{
		Version:    Version,
		Flags:      flags,
		PayloadLen: payloadLen,
	}
	copy(h.Magic[:], Magic)
	return h
}

// Encode encodes header to bytes
func (h *Header) Encode() []byte {
	buf := make([]byte, HeaderSize)
	copy(buf[0:4], h.Magic[:])
	buf[4] = h.Version
	buf[5] = h.Flags
	binary.BigEndian.PutUint16(buf[6:8], h.PayloadLen)
	return buf
}

// DecodeHeader decodes header from bytes
func DecodeHeader(data []byte) (*Header, error) {
	if len(data) < HeaderSize {
		return nil, ErrBufferTooSmall
	}

	h := &Header{}
	copy(h.Magic[:], data[0:4])

	if string(h.Magic[:]) != Magic {
		return nil, ErrInvalidMagic
	}

	h.Version = data[4]
	if h.Version != Version {
		return nil, ErrInvalidVersion
	}

	h.Flags = data[5]
	h.PayloadLen = binary.BigEndian.Uint16(data[6:8])

	return h, nil
}

// HasFlag checks if header has specific flag
func (h *Header) HasFlag(flag uint8) bool {
	return (h.Flags & flag) != 0
}

// Frame represents a CBP frame
type Frame struct {
	Header   *Header
	Payload  []byte
	Checksum uint32
}

// NewFrame creates a new frame
func NewFrame(flags uint8, payload []byte) *Frame {
	header := NewHeader(flags, uint16(len(payload)))
	frame := &Frame{
		Header:  header,
		Payload: payload,
	}

	if flags&FlagHasChecksum != 0 {
		frame.Checksum = crc32.ChecksumIEEE(payload)
	}

	return frame
}

// Encode encodes frame to bytes
func (f *Frame) Encode() []byte {
	size := HeaderSize + len(f.Payload)
	if f.Header.HasFlag(FlagHasChecksum) {
		size += 4
	}

	buf := bytes.NewBuffer(make([]byte, 0, size))
	buf.Write(f.Header.Encode())
	buf.Write(f.Payload)

	if f.Header.HasFlag(FlagHasChecksum) {
		checksumBytes := make([]byte, 4)
		binary.LittleEndian.PutUint32(checksumBytes, f.Checksum)
		buf.Write(checksumBytes)
	}

	return buf.Bytes()
}

// DecodeFrame decodes frame from bytes
func DecodeFrame(data []byte) (*Frame, error) {
	header, err := DecodeHeader(data)
	if err != nil {
		return nil, err
	}

	payloadEnd := HeaderSize + int(header.PayloadLen)
	if len(data) < payloadEnd {
		return nil, ErrBufferTooSmall
	}

	payload := make([]byte, header.PayloadLen)
	copy(payload, data[HeaderSize:payloadEnd])

	frame := &Frame{
		Header:  header,
		Payload: payload,
	}

	if header.HasFlag(FlagHasChecksum) {
		if len(data) < payloadEnd+4 {
			return nil, ErrBufferTooSmall
		}

		storedChecksum := binary.LittleEndian.Uint32(data[payloadEnd : payloadEnd+4])
		calculatedChecksum := crc32.ChecksumIEEE(payload)

		if storedChecksum != calculatedChecksum {
			return nil, ErrChecksumMismatch
		}

		frame.Checksum = storedChecksum
	}

	return frame, nil
}

// MessageType returns the message type from payload
func (f *Frame) MessageType() MessageType {
	if len(f.Payload) == 0 {
		return TypeUnknown
	}
	return MessageType(f.Payload[0])
}

// IsError checks if frame has error flag
func (f *Frame) IsError() bool {
	return f.Header.HasFlag(FlagError)
}

// CalculateResponse represents a calculate response
type CalculateResponse struct {
	Result     float64
	DurationUS uint32
	Expression string
}

// DecodeCalculateResponse decodes calculate response from payload
func DecodeCalculateResponse(payload []byte) (*CalculateResponse, error) {
	if len(payload) < 15 {
		return nil, ErrBufferTooSmall
	}

	resp := &CalculateResponse{}
	resp.Result = bytesToFloat64(payload[1:9])
	resp.DurationUS = binary.LittleEndian.Uint32(payload[9:13])
	exprLen := binary.LittleEndian.Uint16(payload[13:15])

	if len(payload) >= 15+int(exprLen) {
		resp.Expression = string(payload[15 : 15+exprLen])
	}

	return resp, nil
}

// AlgebraResponse represents an algebra response
type AlgebraResponse struct {
	Operation uint8
	OperandA  uint64
	OperandB  uint64
	Result    uint64
	Bits      uint8
}

// DecodeAlgebraResponse decodes algebra response from payload
func DecodeAlgebraResponse(payload []byte) (*AlgebraResponse, error) {
	if len(payload) < 26 {
		return nil, ErrBufferTooSmall
	}

	resp := &AlgebraResponse{
		Operation: payload[1],
		OperandA:  binary.LittleEndian.Uint64(payload[2:10]),
		OperandB:  binary.LittleEndian.Uint64(payload[10:18]),
		Result:    binary.LittleEndian.Uint64(payload[18:26]),
	}

	if len(payload) > 26 {
		resp.Bits = payload[26]
	} else {
		resp.Bits = 64
	}

	return resp, nil
}

// StreamFrame represents a stream frame
type StreamFrame struct {
	StreamID uint32
	Sequence uint32
	Payload  []byte
}

// NewStreamFrame creates a new stream frame
func NewStreamFrame(streamID, sequence uint32, payload []byte) *StreamFrame {
	return &StreamFrame{
		StreamID: streamID,
		Sequence: sequence,
		Payload:  payload,
	}
}

// Encode encodes stream frame to payload bytes
func (sf *StreamFrame) Encode() []byte {
	buf := bytes.NewBuffer(make([]byte, 0, 11+len(sf.Payload)))
	buf.WriteByte(byte(TypeStream))

	idBytes := make([]byte, 4)
	binary.LittleEndian.PutUint32(idBytes, sf.StreamID)
	buf.Write(idBytes)

	seqBytes := make([]byte, 4)
	binary.LittleEndian.PutUint32(seqBytes, sf.Sequence)
	buf.Write(seqBytes)

	lenBytes := make([]byte, 2)
	binary.LittleEndian.PutUint16(lenBytes, uint16(len(sf.Payload)))
	buf.Write(lenBytes)

	buf.Write(sf.Payload)
	return buf.Bytes()
}

// DecodeStreamFrame decodes stream frame from payload
func DecodeStreamFrame(data []byte) (*StreamFrame, error) {
	if len(data) < 11 {
		return nil, ErrBufferTooSmall
	}

	sf := &StreamFrame{
		StreamID: binary.LittleEndian.Uint32(data[1:5]),
		Sequence: binary.LittleEndian.Uint32(data[5:9]),
	}

	payloadLen := binary.LittleEndian.Uint16(data[9:11])
	if len(data) >= 11+int(payloadLen) {
		sf.Payload = make([]byte, payloadLen)
		copy(sf.Payload, data[11:11+payloadLen])
	}

	return sf, nil
}

// Helper functions
func bytesToFloat64(b []byte) float64 {
	bits := binary.LittleEndian.Uint64(b)
	return float64(bits)
}

// Client is a simple CBP client
type Client struct {
	endpoint string
}

// NewClient creates a new CBP client
func NewClient(endpoint string) *Client {
	return &Client{endpoint: endpoint}
}

