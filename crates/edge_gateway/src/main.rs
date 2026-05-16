use std::env;
use std::sync::Arc;
use std::time::{Duration, Instant};

use axum::{extract::State, routing::get, Json, Router};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct OceanFabricState {
    active_origin: String,
    fallback_origin: String,
    load: f32,
    latency_ms: u64,
    asi_signal: String,
}

#[derive(Debug, Clone, Serialize)]
struct RouteSnapshot {
    active_origin: String,
    fallback_origin: String,
    ocean_origin: String,
    ocean_asi_signal: String,
    hq_healthy: bool,
    failover_healthy: bool,
    last_probe_latency_ms: Option<u64>,
    last_switch_reason: String,
}

#[derive(Debug, Clone)]
struct RoutingState {
    active_origin: String,
    fallback_origin: String,
    ocean_origin: String,
    ocean_asi_signal: String,
    hq_healthy: bool,
    failover_healthy: bool,
    last_probe_latency_ms: Option<u64>,
    last_switch_reason: String,
}

#[derive(Clone)]
struct AppState {
    state: Arc<RwLock<RoutingState>>,
}

impl RoutingState {
    fn snapshot(&self) -> RouteSnapshot {
        RouteSnapshot {
            active_origin: self.active_origin.clone(),
            fallback_origin: self.fallback_origin.clone(),
            ocean_origin: self.ocean_origin.clone(),
            ocean_asi_signal: self.ocean_asi_signal.clone(),
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
            write.ocean_origin = fabric.active_origin.clone();
            write.fallback_origin = fabric.fallback_origin.clone();
            write.ocean_asi_signal = fabric.asi_signal;
        }
    }
}

async fn run_control_loop(app_state: AppState, hq_origin: String, failover_origin: String, ocean_core_url: String) {
    let client = Client::new();

    loop {
        refresh_from_ocean(&client, &ocean_core_url, &app_state.state).await;

        let (ocean_origin, fallback_origin, asi_signal) = {
            let read = app_state.state.read().await;
            (
                read.ocean_origin.clone(),
                read.fallback_origin.clone(),
                read.ocean_asi_signal.clone(),
            )
        };

        let hq = probe_origin(&client, &hq_origin).await;
        let failover = probe_origin(&client, &failover_origin).await;
        let ocean = probe_origin(&client, &ocean_origin).await;
        let fallback = probe_origin(&client, &fallback_origin).await;

        let mut write = app_state.state.write().await;
        write.hq_healthy = hq.is_some();
        write.failover_healthy = failover.is_some();

        if asi_signal.eq_ignore_ascii_case("reroute") {
            if fallback.is_some() {
                write.active_origin = fallback_origin;
                write.last_probe_latency_ms = fallback;
                write.last_switch_reason = "ocean_asi_reroute".to_string();
            }
        } else if ocean.is_some() {
            write.active_origin = ocean_origin;
            write.last_probe_latency_ms = ocean;
            write.last_switch_reason = "ocean_preferred_healthy".to_string();
        } else if hq.is_some() {
            write.active_origin = hq_origin.clone();
            write.last_probe_latency_ms = hq;
            write.last_switch_reason = "hq_healthy".to_string();
        } else if failover.is_some() {
            write.active_origin = failover_origin.clone();
            write.last_probe_latency_ms = failover;
            write.last_switch_reason = "hq_down_failover".to_string();
        } else if fallback.is_some() {
            write.active_origin = fallback_origin;
            write.last_probe_latency_ms = fallback;
            write.last_switch_reason = "fallback_healthy".to_string();
        } else {
            write.last_probe_latency_ms = None;
            write.last_switch_reason = "no_healthy_origin".to_string();
        }

        tokio::time::sleep(Duration::from_secs(2)).await;
    }
}

async fn health() -> &'static str {
    "edge_gateway: ok"
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
        ocean_origin: hq_origin.clone(),
        ocean_asi_signal: "stable".to_string(),
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
        .with_state(app_state);

    let listener = TcpListener::bind("0.0.0.0:7000").await.unwrap();
    println!("edge_gateway running on 0.0.0.0:7000");
    axum::serve(listener, app).await.unwrap();
}
