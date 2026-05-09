-- 🦈 KLOUD BINARY PROTOCOL (CBP) - WIRESHARK DISSECTOR
-- ========================================================
--
-- Wireshark dissector plugin for Kloud Binary Protocol.
--
-- Installation:
--   1. Copy this file to Wireshark plugins folder:
--      - Windows: %APPDATA%\Wireshark\plugins\
--      - Linux: ~/.local/lib/wireshark/plugins/
--      - macOS: ~/.config/wireshark/plugins/
--   2. Restart Wireshark or reload plugins (Ctrl+Shift+L)
--
-- Usage:
--   - Filter: cbp
--   - Display filter: cbp.magic == "CLSN"
--   - Filter by type: cbp.type == 0x01
--
-- Frame Layout:
--   Offset | Size | Field
--   -------|------|-------------------------
--   0      | 4    | Magic "CLSN"
--   4      | 1    | Version
--   5      | 1    | Flags
--   6      | 2    | Payload length (big-endian)
--   8      | N    | Payload
--
-- Author: Kloud Team
-- License: MIT

-- Protocol declaration
local cbp_proto = Proto("cbp", "Kloud Binary Protocol")

-- Constants
local CBP_MAGIC = "CLSN"
local CBP_HEADER_SIZE = 8
local CBP_DEFAULT_PORT = 8030

-- Flag definitions
local flag_names = {
    [0x01] = "COMPRESSED",
    [0x02] = "ENCRYPTED", 
    [0x04] = "CHUNKED",
    [0x08] = "ERROR",
    [0x10] = "LAST_CHUNK",
    [0x20] = "HAS_CHECKSUM"
}

-- Message type definitions
local message_types = {
    [0x00] = "UNKNOWN",
    [0x01] = "CALCULATE",
    [0x02] = "CHAT",
    [0x03] = "TIME",
    [0x04] = "STATUS",
    [0x10] = "SIGNAL",
    [0x20] = "STREAM",
    [0x30] = "ALGEBRA",
    [0xFF] = "ERROR"
}

-- Protocol fields
local pf = {
    -- Header fields
    magic       = ProtoField.string("cbp.magic", "Magic"),
    version     = ProtoField.uint8("cbp.version", "Version", base.DEC),
    flags       = ProtoField.uint8("cbp.flags", "Flags", base.HEX),
    payload_len = ProtoField.uint16("cbp.payload_len", "Payload Length", base.DEC),
    
    -- Flag bits
    flag_compressed  = ProtoField.bool("cbp.flags.compressed", "Compressed", 8, nil, 0x01),
    flag_encrypted   = ProtoField.bool("cbp.flags.encrypted", "Encrypted", 8, nil, 0x02),
    flag_chunked     = ProtoField.bool("cbp.flags.chunked", "Chunked", 8, nil, 0x04),
    flag_error       = ProtoField.bool("cbp.flags.error", "Error", 8, nil, 0x08),
    flag_last_chunk  = ProtoField.bool("cbp.flags.last_chunk", "Last Chunk", 8, nil, 0x10),
    flag_checksum    = ProtoField.bool("cbp.flags.checksum", "Has Checksum", 8, nil, 0x20),
    
    -- Payload fields
    payload     = ProtoField.bytes("cbp.payload", "Payload"),
    msg_type    = ProtoField.uint8("cbp.type", "Message Type", base.HEX, message_types),
    checksum    = ProtoField.uint32("cbp.checksum", "Checksum", base.HEX),
    
    -- Calculate response fields
    calc_result     = ProtoField.double("cbp.calc.result", "Result"),
    calc_duration   = ProtoField.uint32("cbp.calc.duration", "Duration (μs)", base.DEC),
    calc_expr_len   = ProtoField.uint16("cbp.calc.expr_len", "Expression Length", base.DEC),
    calc_expr       = ProtoField.string("cbp.calc.expression", "Expression"),
    
    -- Algebra response fields
    algebra_op      = ProtoField.uint8("cbp.algebra.op", "Operation", base.DEC),
    algebra_a       = ProtoField.uint64("cbp.algebra.a", "Operand A", base.DEC),
    algebra_b       = ProtoField.uint64("cbp.algebra.b", "Operand B", base.DEC),
    algebra_result  = ProtoField.uint64("cbp.algebra.result", "Result", base.DEC),
    algebra_bits    = ProtoField.uint8("cbp.algebra.bits", "Bits", base.DEC),
    
    -- Stream frame fields
    stream_id       = ProtoField.uint32("cbp.stream.id", "Stream ID", base.DEC),
    stream_seq      = ProtoField.uint32("cbp.stream.seq", "Sequence", base.DEC),
    stream_len      = ProtoField.uint16("cbp.stream.len", "Stream Payload Length", base.DEC),
    
    -- Time response fields
    time_timestamp  = ProtoField.uint64("cbp.time.timestamp", "Timestamp", base.DEC),
    time_year       = ProtoField.uint16("cbp.time.year", "Year", base.DEC),
    time_month      = ProtoField.uint8("cbp.time.month", "Month", base.DEC),
    time_day        = ProtoField.uint8("cbp.time.day", "Day", base.DEC),
    time_hour       = ProtoField.uint8("cbp.time.hour", "Hour", base.DEC),
    time_minute     = ProtoField.uint8("cbp.time.minute", "Minute", base.DEC),
    time_second     = ProtoField.uint8("cbp.time.second", "Second", base.DEC),
}

-- Register all fields
cbp_proto.fields = {
    pf.magic, pf.version, pf.flags, pf.payload_len,
    pf.flag_compressed, pf.flag_encrypted, pf.flag_chunked,
    pf.flag_error, pf.flag_last_chunk, pf.flag_checksum,
    pf.payload, pf.msg_type, pf.checksum,
    pf.calc_result, pf.calc_duration, pf.calc_expr_len, pf.calc_expr,
    pf.algebra_op, pf.algebra_a, pf.algebra_b, pf.algebra_result, pf.algebra_bits,
    pf.stream_id, pf.stream_seq, pf.stream_len,
    pf.time_timestamp, pf.time_year, pf.time_month, pf.time_day,
    pf.time_hour, pf.time_minute, pf.time_second
}

-- Expert info
local ef = {
    invalid_magic = ProtoExpert.new("cbp.invalid_magic", "Invalid magic bytes",
                                     expert.group.MALFORMED, expert.severity.ERROR),
    checksum_mismatch = ProtoExpert.new("cbp.checksum_mismatch", "Checksum mismatch",
                                         expert.group.CHECKSUM, expert.severity.ERROR),
    encrypted = ProtoExpert.new("cbp.encrypted", "Payload is encrypted",
                                 expert.group.SECURITY, expert.severity.NOTE),
    compressed = ProtoExpert.new("cbp.compressed", "Payload is compressed",
                                  expert.group.COMMENTS_GROUP, expert.severity.NOTE),
}

cbp_proto.experts = { ef.invalid_magic, ef.checksum_mismatch, ef.encrypted, ef.compressed }

-- Helper: Get flag string
local function get_flags_string(flags)
    local names = {}
    for bit, name in pairs(flag_names) do
        if bit32.band(flags, bit) ~= 0 then
            table.insert(names, name)
        end
    end
    if #names == 0 then
        return "NONE"
    end
    return table.concat(names, ", ")
end

-- Helper: CRC32 calculation
local function crc32(data)
    local crc = 0xFFFFFFFF
    for i = 1, #data do
        local byte = data:byte(i)
        crc = bit32.bxor(crc, byte)
        for j = 1, 8 do
            if bit32.band(crc, 1) ~= 0 then
                crc = bit32.bxor(bit32.rshift(crc, 1), 0xEDB88320)
            else
                crc = bit32.rshift(crc, 1)
            end
        end
    end
    return bit32.bnot(crc)
end

-- Dissect Calculate response
local function dissect_calculate(buffer, pinfo, tree, offset)
    local subtree = tree:add(cbp_proto, buffer(offset), "Calculate Response")
    
    if buffer:len() >= offset + 15 then
        subtree:add_le(pf.calc_result, buffer(offset + 1, 8))
        subtree:add_le(pf.calc_duration, buffer(offset + 9, 4))
        subtree:add_le(pf.calc_expr_len, buffer(offset + 13, 2))
        
        local expr_len = buffer(offset + 13, 2):le_uint()
        if buffer:len() >= offset + 15 + expr_len then
            subtree:add(pf.calc_expr, buffer(offset + 15, expr_len))
        end
    end
    
    pinfo.cols.info:append(" [CALCULATE]")
end

-- Dissect Algebra response
local function dissect_algebra(buffer, pinfo, tree, offset)
    local subtree = tree:add(cbp_proto, buffer(offset), "Algebra Response")
    
    local ops = { [1]="AND", [2]="OR", [3]="XOR", [4]="NOT", [5]="SHL", [6]="SHR" }
    
    if buffer:len() >= offset + 26 then
        local op = buffer(offset + 1, 1):uint()
        subtree:add(pf.algebra_op, buffer(offset + 1, 1)):append_text(" (" .. (ops[op] or "?") .. ")")
        subtree:add_le(pf.algebra_a, buffer(offset + 2, 8))
        subtree:add_le(pf.algebra_b, buffer(offset + 10, 8))
        subtree:add_le(pf.algebra_result, buffer(offset + 18, 8))
        
        if buffer:len() >= offset + 27 then
            subtree:add(pf.algebra_bits, buffer(offset + 26, 1))
        end
    end
    
    pinfo.cols.info:append(" [ALGEBRA]")
end

-- Dissect Stream frame
local function dissect_stream(buffer, pinfo, tree, offset)
    local subtree = tree:add(cbp_proto, buffer(offset), "Stream Frame")
    
    if buffer:len() >= offset + 11 then
        subtree:add_le(pf.stream_id, buffer(offset + 1, 4))
        subtree:add_le(pf.stream_seq, buffer(offset + 5, 4))
        subtree:add_le(pf.stream_len, buffer(offset + 9, 2))
        
        local stream_id = buffer(offset + 1, 4):le_uint()
        local seq = buffer(offset + 5, 4):le_uint()
        pinfo.cols.info:append(string.format(" [STREAM id=%d seq=%d]", stream_id, seq))
    end
end

-- Dissect Time response
local function dissect_time(buffer, pinfo, tree, offset)
    local subtree = tree:add(cbp_proto, buffer(offset), "Time Response")
    
    if buffer:len() >= offset + 16 then
        subtree:add_le(pf.time_timestamp, buffer(offset + 1, 8))
        subtree:add_le(pf.time_year, buffer(offset + 9, 2))
        subtree:add(pf.time_month, buffer(offset + 11, 1))
        subtree:add(pf.time_day, buffer(offset + 12, 1))
        subtree:add(pf.time_hour, buffer(offset + 13, 1))
        subtree:add(pf.time_minute, buffer(offset + 14, 1))
        subtree:add(pf.time_second, buffer(offset + 15, 1))
    end
    
    pinfo.cols.info:append(" [TIME]")
end

-- Main dissector function
function cbp_proto.dissector(buffer, pinfo, tree)
    -- Check minimum length
    if buffer:len() < CBP_HEADER_SIZE then
        return 0
    end
    
    -- Check magic
    local magic = buffer(0, 4):string()
    if magic ~= CBP_MAGIC then
        return 0
    end
    
    -- Set protocol column
    pinfo.cols.protocol = "CBP"
    
    -- Create protocol tree
    local subtree = tree:add(cbp_proto, buffer(), "Kloud Binary Protocol")
    
    -- Header subtree
    local header_tree = subtree:add(cbp_proto, buffer(0, CBP_HEADER_SIZE), "Header")
    header_tree:add(pf.magic, buffer(0, 4))
    header_tree:add(pf.version, buffer(4, 1))
    
    -- Flags
    local flags = buffer(5, 1):uint()
    local flags_tree = header_tree:add(pf.flags, buffer(5, 1))
    flags_tree:append_text(" (" .. get_flags_string(flags) .. ")")
    flags_tree:add(pf.flag_compressed, buffer(5, 1))
    flags_tree:add(pf.flag_encrypted, buffer(5, 1))
    flags_tree:add(pf.flag_chunked, buffer(5, 1))
    flags_tree:add(pf.flag_error, buffer(5, 1))
    flags_tree:add(pf.flag_last_chunk, buffer(5, 1))
    flags_tree:add(pf.flag_checksum, buffer(5, 1))
    
    -- Payload length
    local payload_len = buffer(6, 2):uint()
    header_tree:add(pf.payload_len, buffer(6, 2))
    
    -- Expert info for flags
    if bit32.band(flags, 0x02) ~= 0 then
        subtree:add_proto_expert_info(ef.encrypted)
    end
    if bit32.band(flags, 0x01) ~= 0 then
        subtree:add_proto_expert_info(ef.compressed)
    end
    
    -- Payload
    local payload_offset = CBP_HEADER_SIZE
    local total_len = CBP_HEADER_SIZE + payload_len
    
    -- Check for checksum
    local has_checksum = bit32.band(flags, 0x20) ~= 0
    if has_checksum then
        total_len = total_len + 4
    end
    
    if buffer:len() >= total_len then
        local payload_tree = subtree:add(pf.payload, buffer(payload_offset, payload_len))
        
        -- Get message type
        if payload_len > 0 then
            local msg_type = buffer(payload_offset, 1):uint()
            payload_tree:add(pf.msg_type, buffer(payload_offset, 1))
            
            -- Type-specific dissection
            if msg_type == 0x01 then
                dissect_calculate(buffer, pinfo, subtree, payload_offset)
            elseif msg_type == 0x30 then
                dissect_algebra(buffer, pinfo, subtree, payload_offset)
            elseif msg_type == 0x20 then
                dissect_stream(buffer, pinfo, subtree, payload_offset)
            elseif msg_type == 0x03 then
                dissect_time(buffer, pinfo, subtree, payload_offset)
            else
                local type_name = message_types[msg_type] or "UNKNOWN"
                pinfo.cols.info:append(" [" .. type_name .. "]")
            end
        end
        
        -- Checksum
        if has_checksum and buffer:len() >= payload_offset + payload_len + 4 then
            local checksum_offset = payload_offset + payload_len
            subtree:add_le(pf.checksum, buffer(checksum_offset, 4))
            
            -- Verify checksum
            local stored_crc = buffer(checksum_offset, 4):le_uint()
            local payload_data = buffer(payload_offset, payload_len):raw()
            local calc_crc = crc32(payload_data)
            
            if stored_crc ~= calc_crc then
                subtree:add_proto_expert_info(ef.checksum_mismatch)
            end
        end
    end
    
    -- Info column
    local version = buffer(4, 1):uint()
    pinfo.cols.info = string.format("CBP v%d, %d bytes", version, payload_len)
    
    return total_len
end

-- Heuristic dissector for HTTP
local function cbp_heuristic_checker(buffer, pinfo, tree)
    if buffer:len() < CBP_HEADER_SIZE then
        return false
    end
    
    local magic = buffer(0, 4):string()
    if magic == CBP_MAGIC then
        cbp_proto.dissector(buffer, pinfo, tree)
        return true
    end
    
    return false
end

-- Register with TCP port
local tcp_port = DissectorTable.get("tcp.port")
tcp_port:add(CBP_DEFAULT_PORT, cbp_proto)

-- Register as heuristic dissector
cbp_proto:register_heuristic("tcp", cbp_heuristic_checker)

-- Post-dissector for statistics
local cbp_stats = {}

local function cbp_stats_tap()
    local tap = Listener.new("frame", "cbp")
    
    function tap.packet(pinfo, tvb, tapinfo)
        if tapinfo then
            cbp_stats.packets = (cbp_stats.packets or 0) + 1
        end
    end
    
    function tap.reset()
        cbp_stats = {}
    end
end

-- Print load message
print("🔷 Kloud Binary Protocol (CBP) dissector loaded")
print("   Port: " .. CBP_DEFAULT_PORT)
print("   Filter: cbp")

