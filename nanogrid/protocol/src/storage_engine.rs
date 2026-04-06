use std::fs::{OpenOptions};
use std::io::{Write, Seek, SeekFrom, BufWriter};
use sha3::{Sha3_256, Digest};
use std::collections::HashMap;
use crate::TideLevel;

pub struct StorageEngine {
    file: BufWriter<std::fs::File>,
    index: HashMap<[u8; 32], u64>, // msg_id -> offset
    tide_level: TideLevel,
    buffer: Vec<u8>, // for batching in low tide
}

impl StorageEngine {
    pub fn open(path: &str, tide_level: TideLevel) -> Self {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .read(true)
            .open(path)
            .unwrap();

        let mut engine = StorageEngine {
            file: BufWriter::new(file),
            index: HashMap::new(),
            tide_level,
            buffer: Vec::new(),
        };

        // TODO: load existing index from disk if persisted
        engine
    }

    pub fn update_tide(&mut self, tide_level: TideLevel) {
        if self.tide_level != tide_level {
            self.flush(); // flush on tide change
            self.tide_level = tide_level;
        }
    }

    pub fn store(&mut self, data: &[u8]) -> [u8; 32] {
        let id = Self::hash(data);

        if self.index.contains_key(&id) {
            return id; // idempotent
        }

        let offset = self.file.get_ref().seek(SeekFrom::End(0)).unwrap();

        match self.tide_level {
            TideLevel::High => {
                // Immediate write
                self.file.write_all(data).unwrap();
                self.file.write_all(b"\n").unwrap();
                self.file.flush().unwrap();
            }
            TideLevel::Normal => {
                // Buffered write
                self.file.write_all(data).unwrap();
                self.file.write_all(b"\n").unwrap();
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
        if let Some(&offset) = self.index.get(id) {
            self.file.get_ref().seek(SeekFrom::Start(offset)).unwrap();
            let mut buf = Vec::new();
            // Read until newline
            let mut byte = [0u8; 1];
            loop {
                self.file.get_ref().read_exact(&mut byte).ok()?;
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
            self.file.write_all(&self.buffer).unwrap();
            self.buffer.clear();
        }
        self.file.flush().unwrap();
    }

    fn hash(data: &[u8]) -> [u8; 32] {
        let mut h = Sha3_256::new();
        h.update(data);
        h.finalize().into()
    }

    // For CRDT merge: merge another storage's data
    pub fn merge(&mut self, other: &StorageEngine) {
        for (&id, &offset) in &other.index {
            if !self.index.contains_key(&id) {
                // Load data from other and store
                if let Some(data) = other.load(&id) {
                    self.store(&data);
                }
            }
        }
    }
}