use protocol::*;
use reqwest;
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
    let mesh_healthcheck_interval_ms: u64 = std::env::var("MESH_HEALTHCHECK_INTERVAL_MS")
        .unwrap_or("600000".to_string())
        .parse()
        .unwrap_or(600000);
    let mesh_healthcheck_timeout_ms: u64 = std::env::var("MESH_HEALTHCHECK_TIMEOUT_MS")
        .unwrap_or("1200".to_string())
        .parse()
        .unwrap_or(1200);
    let peers_str = std::env::var("PEERS").unwrap_or("".to_string());

    // Parse PEERS: supports "id:host:gossip_port" (remote) or "id:gossip_port" (local 127.0.0.1)
    let mut peer_addresses = HashMap::new();   // id -> gossip addr (host:port)
    let mut peer_api_addrs = HashMap::new();   // id -> HTTP API base URL
    let mut peers: Vec<u64> = Vec::new();

    if !peers_str.is_empty() {
        for seg in peers_str.split(',') {
            let parts: Vec<&str> = seg.trim().split(':').collect();
            match parts.len() {
                3 => {
                    // id:host:gossip_port
                    if let (Ok(id), Ok(gossip_port)) = (parts[0].parse::<u64>(), parts[2].parse::<u16>()) {
                        let host = parts[1];
                        let api_port = gossip_port + 1000;
                        peer_addresses.insert(id, format!("{}:{}", host, gossip_port));
                        peer_api_addrs.insert(id, format!("http://{}:{}", host, api_port));
                        peers.push(id);
                    }
                }
                2 => {
                    // id:gossip_port (local)
                    if let (Ok(id), Ok(port)) = (parts[0].parse::<u64>(), parts[1].parse::<u16>()) {
                        peer_addresses.insert(id, format!("127.0.0.1:{}", port));
                        peer_api_addrs.insert(id, format!("http://127.0.0.1:{}", port + 1000));
                        peers.push(id);
                    }
                }
                _ => {}
            }
        }
    }

    // Channels for gossip
    let (digest_tx, digest_rx) = mpsc::channel(100);
    let (request_tx, request_rx) = mpsc::channel(100);
    let (payload_tx, payload_rx) = mpsc::channel(100);

    let transport = TcpTransport::new(peer_addresses.clone(), digest_tx, request_tx, payload_tx, &format!("0.0.0.0:{}", listen_port));

    // Share transport metrics
    let transport_metrics = transport.metrics.clone();

    // Create peer infos
    let initial_tm = transport_metrics.lock().await.clone();

    let peer_infos: Vec<protocol::PeerInfo> = peers.iter().map(|&id| {
        let addr = peer_addresses.get(&id).cloned().unwrap_or_default();
        protocol::PeerInfo {
            id,
            addr,
            latency_ms: initial_tm.avg_latency_ms,
            bandwidth_kbps: initial_tm.bandwidth_kbps,
            load: 0.0,
            reliability: 1.0,
        }
    }).collect();

    // Initial metrics and tide
    let mut metrics = Metrics {
        active_peers: initial_tm.active_connections,
        avg_latency_ms: initial_tm.avg_latency_ms,
        bandwidth_kbps: initial_tm.bandwidth_kbps,
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

    // Build initial peers_map from parsed peer_api_addrs
    let peers_map: Arc<Mutex<HashMap<u64, api::PeerRecord>>> = Arc::new(Mutex::new(
        peer_api_addrs.iter().map(|(&id, api_addr)| {
            let gossip_addr = peer_addresses.get(&id).cloned().unwrap_or_default();
            (id, api::PeerRecord {
                id,
                api_addr: api_addr.clone(),
                gossip_addr,
                state: "Unknown".to_string(),
                tide: "Unknown".to_string(),
                last_seen_ms: 0,
                latency_ms: 0,
                reachable: false,
            })
        }).collect()
    ));

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
        peers_map: peers_map.clone(),
    };

    // Background mesh peer health-check (ping every 15s)
    {
        let peers_map_hc = peers_map.clone();
        let metrics_arc_hc = metrics_arc.clone();
        let healthcheck_interval_ms = mesh_healthcheck_interval_ms;
        let healthcheck_timeout_ms = mesh_healthcheck_timeout_ms;
        tokio::spawn(async move {
            let client = reqwest::Client::builder()
                .timeout(std::time::Duration::from_millis(healthcheck_timeout_ms))
                .build()
                .unwrap();
            loop {
                let entries: Vec<(u64, String)> = {
                    let pm = peers_map_hc.lock().await;
                    pm.iter().map(|(&id, p)| (id, p.api_addr.clone())).collect()
                };
                let mut reachable_count = 0usize;
                let mut total_latency = 0u64;
                for (id, base_url) in &entries {
                    let url = format!("{}/status?stigma_level=2", base_url);
                    let start = std::time::Instant::now();
                    match client.get(&url).send().await {
                        Ok(resp) if resp.status().is_success() => {
                            let latency_ms = start.elapsed().as_millis() as u64;
                            reachable_count += 1;
                            total_latency += latency_ms;
                            if let Ok(body) = resp.json::<serde_json::Value>().await {
                                let now_ms = std::time::SystemTime::now()
                                    .duration_since(std::time::UNIX_EPOCH)
                                    .unwrap_or_default()
                                    .as_millis();
                                let mut pm = peers_map_hc.lock().await;
                                if let Some(peer) = pm.get_mut(id) {
                                    peer.reachable = true;
                                    peer.latency_ms = latency_ms;
                                    peer.last_seen_ms = now_ms;
                                    peer.state = body.get("state").and_then(|v| v.as_str()).unwrap_or("Unknown").to_string();
                                    peer.tide = body.get("tide").and_then(|v| v.as_str()).unwrap_or("Unknown").to_string();
                                }
                            }
                        }
                        _ => {
                            let mut pm = peers_map_hc.lock().await;
                            if let Some(peer) = pm.get_mut(id) {
                                peer.reachable = false;
                            }
                        }
                    }
                }
                // Push real active_peers count to metrics
                {
                    let mut m = metrics_arc_hc.lock().await;
                    m.active_peers = reachable_count;
                    if reachable_count > 0 {
                        m.avg_latency_ms = total_latency / reachable_count as u64;
                    }
                }
                tokio::time::sleep(std::time::Duration::from_millis(healthcheck_interval_ms)).await;
            }
        });
    }

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
                _ = tokio::time::sleep(std::time::Duration::from_millis(1000)) => {}
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
                    let mesh_active_peers = {
                        let current_metrics = metrics_arc.lock().await;
                        current_metrics.active_peers
                    };
                    // Keep the larger signal between mesh reachability and gossip connections.
                    metrics.active_peers = std::cmp::max(mesh_active_peers, tm.active_connections);
                    metrics.avg_latency_ms = tm.avg_latency_ms;
                    metrics.bandwidth_kbps = tm.bandwidth_kbps;
                    metrics.load = (((tm.avg_latency_ms as f32) / 250.0).min(1.0)
                        + ((tm.bandwidth_kbps as f32) / 10000.0).min(1.0)) / 2.0;
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