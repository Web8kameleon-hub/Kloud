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
    compute_origin: String,
    load: f32,
    latency_ms: u64,
    harmony: f32,
    asi_signal: String,
    anomalies: Vec<String>,
    decision_explanation: String,
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
    preferred_origin: Option<String>,
    fallback_origin: Option<String>,
    compute_origin: Option<String>,
    harmony: Option<f32>,
    anomalies: Option<Vec<String>>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct MeshNodeRegistration {
    node_id: String,
    role: String,
    region: String,
    public_ip: String,
    mesh_ip: String,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
struct MeshNodeStatus {
    node_id: String,
    cpu: f32,
    memory: f32,
    latency_ms: u64,
    bti: Option<f32>,
    das: Option<f32>,
    pfd: Option<f32>,
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
    mesh_registry: Arc<RwLock<HashMap<String, MeshNodeRegistration>>>,
    mesh_status: Arc<RwLock<HashMap<String, MeshNodeStatus>>>,
}

async fn health() -> &'static str {
    "ocean_core: ok"
}

async fn get_fabric_state(State(app_state): State<AppState>) -> Json<FabricState> {
    Json(app_state.fabric.read().await.clone())
}

async fn get_fabric_explain(State(app_state): State<AppState>) -> Json<ApiResult> {
    let state = app_state.fabric.read().await;
    Json(ApiResult {
        ok: true,
        message: format!(
            "active_origin={} signal={} harmony={} reason={}",
            state.active_origin, state.asi_signal, state.harmony, state.decision_explanation
        ),
    })
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
        state.harmony = (payload.bti * 100.0).clamp(0.0, 100.0);

        if payload.pfd >= 0.80 {
            state.asi_signal = "reroute".to_string();
            state.active_origin = state.fallback_origin.clone();
            state.decision_explanation = "telemetry_pfd_high".to_string();
        } else if payload.bti >= 0.70 {
            state.asi_signal = "stable".to_string();
            state.active_origin = "http://10.10.0.1:8000".to_string();
            state.decision_explanation = "telemetry_bti_stable".to_string();
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

    if let Some(preferred) = payload.preferred_origin {
        state.active_origin = preferred;
    }

    if let Some(fallback) = payload.fallback_origin {
        state.fallback_origin = fallback;
    }

    if let Some(compute) = payload.compute_origin {
        state.compute_origin = compute;
    }

    if let Some(harmony) = payload.harmony {
        state.harmony = harmony.clamp(0.0, 100.0);
    }

    if let Some(anomalies) = payload.anomalies {
        state.anomalies = anomalies;
    }

    if payload.signal.eq_ignore_ascii_case("reroute") {
        state.active_origin = state.fallback_origin.clone();
        state.decision_explanation = payload.reason.clone().unwrap_or_else(|| "asi_reroute".to_string());
    } else if payload.signal.eq_ignore_ascii_case("compute_overload") {
        state.decision_explanation = payload.reason.clone().unwrap_or_else(|| "compute_overload".to_string());
    } else if payload.signal.eq_ignore_ascii_case("stable") {
        state.active_origin = "http://10.10.0.1:8000".to_string();
        state.decision_explanation = payload.reason.clone().unwrap_or_else(|| "asi_stable".to_string());
    }

    let reason = payload.reason.unwrap_or_else(|| "none".to_string());
    Json(ApiResult {
        ok: true,
        message: format!("asi_signal_applied:{reason}"),
    })
}

async fn mesh_register(
    State(app_state): State<AppState>,
    Json(payload): Json<MeshNodeRegistration>,
) -> Json<ApiResult> {
    let mut write = app_state.mesh_registry.write().await;
    write.insert(payload.node_id.clone(), payload);
    Json(ApiResult {
        ok: true,
        message: "mesh_registered".to_string(),
    })
}

async fn mesh_status(
    State(app_state): State<AppState>,
    Json(payload): Json<MeshNodeStatus>,
) -> Json<ApiResult> {
    let mut write = app_state.mesh_status.write().await;
    write.insert(payload.node_id.clone(), payload);
    Json(ApiResult {
        ok: true,
        message: "mesh_status_ingested".to_string(),
    })
}

#[tokio::main]
async fn main() {
    let app_state = AppState {
        fabric: Arc::new(RwLock::new(FabricState {
            active_origin: "http://10.10.0.1:8000".to_string(),
            fallback_origin: "http://10.10.0.3:8000".to_string(),
            compute_origin: "http://10.10.0.2:8000".to_string(),
            load: 0.1,
            latency_ms: 12,
            harmony: 90.0,
            asi_signal: "stable".to_string(),
            anomalies: Vec::new(),
            decision_explanation: "initial_boot".to_string(),
        })),
        latest_telemetry: Arc::new(RwLock::new(HashMap::new())),
        mesh_registry: Arc::new(RwLock::new(HashMap::new())),
        mesh_status: Arc::new(RwLock::new(HashMap::new())),
    };

    let app = Router::new()
        .route("/health", get(health))
        .route("/fabric/state", get(get_fabric_state))
        .route("/fabric/explain", get(get_fabric_explain))
        .route("/telemetry", post(ingest_telemetry))
        .route("/asi/signal", post(ingest_asi_signal))
        .route("/mesh/register", post(mesh_register))
        .route("/mesh/status", post(mesh_status))
        .with_state(app_state);

    let listener = TcpListener::bind("0.0.0.0:9000").await.unwrap();
    println!("ocean_core running on 0.0.0.0:9000");
    axum::serve(listener, app).await.unwrap();
}
