use crate::crdt_merge::MergeEngine;
use protocol::{Message, TideLevel};
use std::collections::HashMap;

pub struct MergeSyncEngine {
    local_state: HashMap<String, Vec<u8>>, // key -> value
    tide_level: TideLevel,
}

impl MergeSyncEngine {
    pub fn new(tide_level: TideLevel) -> Self {
        MergeSyncEngine {
            local_state: HashMap::new(),
            tide_level,
        }
    }

    pub fn fupdate_tide(&mut self, tide: TideLevel) {
        self.tide_level = tide;
    }

    pub fn apply_message(&mut self, msg: &Message) {
        // Apply ops to local state using CRDT merge
        for &op_id in &msg.ops {
            if op_id == 1 { // S - Store
                let key = "default".to_string(); // TODO: extract key from payload
                let value = msg.payload.clone();
                self.local_state.insert(key, value);
            }
            // TODO: other ops
        }
    }

    pub fn merge_remote_state(&mut self, remote_state: &HashMap<String, Vec<u8>>) {
        // CRDT merge
        for (key, remote_value) in remote_state {
            self.local_state.entry(key.clone())
                .and_modify(|local_value| {
                    *local_value = MergeEngine::merge(local_value, remote_value);
                })
                .or_insert(remote_value.clone());
        }
    }

    pub fn get_state(&self) -> &HashMap<String, Vec<u8>> {
        &self.local_state
    }

    // Sync after partition: fetch missing from peers
    pub async fn sync_after_partition(&self, peers: &[u64], transport: &impl protocol::transport::GossipTransport) {
        // TODO: Send sync requests to peers
        // For now, placeholder
    }
}