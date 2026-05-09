use protocol::*;
use algebra::*;
use security::*;
use serde::{Deserialize, Serialize};
use tokio::sync::mpsc;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::Mutex;

mod crdt_merge;
mod policy_engine;
mod encryption_engine;
mod api;
mod merge_sync_engine;

#[derive(Clone, Copy, Serialize, Deserialize)]
pub struct Metrics {
    pub active_peers: usize,
    pub avg_latency_ms: u64,
    pub bandwidth_kbps: u64,
    pub load: f32,
}

pub fn compute_tide(m: &Metrics) -> TideLevel {
    if m.active_peers > 7 && m.bandwidth_kbps > 5000 {
        TideLevel::High
    } else if m.active_peers > 3 {
        TideLevel::Normal
    } else {
        TideLevel::Low
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_tide_high() {
        let metrics = Metrics {
            active_peers: 8,
            avg_latency_ms: 10,
            bandwidth_kbps: 6000,
            load: 0.0,
        };
        assert_eq!(compute_tide(&metrics), TideLevel::High);
    }

    #[test]
    fn test_compute_tide_normal() {
        let metrics = Metrics {
            active_peers: 5,
            avg_latency_ms: 50,
            bandwidth_kbps: 3000,
            load: 0.0,
        };
        assert_eq!(compute_tide(&metrics), TideLevel::Normal);
    }

    #[test]
    fn test_compute_tide_low() {
        let metrics = Metrics {
            active_peers: 2,
            avg_latency_ms: 200,
            bandwidth_kbps: 500,
            load: 0.0,
        };
        assert_eq!(compute_tide(&metrics), TideLevel::Low);
    }
}

enum NodeState {
    Offline,
    Syncing,
    Active,
    Degraded,
}

#[tokio::main]
async fn main() {
    let node_id: u64 = std::env::var("NODE_ID").unwrap_or("1".to_string()).parse().unwrap();
    let listen_port: u16 = std::env::var("LISTEN_PORT").unwrap_or("8080".to_string()).parse().unwrap();
    let peers_str = std::env::var("PEERS").unwrap_or("2:8081,3:8082,4:8083,5:8084".to_string());
    let peers: Vec<u64> = peers_str.split(',').map(|s| s.split(':').next().unwrap().parse().unwrap()).collect();

    let mut peer_addresses = HashMap::new();
    for peer in peers_str.split(',') {
        let parts: Vec<&str> = peer.split(':').collect();
        let id: u64 = parts[0].parse().unwrap();
        let port: u16 = parts[1].parse().unwrap();
        peer_addresses.insert(id, format!("127.0.0.1:{}", port));
    }

    // Channels for gossip
    let (digest_tx, digest_rx) = mpsc::channel(100);
    let (request_tx, request_rx) = mpsc::channel(100);
    let (payload_tx, payload_rx) = mpsc::channel(100);

    let transport = TcpTransport::new(peer_addresses.clone(), digest_tx, request_tx, payload_tx, &format!("127.0.0.1:{}", listen_port));

    // Share transport metrics
    let transport_metrics = transport.metrics.clone();

    // Create peer infos
    let peer_infos: Vec<protocol::PeerInfo> = peers.iter().map(|&id| {
        let addr = peer_addresses.get(&id).unwrap().clone();
        protocol::PeerInfo {
            id,
            addr,
            latency_ms: 50, // dummy
            bandwidth_kbps: 10000, // dummy
            load: 0.0, // dummy
            reliability: 1.0, // dummy
        }
    }).collect();

    // Initial metrics and tide
    let mut metrics = Metrics {
        active_peers: peers.len(),
        avg_latency_ms: 50,
        bandwidth_kbps: 10000,
        load: 0.0,
    };
    let tide_level = compute_tide(&metrics);

    // Shared state for API
    let metrics_arc = Arc::new(Mutex::new(metrics.clone()));
    let tide_arc = Arc::new(Mutex::new(tide_level));

    // Merge-Sync Engine
    let merge_sync_arc = Arc::new(Mutex::new(merge_sync_engine::MergeSyncEngine::new(tide_level)));

    let keypair = security::pq_generate_keypair();

    let gossip_engine = Arc::new(Mutex::new(GossipEngine::new(
        node_id,
        peer_infos,
        transport,
        digest_rx,
        request_rx,
        payload_rx,
        tide_level,
        keypair.clone(),
    )));

    // External API channel
    let (external_tx, external_rx) = mpsc::channel(100);

    // API state
    let api_state = api::ApiState {
        node_id,
        metrics: metrics_arc.clone(),
        tide_level: tide_arc.clone(),
        external_tx: external_tx.clone(),
        merge_sync: merge_sync_arc.clone(),
        security_events: Arc::new(Mutex::new(Vec::new())),
    };

    // HTTP API server
    let http_handle = tokio::spawn(async move {
        let app = api::create_router(api_state);
        let listener = tokio::net::TcpListener::bind(format!("0.0.0.0:{}", listen_port + 1000)).await.unwrap(); // API on port + 1000
        axum::serve(listener, app).await.unwrap();
    });

    let mut fast_loop = protocol::FastLoop::new(tide_level, keypair, "node.log");

    let mut state = NodeState::Syncing;

    // Fast loop for gossip
    let gossip_engine_for_task = Arc::clone(&gossip_engine);
    let gossip_handle = tokio::spawn(async move {
        let gossip_engine = Arc::clone(&gossip_engine_for_task);
        loop {
            let mut engine = gossip_engine.lock().await;
            engine.run().await;
            drop(engine);
            tokio::time::sleep(std::time::Duration::from_millis(100)).await;
        }
    });

    // Interface loop for external ops and simulation
    let merge_sync_for_task = merge_sync_arc.clone();
    let interface_handle = tokio::spawn(async move {
        let merge_sync = merge_sync_for_task.clone();
        let mut external_rx = external_rx;
        loop {
            tokio::select! {
                Some(msg) = external_rx.recv() => {
                    // Process external message
                    println!("Processing external message with ops: {:?}", msg.ops);
                    merge_sync.lock().await.apply_message(&msg);
                    // TODO: Send to gossip or process locally
                }
                _ = tokio::time::sleep(std::time::Duration::from_millis(1000)) => {
                    // Simulate incoming message
                    let msg = protocol::Message {
                        ops: vec![1, 2], // S, C
                        payload: vec![1, 2, 3],
                        ttl: 10,
                        clock: 1,
                        sig: vec![],
                        node_id: 1,
                        flags: 0,
                    };
                    println!("Simulating message: {:?}", msg.ops);
                    merge_sync.lock().await.apply_message(&msg);
                    // TODO: Process
                }
            }
        }
    });

    let mut tide_update_counter = 0;

    // State management loop
    loop {
        match state {
            NodeState::Offline => {
                tokio::time::sleep(std::time::Duration::from_millis(1000)).await;
            }
            NodeState::Syncing => {
                // Wait for sync
                tokio::time::sleep(std::time::Duration::from_millis(5000)).await;
                state = NodeState::Active;
            }
            NodeState::Active => {
                // Update metrics and tide every 10 seconds
                tide_update_counter += 1;
                if tide_update_counter % 10 == 0 {
                    // Get real metrics from transport
                    let tm = transport_metrics.lock().await;
                    metrics.active_peers = (metrics.active_peers as i32 + (rand::random::<i32>() % 3 - 1)).max(1) as usize; // still simulate peers
                    metrics.avg_latency_ms = tm.avg_latency_ms;
                    metrics.bandwidth_kbps = tm.bandwidth_kbps;
                    metrics.load = (metrics.load + (rand::random::<f32>() - 0.5) * 0.1).max(0.0).min(1.0); // simulate load
                    let new_tide = compute_tide(&metrics);
                    let mut engine = gossip_engine.lock().await;
                    engine.update_tide(new_tide);
                    drop(engine);
                    *metrics_arc.lock().await = metrics;
                    *tide_arc.lock().await = new_tide;
                    merge_sync_arc.lock().await.update_tide(new_tide);
                    println!("Updated tide to {:?}", new_tide);
                }
                tokio::time::sleep(std::time::Duration::from_millis(1000)).await;
            }
            NodeState::Degraded => {
                tokio::time::sleep(std::time::Duration::from_millis(2000)).await;
            }
        }
    }
}