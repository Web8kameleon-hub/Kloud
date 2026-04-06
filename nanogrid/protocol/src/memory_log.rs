use std::fs::{OpenOptions, File};
use std::io::{Write, Seek, SeekFrom, Read};
use sha3::{Sha3_256, Digest};
use std::collections::HashMap;

pub struct MemoryLog {
    file: File,
    index: HashMap<[u8; 32], u64>, // msg_id -> offset
}

impl MemoryLog {
    pub fn open(path: &str) -> Self {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .read(true)
            .open(path)
            .unwrap();

        MemoryLog {
            file,
            index: HashMap::new(),
        }
    }

    pub fn append(&mut self, data: &[u8]) -> [u8; 32] {
        let id = Self::hash(data);

        if self.index.contains_key(&id) {
            return id;
        }

        let offset = self.file.seek(SeekFrom::End(0)).unwrap();
        self.file.write_all(data).unwrap();
        self.file.write_all(b"\n").unwrap();

        self.index.insert(id, offset);
        id
    }

    pub fn read(&mut self, id: &[u8; 32]) -> Option<Vec<u8>> {
        if let Some(&offset) = self.index.get(id) {
            self.file.seek(SeekFrom::Start(offset)).unwrap();
            let mut buf = Vec::new();
            // Read until newline
            let mut byte = [0u8; 1];
            loop {
                self.file.read_exact(&mut byte).ok()?;
                if byte[0] == b'\n' {
                    break;
                }
                buf.push(byte[0]);
            }
            return Some(buf);
        }
        None
    }

    fn hash(data: &[u8]) -> [u8; 32] {
        let mut h = Sha3_256::new();
        h.update(data);
        h.finalize().into()
    }
}