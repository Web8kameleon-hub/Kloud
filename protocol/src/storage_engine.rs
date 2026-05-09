use std::fs::{OpenOptions};
use std::io::{Read, Write, Seek, SeekFrom, BufWriter};
use sha3::{Sha3_256, Digest};
use std::collections::HashMap;
use algebra::TideLevel;

pub struct StorageEngine {
    writer: BufWriter<std::fs::File>,  // buffered writes
    reader: std::fs::File,              // direct reads
    index: HashMap<[u8; 32], u64>,      // msg_id -> offset
    tide_level: TideLevel,
    buffer: Vec<u8>,                    // for batching in low tide
}

impl StorageEngine {
    pub fn open(path: &str, tide_level: TideLevel) -> Self {
        let writer = BufWriter::new(
            OpenOptions::new()
                .create(true)
                .append(true)
                .open(path)
                .unwrap()
        );
        
        let reader = OpenOptions::new()
            .read(true)
            .open(path)
            .unwrap();

        let mut engine = StorageEngine {
            writer,
            reader,
            index: HashMap::new(),
            tide_level,
            buffer: Vec::new(),
        };

        // TODO: load existing index from disk if persisted
        engine
    }

    pub fn update_tide(&mut self, tide_level: TideLevel) {
        if !std::mem::discriminant(&self.tide_level).eq(&std::mem::discriminant(&tide_level)) {
            self.flush(); // flush on tide change
            self.tide_level = tide_level;
        }
    }

    pub fn store(&mut self, data: &[u8]) -> [u8; 32] {
        let id = Self::hash(data);

        if self.index.contains_key(&id) {
            return id; // idempotent
        }

        let offset = self.writer.get_mut().seek(SeekFrom::End(0)).unwrap();

        match self.tide_level {
            TideLevel::High => {
                // Immediate write
                self.writer.write_all(data).unwrap();
                self.writer.write_all(b"\n").unwrap();
                self.writer.flush().unwrap();
            }
            TideLevel::Normal => {
                // Buffered write
                self.writer.write_all(data).unwrap();
                self.writer.write_all(b"\n").unwrap();
            }
            TideLevel::Low => {
                // Batch in buffer
                self.buffer.extend_from_slice(data);
                self.buffer.push(b'\n');
                if self.buffer.len() > 1024 * 1024 { // 1MB batch
                    self.flush();
                }
            }
        }

        self.index.insert(id, offset);
        id
    }

    pub fn load(&mut self, id: &[u8; 32]) -> Option<Vec<u8>> {
        // Flush pending writes before reading to ensure consistency
        self.writer.flush().unwrap();

        if let Some(&offset) = self.index.get(id) {
            self.reader.seek(SeekFrom::Start(offset)).unwrap();
            let mut buf = Vec::new();
            // Read until newline
            let mut byte = [0u8; 1];
            loop {
                self.reader.read_exact(&mut byte).ok()?;
                if byte[0] == b'\n' {
                    break;
                }
                buf.push(byte[0]);
            }
            Some(buf)
        } else {
            None
        }
    }

    pub fn flush(&mut self) {
        if !self.buffer.is_empty() {
            self.writer.write_all(&self.buffer).unwrap();
            self.buffer.clear();
        }
        self.writer.flush().unwrap();
    }

    fn hash(data: &[u8]) -> [u8; 32] {
        let mut h = Sha3_256::new();
        h.update(data);
        h.finalize().into()
    }

    // For CRDT merge: merge another storage's data
    pub fn merge(&mut self, other: &mut StorageEngine) {
        let ids: Vec<[u8; 32]> = other.index.keys().copied().collect();
        for id in ids {
            if !self.index.contains_key(&id) {
                // Load data from other and store
                if let Some(data) = other.load(&id) {
                    self.store(&data);
                }
            }
        }
    }
}