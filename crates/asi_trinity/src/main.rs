use std::env;
use std::sync::Arc;
use std::time::Duration;

use axum::{extract::State, routing::get, Json, Router};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::net::TcpListener;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize)]
struct TrinitySnapshot {
    alba_ok: bool,
    albi_ok: bool,
    jona_ok: bool,
    asi_ok: bool,
    cpu: f32,
    harmony: f32,
    anomaly_score: f32,
    decision: String,
    decision_reason: String,
}

#[derive(Debug, Clone, Serialize)]
struct DecisionPayload {
    signal: String,
    reason: String,
    preferred_origin: String,
    fallback_origin: String,
    compute_origin: String,
    harmony: f32,
    anomalies: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct HealthResponse {
    status: String,
}

#[derive(Clone)]
struct AppState {
    snapshot: Arc<RwLock<TrinitySnapshot>>,
}

fn get_env(name: &str, default_value: &str) -> String {
    env::var(name).unwrap_or_else(|_| default_value.to_string())
}

fn read_numeric(v: &Value, candidates: &[&str]) -> Option<f32> {
    for key in candidates {
        if let Some(value) = v.get(*key) {
            if let Some(n) = value.as_f64() {
                return Some(n as f32);
            }
            if let Some(s) = value.as_str() {
                if let Ok(parsed) = s.parse::<f32>() {
                    return Some(parsed);
                }
            }
        }
    }
    None
}

fn read_vec_string(v: &Value, key: &str) -> Vec<String> {
    v.get(key)
        .and_then(Value::as_array)
        .map(|arr| {
            arr.iter()
                .filter_map(|item| item.as_str().map(ToString::to_string))
                .collect::<Vec<_>>()
        })
        .unwrap_or_default()
}

async fn get_first_json(client: &Client, base: &str, paths: &[&str]) -> Option<Value> {
    for path in paths {
        let url = format!("{base}{path}");
        if let Ok(resp) = client.get(url).timeout(Duration::from_millis(1200)).send().await {
            if resp.status().is_success() {
                if let Ok(json) = resp.json::<Value>().await {
                    return Some(json);
                }
            }
        }
    }
    None
}

fn derive_decision(cpu: f32, harmony: f32, anomaly_score: f32) -> (String, String) {
    if harmony < 65.0 || anomaly_score >= 0.80 {
        return ("reroute".to_string(), "harmony_low_or_anomaly_high".to_string());
    }
    if cpu >= 0.85 {
        return ("compute_overload".to_string(), "compute_cpu_high".to_string());
    }
    ("stable".to_string(), "signals_stable".to_string())
}

async fn publish_decision(client: &Client, ocean_url: &str, payload: &DecisionPayload) {
    let _ = client
        .post(format!("{ocean_url}/asi/signal"))
        .json(payload)
        .timeout(Duration::from_millis(1200))
        .send()
        .await;
}

async fn run_orchestrator_loop(app_state: AppState, trinity_base_url: String, ocean_core_url: String) {
    let client = Client::new();

    let alba_paths = ["/api/asi/alba/metrics", "/asi/alba/metrics", "/alba/latest"];
    let albi_paths = ["/api/asi/albi/metrics", "/asi/albi/metrics", "/api/albi/eeg/quality"];
    let jona_paths = ["/api/asi/jona/metrics", "/asi/jona/metrics", "/api/jona/status"];
    let asi_paths = ["/api/asi/status", "/asi/status"];

    loop {
        let alba = get_first_json(&client, &trinity_base_url, &alba_paths).await;
        let albi = get_first_json(&client, &trinity_base_url, &albi_paths).await;
        let jona = get_first_json(&client, &trinity_base_url, &jona_paths).await;
        let asi = get_first_json(&client, &trinity_base_url, &asi_paths).await;

        let cpu = asi
            .as_ref()
            .and_then(|v| read_numeric(v, &["cpu", "cpu_load", "cpu_usage"]))
            .unwrap_or(0.10);

        let harmony = jona
            .as_ref()
            .and_then(|v| read_numeric(v, &["harmony", "harmony_score", "score"]))
            .unwrap_or(90.0);

        let anomaly_score = albi
            .as_ref()
            .and_then(|v| read_numeric(v, &["anomaly_score", "anomalies", "risk"]))
            .unwrap_or(0.10);

        let anomalies = albi
            .as_ref()
            .map(|v| read_vec_string(v, "anomalies"))
            .unwrap_or_default();

        let (decision, reason) = derive_decision(cpu, harmony, anomaly_score);

        let payload = DecisionPayload {
            signal: decision.clone(),
            reason: reason.clone(),
            preferred_origin: "http://10.10.0.1:8000".to_string(),
            fallback_origin: "http://10.10.0.3:8000".to_string(),
            compute_origin: "http://10.10.0.2:8000".to_string(),
            harmony,
            anomalies,
        };
        publish_decision(&client, &ocean_core_url, &payload).await;

        let mut write = app_state.snapshot.write().await;
        write.alba_ok = alba.is_some();
        write.albi_ok = albi.is_some();
        write.jona_ok = jona.is_some();
        write.asi_ok = asi.is_some();
        write.cpu = cpu;
        write.harmony = harmony;
        write.anomaly_score = anomaly_score;
        write.decision = decision;
        write.decision_reason = reason;

        tokio::time::sleep(Duration::from_secs(2)).await;
    }
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "asi_trinity: ok".to_string(),
    })
}

async fn trinity_state(State(app_state): State<AppState>) -> Json<TrinitySnapshot> {
    Json(app_state.snapshot.read().await.clone())
}

#[tokio::main]
async fn main() {
    let trinity_base_url = get_env("TRINITY_BASE_URL", "http://10.10.0.2:9999");
    let ocean_core_url = get_env("OCEAN_CORE_URL", "http://10.10.0.1:9000");
    let bind_addr = get_env("ASI_TRINITY_BIND", "0.0.0.0:8082");

    let state = AppState {
        snapshot: Arc::new(RwLock::new(TrinitySnapshot {
            alba_ok: false,
            albi_ok: false,
            jona_ok: false,
            asi_ok: false,
            cpu: 0.0,
            harmony: 0.0,
            anomaly_score: 0.0,
            decision: "boot".to_string(),
            decision_reason: "initializing".to_string(),
        })),
    };

    tokio::spawn(run_orchestrator_loop(
        state.clone(),
        trinity_base_url,
        ocean_core_url,
    ));

    let app = Router::new()
        .route("/health", get(health))
        .route("/trinity/state", get(trinity_state))
        .with_state(state);

    let listener = TcpListener::bind(bind_addr).await.unwrap();
    println!("ASI Trinity orchestrator running");
    axum::serve(listener, app).await.unwrap();
}
