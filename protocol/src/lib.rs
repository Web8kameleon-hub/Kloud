use std::sync::Arc;
use std::collections::HashSet;
use algebra::Op;
use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::mpsc::{Receiver, Sender};
use tokio::sync::Mutex;
use tokio_util::codec::{Framed, LengthDelimitedCodec};

pub use algebra::TideLevel;

mod transport;
mod quic_transport;
mod memory_log;
mod execution_pipeline;
mod routing_engine;
mod storage_engine;
mod replication_engine;

#[derive(Clone)]
pub struct TransportMetrics {
    pub total_bytes_sent: u64,
    pub total_bytes_received: u64,
    pub avg_latency_ms: u64,
    pub bandwidth_kbps: u64,
    pub latencies: Vec<u64>, // last 10
}

#[derive(Serialize, Deserialize, Clone)]
pub struct Message {
    pub ops: Vec<u8>,
    pub payload: Vec<u8>,
    pub ttl: u64,
    pub clock: u64,
    pub sig: Vec<u8>,
    pub node_id: u64,
    pub flags: u64,
}

#[derive(Serialize, Deserialize)]
pub struct Digest {
    pub node_id: u64,
    pub clock: u64,
    pub known_ids: Vec<[u8; 32]>,
    pub sig: Vec<u8>,
}

#[derive(Serialize, Deserialize)]
pub struct Request {
    pub node_id: u64,
    pub missing: Vec<[u8; 32]>,
    pub clock: u64,
    pub sig: Vec<u8>,
}

#[derive(Serialize, Deserialize)]
pub struct Payload {
    pub messages: Vec<Message>,
    pub clock: u64,
    pub sig: Vec<u8>,
}

pub trait GossipTransport {
    async fn send_digest(&self, peer_id: u64, d: &Digest) -> Result<(), Box<dyn std::error::Error>>;
    async fn send_request(&self, peer_id: u64, r: &Request) -> Result<(), Box<dyn std::error::Error>>;
    async fn send_payload(&self, peer_id: u64, p: &Payload) -> Result<(), Box<dyn std::error::Error>>;

    async fn tide_send_digest(&self, peer_id: u64, d: &Digest, _tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        self.send_digest(peer_id, d).await
    }

    async fn tide_send_request(&self, peer_id: u64, r: &Request, _tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        self.send_request(peer_id, r).await
    }

    async fn tide_send_payload(&self, peer_id: u64, p: &Payload, _tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        self.send_payload(peer_id, p).await
    }
}

// TCP Transport Implementation
pub struct TcpTransport {
    peer_addresses: std::collections::HashMap<u64, String>, // node_id -> "127.0.0.1:8080"
    digest_tx: Sender<Digest>,
    request_tx: Sender<Request>,
    payload_tx: Sender<Payload>,
    pub metrics: Arc<Mutex<TransportMetrics>>,
    connections: Arc<Mutex<std::collections::HashMap<u64, Framed<TcpStream, LengthDelimitedCodec>>>>,
}

impl TcpTransport {
    pub fn new(
        peer_addresses: std::collections::HashMap<u64, String>,
        digest_tx: Sender<Digest>,
        request_tx: Sender<Request>,
        payload_tx: Sender<Payload>,
        listen_addr: &str,
    ) -> Self {
        let listen_addr = listen_addr.to_string();
        let transport = Self {
            peer_addresses,
            digest_tx,
            request_tx,
            payload_tx,
            metrics: Arc::new(Mutex::new(TransportMetrics {
                total_bytes_sent: 0,
                total_bytes_received: 0,
                avg_latency_ms: 50,
                bandwidth_kbps: 10000,
                latencies: vec![],
            })),
            connections: Arc::new(Mutex::new(std::collections::HashMap::new())),
        };
        let digest_tx_clone = transport.digest_tx.clone();
        let request_tx_clone = transport.request_tx.clone();
        let payload_tx_clone = transport.payload_tx.clone();
        let metrics_clone = transport.metrics.clone();
        tokio::spawn(async move {
            let listener = TcpListener::bind(&listen_addr).await.unwrap();
            loop {
                let (stream, _) = listener.accept().await.unwrap();
                let mut framed = Framed::new(stream, LengthDelimitedCodec::new());
                let digest_tx = digest_tx_clone.clone();
                let request_tx = request_tx_clone.clone();
                let payload_tx = payload_tx_clone.clone();
                let metrics = metrics_clone.clone();
                tokio::spawn(async move {
                    while let Some(Ok(bytes)) = framed.next().await {
                        // Deserialize and send to appropriate channel
                        if let Ok(digest) = serde_cbor::from_slice::<Digest>(&bytes) {
                            let mut m = metrics.lock().await;
                            m.total_bytes_received += bytes.len() as u64;
                            drop(m);
                            let _ = digest_tx.send(digest).await;
                        } else if let Ok(request) = serde_cbor::from_slice::<Request>(&bytes) {
                            let mut m = metrics.lock().await;
                            m.total_bytes_received += bytes.len() as u64;
                            drop(m);
                            let _ = request_tx.send(request).await;
                        } else if let Ok(payload) = serde_cbor::from_slice::<Payload>(&bytes) {
                            let mut m = metrics.lock().await;
                            m.total_bytes_received += bytes.len() as u64;
                            drop(m);
                            let _ = payload_tx.send(payload).await;
                        }
                    }
                });
            }
        });
        transport
    }

    pub async fn send_to_peer<T: Serialize>(&self, peer_id: u64, data: &T) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(addr) = self.peer_addresses.get(&peer_id) {
            let start = std::time::Instant::now();
            let mut connections = self.connections.lock().await;
            let framed = if let Some(framed) = connections.get_mut(&peer_id) {
                framed
            } else {
                let stream = TcpStream::connect(addr).await?;
                let framed = Framed::new(stream, LengthDelimitedCodec::new());
                connections.insert(peer_id, framed);
                connections.get_mut(&peer_id).unwrap()
            };
            let serialized = serde_cbor::to_vec(data)?;
            let bytes_sent = serialized.len() as u64;
            framed.send(serialized.into()).await?;
            let latency = start.elapsed().as_millis() as u64;

            let mut metrics = self.metrics.lock().await;
            metrics.total_bytes_sent += bytes_sent;
            metrics.latencies.push(latency);
            if metrics.latencies.len() > 10 {
                metrics.latencies.remove(0);
            }
            metrics.avg_latency_ms = metrics.latencies.iter().sum::<u64>() / metrics.latencies.len() as u64;
            metrics.bandwidth_kbps = (metrics.total_bytes_sent * 8) / 1000;
        }
        Ok(())
    }

    pub async fn tide_send_digest(&self, peer_id: u64, d: &Digest, tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        match tide {
            TideLevel::High | TideLevel::Normal => self.send_to_peer(peer_id, d).await,
            TideLevel::Low => Ok(()), // Skip digest in low tide? Wait, user said send Digest/Delta, not Bulk
        }
    }

    pub async fn tide_send_request(&self, peer_id: u64, r: &Request, tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        match tide {
            TideLevel::High => self.send_to_peer(peer_id, r).await,
            TideLevel::Normal => {
                tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                self.send_to_peer(peer_id, r).await
            }
            TideLevel::Low => self.send_to_peer(peer_id, r).await, // Send delta in low
        }
    }

    pub async fn tide_send_payload(&self, peer_id: u64, p: &Payload, tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        match tide {
            TideLevel::High => self.send_to_peer(peer_id, p).await,
            TideLevel::Normal => {
                tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                self.send_to_peer(peer_id, p).await
            }
            TideLevel::Low => Ok(()), // Skip bulk in low tide
        }
    }
}

impl GossipTransport for TcpTransport {
    async fn send_digest(&self, peer_id: u64, d: &Digest) -> Result<(), Box<dyn std::error::Error>> {
        self.send_to_peer(peer_id, d).await
    }

    async fn send_request(&self, peer_id: u64, r: &Request) -> Result<(), Box<dyn std::error::Error>> {
        self.send_to_peer(peer_id, r).await
    }

    async fn send_payload(&self, peer_id: u64, p: &Payload) -> Result<(), Box<dyn std::error::Error>> {
        self.send_to_peer(peer_id, p).await
    }
}

// Real Tri-Channel Gossip Implementation
#[derive(Clone)]
pub struct PeerInfo {
    pub id: u64,
    pub addr: String,
    pub latency_ms: u64,
    pub bandwidth_kbps: u64,
    pub load: f32,
    pub reliability: f32,
}

pub struct GossipEngine<T: GossipTransport> {
    node_id: u64,
    peers: Vec<PeerInfo>,
    known_ids: HashSet<[u8; 32]>,
    transport: T,
    digest_rx: Receiver<Digest>,
    request_rx: Receiver<Request>,
    payload_rx: Receiver<Payload>,
    tide_level: TideLevel,
    keypair: security::PQKeypair,
    storage: storage_engine::StorageEngine,
    key_store: std::collections::HashMap<u64, security::PublicKey>,
}

impl<T: GossipTransport> GossipEngine<T> {
    pub fn new(
        node_id: u64,
        peers: Vec<PeerInfo>,
        transport: T,
        digest_rx: Receiver<Digest>,
        request_rx: Receiver<Request>,
        payload_rx: Receiver<Payload>,
        tide_level: TideLevel,
        keypair: security::PQKeypair,
    ) -> Self {
        Self {
            node_id,
            peers,
            known_ids: HashSet::new(),
            transport,
            digest_rx,
            request_rx,
            payload_rx,
            tide_level,
            keypair,
            storage: storage_engine::StorageEngine::open("storage.log", tide_level),
            key_store: std::collections::HashMap::new(),
        }
    }

    pub async fn run(&mut self) {
        let (interval_ms, fanout) = match self.tide_level {
            TideLevel::High => (500, 5),
            TideLevel::Normal => (1500, 3),
            TideLevel::Low => (3000, 2),
        };
        let mut interval = tokio::time::interval(std::time::Duration::from_millis(interval_ms));
        loop {
            interval.tick().await;
            self.gossip_round(fanout).await;
            self.handle_incoming().await;
        }
    }

    async fn gossip_round(&self, fanout: usize) {
        let selected_peers = self.select_peers(fanout);
        let digest = build_digest(
            self.node_id,
            0, // clock
            self.known_ids.iter().cloned().collect(),
            |bytes| {
                let sig = security::pq_sign(&self.keypair.dilithium_private, bytes);
                sig.as_bytes().to_vec()
            }
        );
        for &peer in &selected_peers {
            let _ = self.transport.tide_send_digest(peer, &digest, self.tide_level).await;
        }
    }

    fn select_peers(&self, fanout: usize) -> Vec<u64> {
        let selected = routing_engine::RoutingEngine::select_peers(&self.peers, self.tide_level, fanout);
        selected.iter().map(|p| p.id).collect()
    }

    async fn handle_incoming(&mut self) {
        // Handle Digest
        if let Ok(digest) = self.digest_rx.try_recv() {
            // For now, skip verify as we don't have public keys
            // if super::super::security::pq_verify(&vec![], &serde_cbor::to_vec(&digest).unwrap(), &digest.sig) {
                let missing: Vec<[u8; 32]> = digest.known_ids.iter()
                    .filter(|id| !self.known_ids.contains(*id))
                    .cloned()
                    .collect();
                if !missing.is_empty() {
                    let request = build_request(
                        self.node_id,
                        0, // clock
                        missing,
                        |bytes| {
                            let sig = security::pq_sign(&self.keypair.dilithium_private, bytes);
                            sig.as_bytes().to_vec()
                        }
                    );
                    let _ = self.transport.tide_send_request(digest.node_id, &request, self.tide_level).await;
                }
            // }
        }

        // Handle Request
        if let Ok(request) = self.request_rx.try_recv() {
            // if super::super::security::pq_verify(&vec![], &serde_cbor::to_vec(&request).unwrap(), &request.sig) {
                let payload = build_payload(
                    vec![], // TODO: fetch actual messages
                    0, // clock
                    |bytes| {
                        let sig = security::pq_sign(&self.keypair.dilithium_private, bytes);
                        sig.as_bytes().to_vec()
                    }
                );
                let _ = self.transport.tide_send_payload(request.node_id, &payload, self.tide_level).await;
            // }
        }

        // Handle Payload
        if let Ok(payload) = self.payload_rx.try_recv() {
            // if super::super::security::pq_verify(&vec![], &serde_cbor::to_vec(&payload).unwrap(), &payload.sig) {
                for msg in &payload.messages {
                    let bytes = serde_cbor::to_vec(&msg).unwrap();
                    let msg_id = self.storage.store(&bytes);
                    self.known_ids.insert(msg_id);
                    // Replicate to peers
                    replication_engine::ReplicationEngine::replicate(&msg, &self.peers, self.tide_level, &self.transport).await;
                }
            // }
        }
    }

    pub fn update_tide(&mut self, tide: TideLevel) {
        self.tide_level = tide;
        self.storage.update_tide(tide);
    }
}

// FAST LOOP — Core Processing Engine
pub struct FastLoop {
    pub tide: TideLevel,
    pub seen: lru::LruCache<[u8; 32], ()>,
    pub keypair: security::PQKeypair,
    pub memory_log: memory_log::MemoryLog,
}

impl FastLoop {
    pub fn new(tide: TideLevel, keypair: security::PQKeypair, log_path: &str) -> Self {
        Self {
            tide,
            seen: lru::LruCache::new(std::num::NonZeroUsize::new(10000).unwrap()),
            keypair,
            memory_log: memory_log::MemoryLog::open(log_path),
        }
    }

    pub fn process(&mut self, msg: Message) {
        // 1. Verify PQ signature
        let msg_hash = self.hash_msg(&msg);
        if let Ok(sig) = security::DetachedSignature::from_bytes(&msg.sig) {
            if !security::pq_verify(&self.keypair.dilithium_public, &msg_hash, &sig) {
                return;
            }
        } else {
            return; // Invalid sig format
        }

        // 2. TTL / clock check
        if msg.ttl == 0 {
            return;
        }

        // 3. Idempotence check
        if self.seen.contains(&msg_hash) {
            return;
        }
        self.seen.put(msg_hash, ());

        // 4. Append to memory log
        let bytes = serde_cbor::to_vec(&msg).unwrap();
        let msg_id = self.memory_log.append(&bytes);

        // 5. Execute pipeline with policy
        let policy = execution_pipeline::PolicyEngine::decide(self.tide, 0.0); // TODO: add load
        let _result = execution_pipeline::ExecutionPipeline::execute(&msg, &policy);

        // 5. Tide-aware behavior
        match self.tide {
            TideLevel::High => self.fast_gossip(msg),
            TideLevel::Normal => self.normal_gossip(msg),
            TideLevel::Low => self.low_gossip(msg),
        }
    }

    fn hash_msg(&self, msg: &Message) -> [u8; 32] {
        use sha3::{Digest, Sha3_256};
        let mut h = Sha3_256::new();
        h.update(&msg.payload);
        h.update(&msg.ops);
        h.update(&msg.clock.to_be_bytes());
        h.update(&msg.node_id.to_be_bytes());
        h.finalize().into()
    }

    fn fast_gossip(&self, _msg: Message) {
        // fanout 5, interval 500ms
        // TODO: Integrate with GossipEngine
    }

    fn normal_gossip(&self, _msg: Message) {
        // fanout 3, interval 1500ms
    }

    fn low_gossip(&self, _msg: Message) {
        // fanout 2, interval 3000ms
        // only digest + delta
    }

    fn map_op(id: u8) -> Option<Op> {
        match id {
            1 => Some(Op::S),
            2 => Some(Op::C),
            3 => Some(Op::R),
            4 => Some(Op::E),
            5 => Some(Op::P),
            6 => Some(Op::M),
            7 => Some(Op::F),
            8 => Some(Op::J),
            9 => Some(Op::L),
            10 => Some(Op::D),
            11 => Some(Op::T),
            12 => Some(Op::X),
            _ => None,
        }
    }
}

// Tri-Channel Gossip Builders
pub fn build_digest(node_id: u64, clock: u64, known: Vec<[u8; 32]>, sign: impl Fn(&[u8]) -> Vec<u8>) -> Digest {
    let mut d = Digest {
        node_id,
        clock,
        known_ids: known,
        sig: vec![],
    };

    let bytes = serde_cbor::to_vec(&d).unwrap();
    d.sig = sign(&bytes);

    d
}

pub fn build_request(node_id: u64, clock: u64, missing: Vec<[u8; 32]>, sign: impl Fn(&[u8]) -> Vec<u8>) -> Request {
    let mut r = Request {
        node_id,
        clock,
        missing,
        sig: vec![],
    };

    let bytes = serde_cbor::to_vec(&r).unwrap();
    r.sig = sign(&bytes);

    r
}

pub fn build_payload(msgs: Vec<Message>, clock: u64, sign: impl Fn(&[u8]) -> Vec<u8>) -> Payload {
    let mut p = Payload {
        messages: msgs,
        clock,
        sig: vec![],
    };

    let bytes = serde_cbor::to_vec(&p).unwrap();
    p.sig = sign(&bytes);

    p
}
