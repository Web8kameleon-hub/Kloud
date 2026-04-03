// node.rs — Node State Machine (Hybrid Runtime)

#![allow(dead_code)]

use tokio::sync::mpsc::{Receiver, Sender};
use crate::algebra::State;
use crate::gossip::{GossipEngine, DigestMessage, DeltaMessage, BulkMessage};
use crate::security::NodeIdentity;

// Node States
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NodeState {
    Offline,
    Syncing,
    Active,
    Degraded,
}

// Node Struct
pub struct Node {
    pub id: u64,
    pub state: NodeState,
    pub identity: NodeIdentity,
    pub state_data: State,
    pub inbox: Receiver<Vec<u8>>, // CBOR messages
    pub outbox: Sender<Vec<u8>>,
    gossip_handle: tokio::task::JoinHandle<()>,
}

impl Node {
    pub fn new(
        id: u64,
        peers: Vec<u64>,
        inbox: Receiver<Vec<u8>>,
        outbox: Sender<Vec<u8>>,
        digest_tx: Sender<DigestMessage>,
        digest_rx: Receiver<DigestMessage>,
        delta_tx: Sender<DeltaMessage>,
        delta_rx: Receiver<DeltaMessage>,
        bulk_tx: Sender<BulkMessage>,
        bulk_rx: Receiver<BulkMessage>,
    ) -> Self {
        let identity = NodeIdentity::new();
        let mut gossip_engine = GossipEngine::new(id, peers, digest_tx, digest_rx, delta_tx, delta_rx, bulk_tx, bulk_rx);
        let gossip_handle = tokio::spawn(async move {
            gossip_engine.run().await;
        });
        Self {
            id,
            state: NodeState::Offline,
            identity,
            state_data: State {
                data: vec![],
                branches: std::collections::HashMap::new(),
                model: vec![],
            },
            inbox,
            outbox,
            gossip_handle,
        }
    }

    pub async fn run(&mut self) {
        loop {
            match self.state {
                NodeState::Offline => {
                    // Buffer messages, no processing
                    if let Ok(_msg) = self.inbox.try_recv() {
                        // Store in append-only log
                    }
                    // Transition to Syncing on boot
                    self.state = NodeState::Syncing;
                }
                NodeState::Syncing => {
                    // Verify PQ keys, sync with peers
                    // On sync complete
                    self.state = NodeState::Active;
                }
                NodeState::Active => {
                    // Full operation
                    self.process_messages().await;
                }
                NodeState::Degraded => {
                    // Limited ops (e.g., no compute)
                    // Partial processing
                }
            }
            tokio::time::sleep(std::time::Duration::from_millis(100)).await;
        }
    }

    async fn process_messages(&mut self) {
        while let Ok(_cbor_msg) = self.inbox.try_recv() {
            // Deserialize CBOR to Message
            // Verify sig
            // Apply algebra ops
            // Update state
        }
    }

    pub fn transition_state(&mut self, new_state: NodeState) {
        self.state = new_state;
    }
}