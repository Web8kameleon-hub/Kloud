// In-memory append-only log for protocol messages.
use std::collections::VecDeque;

pub struct MemoryLog {
    entries: VecDeque<Vec<u8>>,
    capacity: usize,
    next_id: u64,
}

impl MemoryLog {
    /// Create or open a log. `_path` is accepted for API compatibility but ignored;
    /// all entries are kept in-memory only.
    pub fn open(_path: &str) -> Self {
        Self {
            entries: VecDeque::with_capacity(4096),
            capacity: 4096,
            next_id: 0,
        }
    }

    /// Append raw bytes; returns a monotonic entry id.
    pub fn append(&mut self, entry: &[u8]) -> u64 {
        if self.entries.len() >= self.capacity {
            self.entries.pop_front();
        }
        self.entries.push_back(entry.to_vec());
        let id = self.next_id;
        self.next_id += 1;
        id
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn recent(&self, n: usize) -> Vec<&[u8]> {
        self.entries.iter().rev().take(n).map(|v| v.as_slice()).collect()
    }
}
