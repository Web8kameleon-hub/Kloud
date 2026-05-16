use std::collections::HashMap;
use std::sync::Arc;

use axum::{extract::State, routing::{get, post}, Json, Router};
use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct FabricState {
    active_origin: String,
    fallback_origin: String,
    load: f32,
    latency_ms: u64,
    asi_signal: String,
}

#[derive(Debug, Clone, Deserialize)]
struct TelemetryPayload {
    node: String,
    cpu: f32,
    latency: u64,
    bti: f32,
    pfd: f32,
}

#[derive(Debug, Clone, Deserialize)]
struct AsiSignalPayload {
    signal: String,
    reason: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
struct ApiResult {
    ok: bool,
    message: String,
}

#[derive(Clone)]
struct AppState {
    fabric: Arc<RwLock<FabricState>>,
    latest_telemetry: Arc<RwLock<HashMap<String, TelemetryPayload>>>,
}

async fn health() -> &'static str {
    "ocean_core: ok"
}

async fn get_fabric_state(State(app_state): State<AppState>) -> Json<FabricState> {
    Json(app_state.fabric.read().await.clone())
}

async fn ingest_telemetry(
    State(app_state): State<AppState>,
    Json(payload): Json<TelemetryPayload>,
) -> Json<ApiResult> {
    {
        let mut telemetry = app_state.latest_telemetry.write().await;
        telemetry.insert(payload.node.clone(), payload.clone());
    }

    {
        let mut state = app_state.fabric.write().await;
        state.load = payload.cpu;
        state.latency_ms = payload.latency;

        if payload.pfd >= 0.80 {
            state.asi_signal = "reroute".to_string();
            state.active_origin = state.fallback_origin.clone();
        } else if payload.bti >= 0.70 {
            state.asi_signal = "stable".to_string();
            state.active_origin = "http://10.10.0.1:8000".to_string();
        }
    }

    Json(ApiResult {
        ok: true,
        message: "telemetry_processed".to_string(),
    })
}

async fn ingest_asi_signal(
    State(app_state): State<AppState>,
    Json(payload): Json<AsiSignalPayload>,
) -> Json<ApiResult> {
    let mut state = app_state.fabric.write().await;
    state.asi_signal = payload.signal.clone();

    if payload.signal.eq_ignore_ascii_case("reroute") {
        state.active_origin = state.fallback_origin.clone();
    } else if payload.signal.eq_ignore_ascii_case("stable") {
        state.active_origin = "http://10.10.0.1:8000".to_string();
    }

    let reason = payload.reason.unwrap_or_else(|| "none".to_string());
    Json(ApiResult {
        ok: true,
        message: format!("asi_signal_applied:{reason}"),
    })
}

#[tokio::main]
async fn main() {
    let app_state = AppState {
        fabric: Arc::new(RwLock::new(FabricState {
            active_origin: "http://10.10.0.1:8000".to_string(),
            fallback_origin: "http://10.10.0.3:8000".to_string(),
            load: 0.1,
            latency_ms: 12,
            asi_signal: "stable".to_string(),
        })),
        latest_telemetry: Arc::new(RwLock::new(HashMap::new())),
    };

    let app = Router::new()
        .route("/health", get(health))
        .route("/fabric/state", get(get_fabric_state))
        .route("/telemetry", post(ingest_telemetry))
        .route("/asi/signal", post(ingest_asi_signal))
        .with_state(app_state);

    let listener = TcpListener::bind("0.0.0.0:9000").await.unwrap();
    println!("ocean_core running on 0.0.0.0:9000");
    axum::serve(listener, app).await.unwrap();
}
