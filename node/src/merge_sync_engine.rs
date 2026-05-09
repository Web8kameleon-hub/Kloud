use crate::crdt_merge::MergeEngine;
use protocol::{Message, TideLevel};
use sha3::{Digest, Sha3_256};
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

    pub fn update_tide(&mut self, tide: TideLevel) {
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
                    *local_value = Self::merge_values(local_value, remote_value);
                })
                .or_insert(remote_value.clone());
        }
    }

    fn merge_values(local: &[u8], remote: &[u8]) -> Vec<u8> {
        // Deterministic tie-break: prefer longer payload, then hash-order.
        if remote.len() > local.len() {
            return remote.to_vec();
        }
        if local.len() > remote.len() {
            return local.to_vec();
        }

        let mut lh = Sha3_256::new();
        lh.update(local);
        let lsum: [u8; 32] = lh.finalize().into();

        let mut rh = Sha3_256::new();
        rh.update(remote);
        let rsum: [u8; 32] = rh.finalize().into();

        if rsum >= lsum {
            remote.to_vec()
        } else {
            local.to_vec()
        }
    }

    pub fn get_state(&self) -> &HashMap<String, Vec<u8>> {
        &self.local_state
    }

    // Sync after partition: fetch missing from peers
    pub async fn sync_after_partition(&self, _peers: &[u64], _transport: &impl protocol::GossipTransport) {
        // TODO: Send sync requests to peers
        // For now, placeholder
    }
}