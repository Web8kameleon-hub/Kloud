use axum::{
    extract::{Query, State},
    response::Html,
    routing::{get, post},
    Json, Router,
};
use base64::{engine::general_purpose::STANDARD as B64, Engine as _};
use protocol::{Message, TideLevel};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::{SystemTime, UNIX_EPOCH};
use tokio::sync::Mutex;

use crate::Metrics;

#[derive(Clone)]
pub struct ApiState {
    pub node_id: u64,
    pub metrics: Arc<Mutex<Metrics>>,
    pub tide_level: Arc<Mutex<TideLevel>>,
    pub external_tx: tokio::sync::mpsc::Sender<Message>,
    pub merge_sync: Arc<Mutex<super::merge_sync_engine::MergeSyncEngine>>,
    pub security_events: Arc<Mutex<Vec<SecurityEvent>>>,
}

#[derive(Clone, Serialize)]
pub struct SecurityEvent {
    pub timestamp_ms: u128,
    pub node_id: u64,
    pub endpoint: String,
    pub action: String,
    pub stigma_level: u8,
    pub ndb_score: f32,
    pub outcome: String,
}

#[derive(Deserialize)]
pub struct SubmitRequest {
    pub ops: Vec<String>, // e.g., ["S", "C"]
    pub payload: String,  // base64 encoded
    pub ttl: Option<u64>,
    pub stigma_level: Option<u8>,
}

#[derive(Serialize)]
pub struct StatusResponse {
    pub state: String, // "Active", etc.
    pub tide: String,
    pub metrics: Metrics,
    pub ndb_score: f32,
    pub ndb_delta: f32,
    pub ndb_threshold: f32,
}

#[derive(Serialize)]
pub struct StateResponse {
    pub state: std::collections::HashMap<String, String>, // key -> base64 value
}

#[derive(Deserialize)]
pub struct StatusQuery {
    pub stigma_level: Option<u8>,
}

#[derive(Deserialize)]
pub struct EventsQuery {
    pub limit: Option<usize>,
}

#[derive(Deserialize)]
pub struct DashboardQuery {
    pub endpoint: Option<String>,
    pub outcome: Option<String>,
    pub limit: Option<usize>,
}

#[derive(Serialize)]
pub struct SecurityStatusResponse {
    pub node_id: u64,
    pub tide: String,
    pub ndb_score: f32,
    pub ndb_delta: f32,
    pub ndb_threshold: f32,
    pub high_risk: bool,
    pub event_count: usize,
}

pub fn create_router(state: ApiState) -> Router {
    Router::new()
        .route("/submit", get(get_submit_help).post(submit_op))
        .route("/status", get(get_status))
        .route("/security/status", get(get_security_status))
        .route("/security/events", get(get_security_events))
        .route("/peers", get(get_peers))
        .route("/state", get(get_state))
        .route("/dashboard", get(get_dashboard))
        .with_state(state)
}

async fn get_submit_help() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "error": "Method Not Allowed for browser GET",
        "hint": "Use POST /submit with JSON body",
        "example": {
            "ops": ["S", "C"],
            "payload": "AQID",
            "ttl": 10,
            "stigma_level": 2
        }
    }))
}

fn sanitize_stigma_level(level: Option<u8>) -> u8 {
    level.unwrap_or(2).clamp(1, 3)
}

fn compute_ndb_score(metrics: &Metrics) -> f32 {
    let latency_component = (metrics.avg_latency_ms as f32 / 250.0).min(1.0);
    let load_component = metrics.load.clamp(0.0, 1.0);
    let peer_component = (metrics.active_peers as f32 / 12.0).min(1.0);

    // Normalized 0..1 security pressure score.
    latency_component * 0.45 + load_component * 0.40 + peer_component * 0.15
}

fn ndb_threshold() -> f32 {
    0.65
}

fn ndb_delta(score: f32) -> f32 {
    score - ndb_threshold()
}

fn compact_float(value: f32) -> f32 {
    (value * 1000.0).round() / 1000.0
}

async fn append_security_event(
    state: &ApiState,
    endpoint: &str,
    action: &str,
    stigma_level: u8,
    ndb_score: f32,
    outcome: &str,
) {
    let mut events = state.security_events.lock().await;
    events.push(SecurityEvent {
        timestamp_ms: SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis(),
        node_id: state.node_id,
        endpoint: endpoint.to_string(),
        action: action.to_string(),
        stigma_level,
        ndb_score: compact_float(ndb_score),
        outcome: outcome.to_string(),
    });

    // Keep bounded in-memory event list.
    if events.len() > 2000 {
        let overflow = events.len() - 2000;
        events.drain(0..overflow);
    }
}

async fn submit_op(
    State(state): State<ApiState>,
    Json(req): Json<SubmitRequest>,
) -> Json<serde_json::Value> {
    let stigma_level = sanitize_stigma_level(req.stigma_level);
    let metrics = *state.metrics.lock().await;
    let score = compute_ndb_score(&metrics);

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
        append_security_event(
            &state,
            "/submit",
            "submit-op",
            stigma_level,
            score,
            "rejected-invalid-ops",
        ).await;
        return Json(serde_json::json!({"error": "Invalid ops"}));
    }

    // Decode payload
    let payload = match base64::decode(&req.payload) {
        Ok(p) => p,
        Err(_) => {
            append_security_event(
                &state,
                "/submit",
                "submit-op",
                stigma_level,
                score,
                "rejected-invalid-payload",
            ).await;
            return Json(serde_json::json!({"error": "Invalid payload base64"}));
        }
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
        append_security_event(
            &state,
            "/submit",
            "submit-op",
            stigma_level,
            score,
            "failed-channel-closed",
        ).await;
        return Json(serde_json::json!({"error": "Failed to submit"}));
    }

    append_security_event(
        &state,
        "/submit",
        "submit-op",
        stigma_level,
        score,
        "accepted",
    ).await;

    let response = match stigma_level {
        1 => serde_json::json!({
            "status": "submitted",
            "summary": "accepted"
        }),
        2 => serde_json::json!({
            "status": "submitted",
            "accepted_ops": req.ops,
            "ndb_score": compact_float(score),
            "ndb_delta": compact_float(ndb_delta(score))
        }),
        _ => serde_json::json!({
            "ok": true,
            "n": compact_float(score)
        }),
    };

    Json(response)
}

async fn get_status(
    State(state): State<ApiState>,
    Query(query): Query<StatusQuery>,
) -> Json<serde_json::Value> {
    let stigma_level = sanitize_stigma_level(query.stigma_level);
    let metrics = *state.metrics.lock().await;
    let tide = *state.tide_level.lock().await;
    let score = compute_ndb_score(&metrics);
    let delta = ndb_delta(score);

    let rich = StatusResponse {
        state: "Active".to_string(), // TODO: real state
        tide: format!("{:?}", tide),
        metrics,
        ndb_score: compact_float(score),
        ndb_delta: compact_float(delta),
        ndb_threshold: ndb_threshold(),
    };

    let payload = match stigma_level {
        1 => serde_json::json!({
            "state": rich.state,
            "tide": rich.tide,
            "summary": "stable",
            "ndb_score": rich.ndb_score
        }),
        2 => serde_json::to_value(rich).unwrap_or_else(|_| serde_json::json!({"error": "serialize"})),
        _ => serde_json::json!({
            "t": format!("{:?}", tide),
            "n": compact_float(score)
        }),
    };

    append_security_event(
        &state,
        "/status",
        "read-status",
        stigma_level,
        score,
        "ok",
    ).await;

    Json(payload)
}

async fn get_security_status(
    State(state): State<ApiState>,
) -> Json<SecurityStatusResponse> {
    let metrics = *state.metrics.lock().await;
    let tide = *state.tide_level.lock().await;
    let score = compute_ndb_score(&metrics);
    let delta = ndb_delta(score);
    let threshold = ndb_threshold();
    let event_count = state.security_events.lock().await.len();

    Json(SecurityStatusResponse {
        node_id: state.node_id,
        tide: format!("{:?}", tide),
        ndb_score: compact_float(score),
        ndb_delta: compact_float(delta),
        ndb_threshold: threshold,
        high_risk: score > threshold,
        event_count,
    })
}

async fn get_security_events(
    State(state): State<ApiState>,
    Query(query): Query<EventsQuery>,
) -> Json<Vec<SecurityEvent>> {
    let max_limit = 200;
    let limit = query.limit.unwrap_or(25).clamp(1, max_limit);
    let events = state.security_events.lock().await;
    let mut result: Vec<SecurityEvent> = events.iter().rev().take(limit).cloned().collect();
    result.reverse();
    Json(result)
}

async fn get_peers(
    State(state): State<ApiState>,
) -> Json<serde_json::Value> {
    let metrics = *state.metrics.lock().await;
    let peers: Vec<u64> = (1..=metrics.active_peers as u64).collect();
    Json(serde_json::json!({
        "active_peer_count": metrics.active_peers,
        "peers": peers
    }))
}

async fn get_state(
    State(state): State<ApiState>,
) -> Json<StateResponse> {
    let raw_state = state.merge_sync.lock().await.get_state().clone();
    let mut encoded: HashMap<String, String> = HashMap::new();
    for (k, v) in raw_state {
        encoded.insert(k, B64.encode(v));
    }

    Json(StateResponse { state: encoded })
}

async fn get_dashboard(
    State(state): State<ApiState>,
    Query(query): Query<DashboardQuery>,
) -> Html<String> {
    let metrics = state.metrics.lock().await.clone();
    let tide = *state.tide_level.lock().await;
    let state_map = state.merge_sync.lock().await.get_state().clone();
    let all_events = state.security_events.lock().await.clone();
    let event_count = all_events.len();
    let raw_ndb_score = compute_ndb_score(&metrics);
    let raw_ndb_delta = ndb_delta(raw_ndb_score);
    let threshold = ndb_threshold();
    let high_risk = raw_ndb_score > threshold;
    let ndb_score = compact_float(raw_ndb_score);
    let ndb_delta = compact_float(raw_ndb_delta);
    let load_percent = (metrics.load * 100.0).clamp(0.0, 100.0);
    let latency_percent = ((metrics.avg_latency_ms as f32 / 250.0) * 100.0).clamp(0.0, 100.0);
    let bandwidth_percent = ((metrics.bandwidth_kbps as f32 / 10000.0) * 100.0).clamp(0.0, 100.0);
    let endpoint_filter = query.endpoint.unwrap_or_default();
    let outcome_filter = query.outcome.unwrap_or_default();
    let limit = query.limit.unwrap_or(25).clamp(5, 200);

    let filtered_events: Vec<SecurityEvent> = all_events
        .into_iter()
        .filter(|e| endpoint_filter.is_empty() || e.endpoint == endpoint_filter)
        .filter(|e| outcome_filter.is_empty() || e.outcome == outcome_filter)
        .rev()
        .take(limit)
        .collect::<Vec<_>>()
        .into_iter()
        .rev()
        .collect();

    let mut state_html = String::new();
    for (k, v) in &state_map {
        state_html.push_str(&format!(
            "<li><span class=\"state-key\">{}</span><code class=\"state-val\">{}</code></li>",
            k,
            B64.encode(v)
        ));
    }

    if state_html.is_empty() {
        state_html.push_str("<li><span class=\"state-key\">empty</span><code class=\"state-val\">no local keys yet</code></li>");
    }

    let mut events_rows = String::new();
    for e in &filtered_events {
        let severity_class = if e.outcome == "ok" || e.outcome == "accepted" {
            "sev-ok"
        } else if e.outcome.starts_with("rejected") {
            "sev-warn"
        } else {
            "sev-err"
        };
        events_rows.push_str(&format!(
            "<tr class=\"{}\"><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{:.3}</td><td>{}</td></tr>",
            severity_class,
            e.timestamp_ms,
            e.endpoint,
            e.action,
            e.stigma_level,
            e.ndb_score,
            e.outcome
        ));
    }
    if events_rows.is_empty() {
        events_rows.push_str("<tr><td colspan=\"6\">No events match the current filters.</td></tr>");
    }

    let tide_label = format!("{:?}", tide);
    let (tide_color, tide_chip_bg) = match tide {
        TideLevel::High => ("#0f9d58", "#e7f7ed"),
        TideLevel::Normal => ("#e67e22", "#fff3e7"),
        TideLevel::Low => ("#e53935", "#ffeaea"),
    };

    let html = format!(
        r#"
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Kloud Control Surface</title>
            <style>
                :root {{
                    --bg-top: #f5fbff;
                    --bg-bottom: #fff9f3;
                    --ink: #11243a;
                    --muted: #4f6278;
                    --panel: rgba(255, 255, 255, 0.82);
                    --line: rgba(17, 36, 58, 0.12);
                    --accent: #0a84ff;
                    --accent-2: #00a67d;
                }}
                * {{ box-sizing: border-box; }}
                body {{
                    margin: 0;
                    font-family: "Space Grotesk", "IBM Plex Sans", "Segoe UI", sans-serif;
                    color: var(--ink);
                    background:
                      radial-gradient(1200px 600px at -10% -10%, #d9f1ff 0%, transparent 60%),
                      radial-gradient(1200px 600px at 110% -20%, #ffe9cf 0%, transparent 55%),
                      linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
                    min-height: 100vh;
                }}
                .wrap {{
                    max-width: 1180px;
                    margin: 0 auto;
                    padding: 28px 18px 40px;
                }}
                .hero {{
                    display: flex;
                    justify-content: space-between;
                    align-items: end;
                    gap: 14px;
                    margin-bottom: 16px;
                    animation: fade-slide .6s ease-out;
                }}
                .title {{ margin: 0; font-size: clamp(1.5rem, 2.8vw, 2.2rem); letter-spacing: .2px; }}
                .sub {{ margin: 6px 0 0; color: var(--muted); font-size: .96rem; }}
                .chip {{
                    background: {}; color: {}; border: 1px solid {}33;
                    border-radius: 999px; padding: 8px 12px; font-weight: 700; font-size: .86rem;
                    white-space: nowrap;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(12, 1fr);
                    gap: 14px;
                }}
                .card {{
                    background: var(--panel);
                    border: 1px solid var(--line);
                    border-radius: 16px;
                    backdrop-filter: blur(4px);
                    box-shadow: 0 8px 30px rgba(15, 34, 55, .08);
                    padding: 16px;
                    animation: rise .5s ease-out;
                }}
                .span-4 {{ grid-column: span 4; }}
                .span-6 {{ grid-column: span 6; }}
                .span-8 {{ grid-column: span 8; }}
                .span-12 {{ grid-column: span 12; }}
                .k {{ font-size: .8rem; color: var(--muted); text-transform: uppercase; letter-spacing: .7px; }}
                .v {{ margin-top: 8px; font-size: 1.8rem; font-weight: 700; }}
                .delta {{ margin-top: 6px; color: {}; font-weight: 700; }}
                .ok {{ color: #0a8f5b; }}
                .risk {{ color: #c2382e; }}
                .meter {{ margin-top: 10px; }}
                .meter-top {{ display: flex; justify-content: space-between; color: var(--muted); font-size: .84rem; margin-bottom: 6px; }}
                .track {{ height: 10px; border-radius: 999px; background: #e8eff8; overflow: hidden; }}
                .bar {{ height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); }}
                .state-list {{ margin: 0; padding-left: 18px; max-height: 240px; overflow: auto; }}
                .state-list li {{ margin: 8px 0; }}
                .state-key {{ font-weight: 700; margin-right: 8px; }}
                .state-val {{ color: #4a5b71; word-break: break-all; }}
                .ops-head {{ display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 10px; }}
                .ops-form {{ display: flex; flex-wrap: wrap; gap: 8px; }}
                .ops-form select, .ops-form input {{
                    border: 1px solid var(--line);
                    border-radius: 8px;
                    padding: 7px 10px;
                    font: inherit;
                    background: #fff;
                    color: var(--ink);
                }}
                .ops-form button {{
                    border: 0;
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: #fff;
                    background: linear-gradient(90deg, #0a84ff, #00a67d);
                    font-weight: 700;
                    cursor: pointer;
                }}
                .table-wrap {{ overflow: auto; border: 1px solid var(--line); border-radius: 12px; }}
                table {{ width: 100%; border-collapse: collapse; min-width: 700px; background: #fff; }}
                th, td {{ padding: 10px; border-bottom: 1px solid #edf1f5; text-align: left; font-size: .92rem; }}
                th {{ background: #f6f9fc; text-transform: uppercase; letter-spacing: .5px; font-size: .76rem; color: #4f6278; }}
                tr.sev-ok td {{ background: #f2fbf7; }}
                tr.sev-warn td {{ background: #fff8ef; }}
                tr.sev-err td {{ background: #fff0f0; }}
                .ops-tools {{ display: flex; gap: 8px; align-items: center; }}
                .tool-btn {{
                    border: 1px solid var(--line);
                    border-radius: 8px;
                    background: #fff;
                    color: var(--ink);
                    padding: 7px 10px;
                    font: inherit;
                    cursor: pointer;
                }}
                @keyframes rise {{ from {{ opacity: .15; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                @keyframes fade-slide {{ from {{ opacity: .15; transform: translateY(-8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
                @media (max-width: 980px) {{
                    .span-4, .span-6, .span-8 {{ grid-column: span 12; }}
                    .hero {{ flex-direction: column; align-items: start; }}
                }}
            </style>
        </head>
        <body>
            <div class="wrap">
                <div class="hero">
                    <div>
                        <h1 class="title">Kloud Control Surface</h1>
                        <p class="sub">Live Sovereign Fabric telemetry with NDB/STIGMA security posture.</p>
                    </div>
                    <div class="chip">TIDE: {}</div>
                </div>

                <div class="grid">
                    <section class="card span-4">
                        <div class="k">Active Peers</div>
                        <div class="v">{}</div>
                    </section>

                    <section class="card span-4">
                        <div class="k">NDB Score</div>
                        <div class="v">{:.3}</div>
                        <div class="delta">Delta: {:+.3} vs threshold {:.2}</div>
                    </section>

                    <section class="card span-4">
                        <div class="k">Security Posture</div>
                        <div class="v {}">{}</div>
                        <div class="sub">Events tracked: {}</div>
                    </section>

                    <section class="card span-6">
                        <div class="k">Latency</div>
                        <div class="v">{} ms</div>
                        <div class="meter">
                            <div class="meter-top"><span>Current</span><span>{:.1}% of nominal band</span></div>
                            <div class="track"><div class="bar" style="width:{:.1}%"></div></div>
                        </div>
                    </section>

                    <section class="card span-6">
                        <div class="k">Bandwidth</div>
                        <div class="v">{} kbps</div>
                        <div class="meter">
                            <div class="meter-top"><span>Current</span><span>{:.1}% of baseline</span></div>
                            <div class="track"><div class="bar" style="width:{:.1}%"></div></div>
                        </div>
                    </section>

                    <section class="card span-8">
                        <div class="k">Node Load</div>
                        <div class="v">{:.2}</div>
                        <div class="meter">
                            <div class="meter-top"><span>Utilization</span><span>{:.1}%</span></div>
                            <div class="track"><div class="bar" style="width:{:.1}%"></div></div>
                        </div>
                    </section>

                    <section class="card span-4">
                        <div class="k">State Keys</div>
                        <div class="v">{}</div>
                        <div class="sub">CRDT local map cardinality</div>
                    </section>

                    <section class="card span-12">
                        <div class="ops-head">
                            <div class="k">Operations Events</div>
                            <div class="ops-tools">
                                <span id="refresh-state" class="sub">Auto-refresh every 5s · Showing {} / {} events</span>
                                <button id="pause-refresh" class="tool-btn" type="button">Pause Refresh</button>
                                <button id="export-csv" class="tool-btn" type="button">Export CSV</button>
                            </div>
                        </div>
                        <form class="ops-form" method="get" action="/dashboard">
                            <select name="endpoint">
                                <option value="" {}>All endpoints</option>
                                <option value="/status" {}>/status</option>
                                <option value="/submit" {}>/submit</option>
                                <option value="/security/status" {}>/security/status</option>
                            </select>
                            <select name="outcome">
                                <option value="" {}>All outcomes</option>
                                <option value="ok" {}>ok</option>
                                <option value="accepted" {}>accepted</option>
                                <option value="rejected-invalid-ops" {}>rejected-invalid-ops</option>
                                <option value="rejected-invalid-payload" {}>rejected-invalid-payload</option>
                                <option value="failed-channel-closed" {}>failed-channel-closed</option>
                            </select>
                            <input type="number" min="5" max="200" name="limit" value="{}" />
                            <button type="submit">Apply</button>
                        </form>
                        <div class="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>timestamp_ms</th>
                                        <th>endpoint</th>
                                        <th>action</th>
                                        <th>stigma</th>
                                        <th>ndb_score</th>
                                        <th>outcome</th>
                                    </tr>
                                </thead>
                                <tbody id="events-body">{}</tbody>
                            </table>
                        </div>
                    </section>

                    <section class="card span-12">
                        <div class="k">Local State (base64)</div>
                        <ul class="state-list">{}</ul>
                    </section>
                </div>
            </div>
            <script>
                (function () {{
                    var refreshMs = 5000;
                    var paused = false;
                    var pauseBtn = document.getElementById("pause-refresh");
                    var stateEl = document.getElementById("refresh-state");
                    var exportBtn = document.getElementById("export-csv");

                    function updateState() {{
                        if (!stateEl) return;
                        var base = "Showing {} / {} events";
                        stateEl.textContent = (paused ? "Refresh paused" : "Auto-refresh every 5s") + " · " + base;
                    }}

                    if (pauseBtn) {{
                        pauseBtn.addEventListener("click", function () {{
                            paused = !paused;
                            pauseBtn.textContent = paused ? "Resume Refresh" : "Pause Refresh";
                            updateState();
                        }});
                    }}

                    if (exportBtn) {{
                        exportBtn.addEventListener("click", function () {{
                            var rows = Array.from(document.querySelectorAll("table tr"));
                            var csv = rows.map(function (row) {{
                                return Array.from(row.querySelectorAll("th,td")).map(function (cell) {{
                                    var text = (cell.textContent || "").replace(/\"/g, '""').trim();
                                    return '"' + text + '"';
                                }}).join(",");
                            }}).join("\n");

                            var blob = new Blob([csv], {{ type: "text/csv;charset=utf-8;" }});
                            var url = URL.createObjectURL(blob);
                            var a = document.createElement("a");
                            a.href = url;
                            a.download = "kloud-events.csv";
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                        }});
                    }}

                    updateState();
                    setInterval(function () {{
                        if (!paused) {{
                            window.location.reload();
                        }}
                    }}, refreshMs);
                }})();
            </script>
        </body>
        </html>
        "#,
        tide_chip_bg,
        tide_color,
        tide_color,
        if ndb_delta >= 0.0 { "#c2382e" } else { "#0a8f5b" },
        tide_label,
        metrics.active_peers,
        ndb_score,
        ndb_delta,
        threshold,
        if high_risk { "risk" } else { "ok" },
        if high_risk { "HIGH RISK" } else { "STABLE" },
        event_count,
        metrics.avg_latency_ms,
        latency_percent,
        latency_percent,
        metrics.bandwidth_kbps,
        bandwidth_percent,
        bandwidth_percent,
        metrics.load,
        load_percent,
        load_percent,
        state_map.len(),
        filtered_events.len(),
        event_count,
        filtered_events.len(),
        event_count,
        if endpoint_filter.is_empty() { "selected" } else { "" },
        if endpoint_filter == "/status" { "selected" } else { "" },
        if endpoint_filter == "/submit" { "selected" } else { "" },
        if endpoint_filter == "/security/status" { "selected" } else { "" },
        if outcome_filter.is_empty() { "selected" } else { "" },
        if outcome_filter == "ok" { "selected" } else { "" },
        if outcome_filter == "accepted" { "selected" } else { "" },
        if outcome_filter == "rejected-invalid-ops" { "selected" } else { "" },
        if outcome_filter == "rejected-invalid-payload" { "selected" } else { "" },
        if outcome_filter == "failed-channel-closed" { "selected" } else { "" },
        limit,
        events_rows,
        filtered_events.len(),
        event_count,
        state_html
    );

    Html(html)
}