use serde::{Serialize, Deserialize};
use std::collections::HashMap;
use std::collections::HashSet;
use std::sync::Arc;
use tokio::sync::{mpsc, Mutex};
use tokio::net::{TcpListener, TcpStream};
use tokio_util::codec::{Framed, LengthDelimitedCodec};
use tokio_util::codec::BytesCodec;
use sha3::Sha3_256;
use lru::LruCache;
use std::num::NonZeroUsize;

mod transport;
mod quic_transport;
mod memory_log;
mod execution_pipeline;
mod routing_engine;
mod storage_engine;
mod replication_engine;

pub use transport::TcpTransport;
pub use transport::GossipTransport;
pub use algebra::TideLevel;
pub use algebra::Op;

#[derive(Clone, Default)]
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
}

// TCP Transport Implementation
pub struct TcpTransport {
    peer_addresses: HashMap<u64, String>,
    digest_tx: mpsc::Sender<Digest>,
    request_tx: mpsc::Sender<Request>,
    payload_tx: mpsc::Sender<Payload>,
    pub metrics: Arc<Mutex<TransportMetrics>>,
    connections: Arc<Mutex<HashMap<u64, Framed<TcpStream, LengthDelimitedCodec>>>>,
}

impl TcpTransport {
    pub fn new(
        peer_addresses: HashMap<u64, String>,
        digest_tx: mpsc::Sender<Digest>,
        request_tx: mpsc::Sender<Request>,
        payload_tx: mpsc::Sender<Payload>,
        listen_addr: &str,
    ) -> Self {
        let transport = Self {
            peer_addresses,
            digest_tx,
            request_tx,
            payload_tx,
            metrics: Arc::new(Mutex::new(TransportMetrics::default())),
            connections: Arc::new(Mutex::new(HashMap::new())),
        };
        let digest_tx_clone = transport.digest_tx.clone();
        let request_tx_clone = transport.request_tx.clone();
        let payload_tx_clone = transport.payload_tx.clone();
        let metrics_clone = transport.metrics.clone();
        tokio::spawn(async move {
            let listener = TcpListener::bind(listen_addr).await.unwrap();
            loop {
                let (stream, _) = listener.accept().await.unwrap();
                let mut framed = Framed::new(stream, LengthDelimitedCodec::new());
                let digest_tx = digest_tx_clone.clone();
                let request_tx = request_tx_clone.clone();
                let payload_tx = payload_tx_clone.clone();
                let metrics = metrics_clone.clone();
                tokio::spawn(async move {
                    while let Some(Ok(bytes)) = framed.next().await {
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
            framed.send(BytesCodec::encode_vec(serialized)).await?;
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
            TideLevel::Low => Ok(()),
        }
    }

    pub async fn tide_send_request(&self, peer_id: u64, r: &Request, tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        match tide {
            TideLevel::High => self.send_to_peer(peer_id, r).await,
            TideLevel::Normal => {
                tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                self.send_to_peer(peer_id, r).await
            }
            TideLevel::Low => self.send_to_peer(peer_id, r).await,
        }
    }

    pub async fn tide_send_payload(&self, peer_id: u64, p: &Payload, tide: TideLevel) -> Result<(), Box<dyn std::error::Error>> {
        match tide {
            TideLevel::High => self.send_to_peer(peer_id, p).await,
            TideLevel::Normal => {
                tokio::time::sleep(std::time::Duration::from_millis(50)).await;
                self.send_to_peer(peer_id, p).await
            }
            TideLevel::Low => self.send_to_peer(peer_id, p).await,
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

#[derive(Clone)]
pub struct PeerInfo {
    pub id: u64,
    pub addr: String,
    pub latency_ms: u64,
    pub bandwidth_kbps: u64,
    pub load: f32,
    pub reliability: f32,
}

// Simplified GossipEngine (placeholder implementation)
pub struct GossipEngine {}

impl GossipEngine {
    pub fn new(_node_id: u64, _peers: Vec<PeerInfo>, _transport: impl GossipTransport, _digest_rx: mpsc::Receiver<Digest>, _request_rx: mpsc::Receiver<Request>, _payload_rx: mpsc::Receiver<Payload>, _tide_level: TideLevel, _keypair: security::PQKeypair) -> Self {
        Self {}
    }

    pub async fn run(&mut self) {
        tokio::time::sleep(std::time::Duration::from_secs(1)).await;
    }

    pub fn update_tide(&mut self, _tide: TideLevel) {}
}

// Tri-Channel Gossip Builders
pub fn build_digest(_node_id: u64, _clock: u64, _known: Vec<[u8; 32]>, _sign: impl Fn(&[u8]) -> Vec<u8>) -> Digest {
    Digest {
        node_id: 0,
        clock: 0,
        known_ids: vec![],
        sig: vec![],
    }
}

pub fn build_request(_node_id: u64, _clock: u64, _missing: Vec<[u8; 32]>, _sign: impl Fn(&[u8]) -> Vec<u8>) -> Request {
    Request {
        node_id: 0,
        clock: 0,
        missing: vec![],
        sig: vec![],
    }
}

pub fn build_payload(_msgs: Vec<Message>, _clock: u64, _sign: impl Fn(&[u8]) -> Vec<u8>) -> Payload {
    Payload {
        messages: vec![],
        clock: 0,
        sig: vec![],
    }
}

