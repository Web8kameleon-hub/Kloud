// gossip.rs — Tri-Channel Gossip Protocol (Pᴜ)

use serde::{Serialize, Deserialize};
use serde_cbor;
use tokio::sync::mpsc::{Receiver, Sender};
use std::collections::HashSet;

// Base Message (shared)
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct BaseMessage {
    pub node_id: u64,
    pub clock: u64,
    pub sig: Vec<u8>, // PQ Signature
}

// Digest Channel — Metadata Only
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DigestMessage {
    #[serde(flatten)]
    pub base: BaseMessage,
    pub known_msg_ids: Vec<u64>, // Hashes or sketches
}

// Delta Channel — Ops Only
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DeltaMessage {
    #[serde(flatten)]
    pub base: BaseMessage,
    pub ops: Vec<u8>, // Op IDs
}

// Bulk Channel — Full Payload
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct BulkMessage {
    #[serde(flatten)]
    pub base: BaseMessage,
    pub payload: Vec<u8>,
}

// Gossip Engine
pub struct GossipEngine {
    node_id: u64,
    peers: Vec<u64>,
    known_ids: HashSet<u64>,
    digest_tx: Sender<DigestMessage>,
    digest_rx: Receiver<DigestMessage>,
    delta_tx: Sender<DeltaMessage>,
    delta_rx: Receiver<DeltaMessage>,
    bulk_tx: Sender<BulkMessage>,
    bulk_rx: Receiver<BulkMessage>,
}

impl GossipEngine {
    pub fn new(
        node_id: u64,
        peers: Vec<u64>,
        digest_tx: Sender<DigestMessage>,
        digest_rx: Receiver<DigestMessage>,
        delta_tx: Sender<DeltaMessage>,
        delta_rx: Receiver<DeltaMessage>,
        bulk_tx: Sender<BulkMessage>,
        bulk_rx: Receiver<BulkMessage>,
    ) -> Self {
        Self {
            node_id,
            peers,
            known_ids: HashSet::new(),
            digest_tx,
            digest_rx,
            delta_tx,
            delta_rx,
            bulk_tx,
            bulk_rx,
        }
    }

    pub async fn run(&mut self) {
        let mut interval = tokio::time::interval(std::time::Duration::from_millis(1000));
        loop {
            interval.tick().await;
            self.gossip_round().await;
            self.handle_incoming().await;
        }
    }

    async fn gossip_round(&self) {
        let selected_peers = self.select_peers(3);

        // Digest Channel
        let digest = DigestMessage {
            base: BaseMessage {
                node_id: self.node_id,
                clock: 0, // Update with logical clock
                sig: vec![], // PQ sign
            },
            known_msg_ids: self.known_ids.iter().cloned().collect(),
        };
        for _ in selected_peers {
            let _ = self.digest_tx.send(digest.clone()).await;
        }
    }

    async fn handle_incoming(&mut self) {
        // Handle Digest
        if let Ok(digest) = self.digest_rx.try_recv() {
            if super::security::verify_signature(&digest.base.sig, &serde_cbor::to_vec(&digest).unwrap()) {
                let missing = digest.known_msg_ids.iter()
                    .filter(|id| !self.known_ids.contains(id))
                    .cloned()
                    .collect::<Vec<_>>();
                if !missing.is_empty() {
                    // Send Delta Request
                    let delta = DeltaMessage {
                        base: BaseMessage {
                            node_id: self.node_id,
                            clock: 0,
                            sig: vec![],
                        },
                        ops: missing.iter().map(|&id| id as u8).collect(), // Simplified
                    };
                    let _ = self.delta_tx.send(delta).await;
                }
            }
        }

        // Handle Delta (Request)
        if let Ok(delta) = self.delta_rx.try_recv() {
            if super::security::verify_signature(&delta.base.sig, &serde_cbor::to_vec(&delta).unwrap()) {
                // Send Bulk Payload
                let bulk = BulkMessage {
                    base: BaseMessage {
                        node_id: self.node_id,
                        clock: 0,
                        sig: vec![],
                    },
                    payload: vec![], // Fetch actual payload
                };
                let _ = self.bulk_tx.send(bulk).await;
            }
        }

        // Handle Bulk
        if let Ok(bulk) = self.bulk_rx.try_recv() {
            if super::security::verify_signature(&bulk.base.sig, &serde_cbor::to_vec(&bulk).unwrap()) {
                // Apply to algebra
                // super::algebra::apply_ops(&bulk.ops, &mut state, &bulk.payload);
                self.known_ids.insert(0); // Placeholder
            }
        }
    }

    fn select_peers(&self, k: usize) -> Vec<u64> {
        self.peers.iter().take(k).cloned().collect()
    }
}
