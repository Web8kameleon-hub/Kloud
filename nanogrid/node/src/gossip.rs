use protocol::*;
use std::collections::HashSet;
use tokio::sync::mpsc;

pub struct GossipEngine;

impl GossipEngine {
    pub fn new(
        _node_id: u64,
        _peers: Vec<protocol::PeerInfo>,
        _transport: impl protocol::GossipTransport,
        _digest_rx: mpsc::Receiver<protocol::Digest>,
        _request_rx: mpsc::Receiver<protocol::Request>,
        _payload_rx: mpsc::Receiver<protocol::Payload>,
        _tide_level: protocol::TideLevel,
        _keypair: crate::security::PQKeypair
    ) -> Self {
        Self {}
    }

    pub async fn run(&mut self) {
        loop {
            tokio::time::sleep(std::time::Duration::from_secs(1)).await;
        }
    }

    pub fn update_tide(&mut self, _tide: protocol::TideLevel) {}
}

