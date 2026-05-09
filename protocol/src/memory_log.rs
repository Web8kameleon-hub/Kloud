// In-memory append-only log for protocol events.
use std::collections::VecDeque;

pub struct MemoryLog {
    entries: VecDeque<String>,
    capacity: usize,
}

impl MemoryLog {
    pub fn new(capacity: usize) -> Self {
        Self {
            entries: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    pub fn append(&mut self, entry: String) {
        if self.entries.len() >= self.capacity {
            self.entries.pop_front();
        }
        self.entries.push_back(entry);
    }

    pub fn recent(&self, n: usize) -> Vec<&str> {
        self.entries.iter().rev().take(n).map(|s| s.as_str()).collect()
    }

    pub fn len(&self) -> usize {
        self.entries.len()
    }
}
