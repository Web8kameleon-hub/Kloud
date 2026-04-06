use axum::response::Html;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use protocol::{Message, TideLevel};
use crate::{Metrics, compute_tide};

#[derive(Clone)]
pub struct ApiState {
    pub metrics: Arc<Mutex<Metrics>>,
    pub tide_level: Arc<Mutex<TideLevel>>,
    pub external_tx: tokio::sync::mpsc::Sender<Message>,
    pub merge_sync: Arc<Mutex<super::merge_sync_engine::MergeSyncEngine>>,
}

#[derive(Deserialize)]
pub struct SubmitRequest {
    pub ops: Vec<String>, // e.g., ["S", "C"]
    pub payload: String,  // base64 encoded
    pub ttl: Option<u64>,
}

#[derive(Serialize)]
pub struct StatusResponse {
    pub state: String, // "Active", etc.
    pub tide: String,
    pub metrics: Metrics,
}

#[derive(Serialize)]
pub struct StateResponse {
    pub state: std::collections::HashMap<String, String>, // key -> base64 value
}

pub fn create_router(state: ApiState) -> Router {
    Router::new()
        .route("/submit", post(submit_op))
        .route("/status", get(get_status))
        .route("/peers", get(get_peers))
        .route("/state", get(get_state))
        .route("/dashboard", get(get_dashboard))
        .with_state(state)
}

async fn submit_op(
    State(state): State<ApiState>,
    Json(req): Json<SubmitRequest>,
) -> Json<serde_json::Value> {
    // Map string ops to u8
    let ops: Vec<u8> = req.ops.iter().filter_map(|op| match op.as_str() {
        "S" => Some(1),
        "C" => Some(2),
        "R" => Some(3),
        "E" => Some(4),
        "P" => Some(5),
        "M" => Some(6),
        "F" => Some(7),
        "J" => Some(8),
        "L" => Some(9),
        "D" => Some(10),
        "T" => Some(11),
        "X" => Some(12),
        _ => None,
    }).collect();

    if ops.is_empty() {
        return Json(serde_json::json!({"error": "Invalid ops"}));
    }

    // Decode payload
    let payload = match base64::decode(&req.payload) {
        Ok(p) => p,
        Err(_) => return Json(serde_json::json!({"error": "Invalid payload base64"})),
    };

    let msg = Message {
        ops,
        payload,
        ttl: req.ttl.unwrap_or(10),
        clock: 0, // TODO: real clock
        sig: vec![], // TODO: sign
        node_id: 1, // TODO: real node_id
        flags: 0,
    };

    // Send to external channel
    if let Err(_) = state.external_tx.send(msg).await {
        return Json(serde_json::json!({"error": "Failed to submit"}));
    }

    Json(serde_json::json!({"status": "submitted"}))
}

async fn get_status(
    State(state): State<ApiState>,
) -> Json<StatusResponse> {
    let metrics = *state.metrics.lock().await;
    let tide = *state.tide_level.lock().await;
    Json(StatusResponse {
        state: "Active".to_string(), // TODO: real state
        tide: format!("{:?}", tide),
        metrics,
    })
}

async fn get_dashboard(
    State(state): State<ApiState>,
) -> Html<String> {
    let metrics = state.metrics.lock().await.clone();
    let tide = *state.tide_level.lock().await;
    let state_map = state.merge_sync.lock().await.get_state().clone();

    let mut state_html = String::new();
    for (k, v) in &state_map {
        state_html.push_str(&format!("<li>{}: {}</li>", k, base64::encode(v)));
    }

    let html = format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nanogrid Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .tide {{ color: {}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Nanogrid Sovereign Fabric Dashboard</h1>
            <div class="metric">
                <h2>Status</h2>
                <p>State: Active</p>
                <p>Tide: <span class="tide">{:?}</span></p>
            </div>
            <div class="metric">
                <h2>Metrics</h2>
                <p>Active Peers: {}</p>
                <p>Avg Latency: {} ms</p>
                <p>Bandwidth: {} kbps</p>
                <p>Load: {:.2}</p>
            </div>
            <div class="metric">
                <h2>Local State</h2>
                <ul>{}</ul>
            </div>
        </body>
        </html>
        "#,
        match tide {
            protocol::TideLevel::High => "green",
            protocol::TideLevel::Normal => "orange",
            protocol::TideLevel::Low => "red",
        },
        tide,
        metrics.active_peers,
        metrics.avg_latency_ms,
        metrics.bandwidth_kbps,
        metrics.load,
        state_html
    );

    Html(html)
}