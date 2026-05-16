use std::env;
use std::sync::Arc;
use std::time::{Duration, Instant};

use axum::{extract::State, routing::get, Json, Router, response::IntoResponse, body::Body};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct OceanFabricState {
    active_origin: String,
    fallback_origin: String,
    compute_origin: String,
    preferred_origin: String,
    load: f32,
    latency_ms: u64,
    harmony: f32,
    asi_signal: String,
    anomalies: Vec<String>,
    patterns: Vec<String>,
    gaps: Vec<String>,
    risks: Vec<String>,
    predictions: Vec<String>,
    decision_explanation: String,
    updated_at: String,
}

#[derive(Debug, Clone, Serialize)]
struct RouteSnapshot {
    active_origin: String,
    fallback_origin: String,
    compute_origin: String,
    ocean_origin: String,
    ocean_asi_signal: String,
    ocean_harmony: f32,
    anomaly_count: usize,
    hq_healthy: bool,
    failover_healthy: bool,
    last_probe_latency_ms: Option<u64>,
    last_switch_reason: String,
}

#[derive(Debug, Clone)]
struct RoutingState {
    active_origin: String,
    fallback_origin: String,
    compute_origin: String,
    preferred_origin: String,
    ocean_origin: String,
    ocean_asi_signal: String,
    ocean_harmony: f32,
    anomaly_count: usize,
    hq_healthy: bool,
    failover_healthy: bool,
    last_probe_latency_ms: Option<u64>,
    last_switch_reason: String,
}

#[derive(Clone)]
struct AppState {
    state: Arc<RwLock<RoutingState>>,
}

// ─── firewall intelligence ─────────────────────────────────────────────────

#[derive(Debug, Clone)]
pub enum FirewallAction {
    Block(String),           // req: FORBIDDEN
    RateLimit(String),       // req: TOO_MANY_REQUESTS
    Redirect(String),        // req: redirect to origin
}

/// Check request against FabricState anomalies & signals
async fn apply_firewall_rules(
    req_path: &str,
    req_size: usize,
    state: &RoutingState,
) -> Result<(), FirewallAction> {
    // 1) ALBA anomalies → block suspicious patterns
    if state.anomalies.iter().any(|a| a.contains("trinity_anomaly")) {
        if req_size > 50_000 || req_path.contains("admin") {
            return Err(FirewallAction::Block("trinity anomaly detected".into()));
        }
    }

    // 2) ALBI pattern detection → rate limit high-frequency
    if state.anomalies.iter().any(|a| a.contains("mali_pattern")) {
        if req_path.starts_with("/api/v1") && req_size < 100 {
            return Err(FirewallAction::RateLimit("mali pattern detected".into()));
        }
    }

    // 3) BLERINA gap detection → redirect sensitive routes
    if state.anomalies.iter().any(|a| a.contains("gap:")) {
        if req_path.contains("config") || req_path.contains("credential") {
            return Err(FirewallAction::Redirect(state.fallback_origin.clone()));
        }
    }

    // 4) LIAM tensor spike → block large payloads
    if state.anomalies.iter().any(|a| a.contains("liam_eigen_spike")) {
        if req_size > 100_000 {
            return Err(FirewallAction::Block("tensor spike: payload too large".into()));
        }
    }

    // 5) ALDA compute overload → redirect heavy compute
    if state.ocean_asi_signal == "compute_overload" {
        if req_path.contains("analyze") || req_path.contains("compute") {
            return Err(FirewallAction::Redirect(state.compute_origin.clone()));
        }
    }

    // 6) KLAJDI risk detection → block unknown sources
    if state.anomalies.iter().any(|a| a.contains("klajdi_risk")) {
        if !req_path.starts_with("/health") && req_size == 0 {
            return Err(FirewallAction::Block("klajdi risk: empty payload".into()));
        }
    }

    // 7) Degraded harmony → activate protection
    if state.ocean_harmony < 40.0 {
        if req_size > 10_000 {
            return Err(FirewallAction::RateLimit("fabric degraded: high load".into()));
        }
    }

    Ok(())
}

// ─────────────────────────────────────────────────────────────────────────────

impl RoutingState {
    fn snapshot(&self) -> RouteSnapshot {
        RouteSnapshot {
            active_origin: self.active_origin.clone(),
            fallback_origin: self.fallback_origin.clone(),
            compute_origin: self.compute_origin.clone(),
            ocean_origin: self.ocean_origin.clone(),
            ocean_asi_signal: self.ocean_asi_signal.clone(),
            ocean_harmony: self.ocean_harmony,
            anomaly_count: self.anomaly_count,
            hq_healthy: self.hq_healthy,
            failover_healthy: self.failover_healthy,
            last_probe_latency_ms: self.last_probe_latency_ms,
            last_switch_reason: self.last_switch_reason.clone(),
        }
    }
}

async fn probe_origin(client: &Client, origin: &str) -> Option<u64> {
    let start = Instant::now();
    let response = client
        .get(format!("{origin}/health"))
        .timeout(Duration::from_millis(500))
        .send()
        .await
        .ok()?;

    if !response.status().is_success() {
        return None;
    }

    Some(start.elapsed().as_millis() as u64)
}

async fn refresh_from_ocean(client: &Client, ocean_core_url: &str, state: &Arc<RwLock<RoutingState>>) {
    let endpoint = format!("{ocean_core_url}/fabric/state");
    if let Ok(resp) = client
        .get(endpoint)
        .timeout(Duration::from_millis(700))
        .send()
        .await
    {
        if let Ok(fabric) = resp.json::<OceanFabricState>().await {
            let mut write = state.write().await;
            write.ocean_origin     = fabric.active_origin.clone();
            write.fallback_origin  = fabric.fallback_origin.clone();
            write.compute_origin   = fabric.compute_origin.clone();
            write.preferred_origin = fabric.preferred_origin.clone();
            write.ocean_asi_signal = fabric.asi_signal.clone();
            write.ocean_harmony    = fabric.harmony;
            write.anomaly_count    = fabric.anomalies.len();
        }
    }
}

async fn run_control_loop(app_state: AppState, hq_origin: String, failover_origin: String, ocean_core_url: String) {
    let client = Client::new();

    loop {
        refresh_from_ocean(&client, &ocean_core_url, &app_state.state).await;

        let (asi_signal, compute_origin, fallback_origin, preferred_origin, anomaly_count, harmony) = {
            let r = app_state.state.read().await;
            (
                r.ocean_asi_signal.clone(),
                r.compute_origin.clone(),
                r.fallback_origin.clone(),
                r.preferred_origin.clone(),
                r.anomaly_count,
                r.ocean_harmony,
            )
        };

        let hq       = probe_origin(&client, &hq_origin).await;
        let failover = probe_origin(&client, &failover_origin).await;
        let compute  = probe_origin(&client, &compute_origin).await;

        let mut write = app_state.state.write().await;
        write.hq_healthy      = hq.is_some();
        write.failover_healthy = failover.is_some();

        // ─── Stigma-driven routing decisions ────────────────────────────────
        let (new_origin, reason) = match asi_signal.as_str() {
            "reroute" => {
                // BLERINA gap crítikal | KLAJDI anomali | ASI reroute
                if failover.is_some() {
                    (failover_origin.clone(), "stigma_reroute_fallback")
                } else if hq.is_some() {
                    (hq_origin.clone(), "stigma_reroute_hq_fallback")
                } else {
                    (fallback_origin.clone(), "stigma_reroute_static")
                }
            }
            "compute_overload" | "scale_up" => {
                // MALI prediction rising | ALDA batch overload
                if compute.is_some() {
                    (compute_origin.clone(), "stigma_compute_offload")
                } else if hq.is_some() {
                    (hq_origin.clone(), "stigma_compute_hq_fallback")
                } else {
                    (fallback_origin.clone(), "stigma_compute_no_node")
                }
            }
            "optimize" => {
                // LIAM tensor spike → steer to preferred if healthy
                if hq.is_some() {
                    (preferred_origin.clone(), "stigma_optimize_preferred")
                } else if compute.is_some() {
                    (compute_origin.clone(), "stigma_optimize_compute")
                } else {
                    (fallback_origin.clone(), "stigma_optimize_fallback")
                }
            }
            _ => {
                // stable — select healthiest with harmony guard
                if harmony < 40.0 || anomaly_count > 10 {
                    // degraded state — prefer fallback
                    if failover.is_some() {
                        (failover_origin.clone(), "harmony_degraded_fallback")
                    } else if hq.is_some() {
                        (hq_origin.clone(), "harmony_degraded_hq")
                    } else {
                        (fallback_origin.clone(), "harmony_degraded_static")
                    }
                } else if hq.is_some() {
                    (hq_origin.clone(), "stable_hq_preferred")
                } else if failover.is_some() {
                    (failover_origin.clone(), "stable_hq_down_failover")
                } else {
                    (fallback_origin.clone(), "stable_all_down_static")
                }
            }
        };

        write.active_origin          = new_origin;
        write.last_switch_reason     = reason.to_string();
        write.last_probe_latency_ms  = hq.or(failover).or(compute);

        drop(write);
        tokio::time::sleep(Duration::from_millis(150)).await;
    }
}

async fn health() -> &'static str {
    "edge_gateway: ok"
}

async fn gateway(
    State(app_state): State<AppState>,
    axum::http::Uri(uri): axum::http::Uri,
    req_body: axum::body::Body,
) -> axum::response::Response {
    let read = app_state.state.read().await;
    let route_state = read.clone();
    drop(read);

    let req_path = uri.path();
    let body_size = 0; // axum doesn't expose body size easily — use 0 as default

    // Apply firewall rules
    if let Err(action) = apply_firewall_rules(req_path, body_size, &route_state).await {
        return match action {
            FirewallAction::Block(reason) => {
                (
                    axum::http::StatusCode::FORBIDDEN,
                    format!("Blocked: {}", reason),
                )
                    .into_response()
            }
            FirewallAction::RateLimit(reason) => {
                (
                    axum::http::StatusCode::TOO_MANY_REQUESTS,
                    format!("Rate limited: {}", reason),
                )
                    .into_response()
            }
            FirewallAction::Redirect(origin) => {
                let target_uri = format!("{}{}", origin, uri);
                let client = Client::new();
                match client.get(&target_uri).send().await {
                    Ok(resp) => {
                        let status = resp.status();
                        match resp.text().await {
                            Ok(body) => (status, body).into_response(),
                            Err(_) => (status, "").into_response(),
                        }
                    }
                    Err(_) => (
                        axum::http::StatusCode::BAD_GATEWAY,
                        "Redirect origin unavailable",
                    )
                        .into_response(),
                }
            }
        };
    }

    // Firewall passed → proxy to active origin
    let active_origin = route_state.active_origin.clone();
    let target_uri = format!("{}{}", active_origin, uri);

    let client = Client::new();
    match client.get(&target_uri).send().await {
        Ok(resp) => {
            let status = resp.status();
            match resp.text().await {
                Ok(body) => (status, body).into_response(),
                Err(_) => (status, "").into_response(),
            }
        }
        Err(_) => (
            axum::http::StatusCode::BAD_GATEWAY,
            "Active origin unreachable",
        )
            .into_response(),
    }
}

async fn route(State(app_state): State<AppState>) -> Json<RouteSnapshot> {
    let read = app_state.state.read().await;
    Json(read.snapshot())
}

#[tokio::main]
async fn main() {
    let hq_origin = env::var("HQ_ORIGIN").unwrap_or_else(|_| "http://10.10.0.1:8000".to_string());
    let failover_origin =
        env::var("FAILOVER_ORIGIN").unwrap_or_else(|_| "http://10.10.0.3:8000".to_string());
    let ocean_core_url = env::var("OCEAN_CORE_URL").unwrap_or_else(|_| "http://10.10.0.1:9000".to_string());

    let state = Arc::new(RwLock::new(RoutingState {
        active_origin: hq_origin.clone(),
        fallback_origin: failover_origin.clone(),
        compute_origin: env::var("COMPUTE_ORIGIN").unwrap_or_else(|_| "http://10.10.0.2:8000".to_string()),
        preferred_origin: hq_origin.clone(),
        ocean_origin: hq_origin.clone(),
        ocean_asi_signal: "stable".to_string(),
        ocean_harmony: 90.0,
        anomaly_count: 0,
        hq_healthy: false,
        failover_healthy: false,
        last_probe_latency_ms: None,
        last_switch_reason: "boot".to_string(),
    }));

    let app_state = AppState { state };
    tokio::spawn(run_control_loop(
        app_state.clone(),
        hq_origin,
        failover_origin,
        ocean_core_url,
    ));

    let app = Router::new()
        .route("/health", get(health))
        .route("/route", get(route))
        .fallback(gateway)
        .with_state(app_state);

    let listener = TcpListener::bind("0.0.0.0:7000").await.unwrap();
    println!("edge_gateway running on 0.0.0.0:7000");
    axum::serve(listener, app).await.unwrap();
}
