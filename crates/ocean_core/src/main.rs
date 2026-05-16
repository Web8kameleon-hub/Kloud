use std::collections::HashMap;
use std::env;
use std::sync::Arc;

use axum::{extract::State, routing::{get, post}, Json, Router};
use async_trait::async_trait;
use chrono::Utc;
use reqwest;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::net::TcpListener;
use tokio::sync::broadcast;
use tokio::sync::RwLock;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct FabricState {
    preferred_origin: String,
    active_origin: String,
    fallback_origin: String,
    compute_origin: String,
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

#[derive(Debug, Clone, Serialize, Deserialize)]
struct StigmaEvent {
    source: String,
    kind: String,
    level: u8,
    payload: Value,
    timestamp: String,
}

#[derive(Debug, Clone, Deserialize)]
struct GenericModuleEvent {
    kind: String,
    level: u8,
    payload: Value,
    timestamp: Option<String>,
}

type StigmaBus = broadcast::Sender<StigmaEvent>;

#[derive(Clone)]
struct AppState {
    fabric: Arc<RwLock<FabricState>>,
    flow_fields: Arc<RwLock<FlowFields>>,
    impulse_mesh: Arc<RwLock<OceanImpulse>>,
    latest_telemetry: Arc<RwLock<HashMap<String, TelemetryPayload>>>,
    mesh_registry: Arc<RwLock<HashMap<String, MeshNodeRegistration>>>,
    mesh_status: Arc<RwLock<HashMap<String, MeshNodeStatus>>>,
    stigma_bus: StigmaBus,
}

fn create_stigma_bus() -> (StigmaBus, broadcast::Receiver<StigmaEvent>) {
    broadcast::channel(10_000)
}

fn event_timestamp(ts: Option<String>) -> String {
    ts.unwrap_or_else(|| Utc::now().to_rfc3339())
}

fn vec_strings_from_payload(payload: &Value, key: &str) -> Vec<String> {
    payload
        .get(key)
        .and_then(Value::as_array)
        .map(|items| {
            items
                .iter()
                .filter_map(Value::as_str)
                .map(ToString::to_string)
                .collect::<Vec<_>>()
        })
        .unwrap_or_default()
}

fn maybe_string(payload: &Value, key: &str) -> Option<String> {
    payload
        .get(key)
        .and_then(Value::as_str)
        .map(ToString::to_string)
}

// ─── Ocean Core: Distributed Decision-Making Center ────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlowFields {
    pub tension: f64,
    pub harmony: f64,
    pub risk: f64,
    pub gap: f64,
    pub pattern: f64,
    pub compute: f64,
    pub load: f64,
    pub protection: f64,
    pub origin_shift: f64,
    pub updated_at: String,
}

impl FlowFields {
    fn new() -> Self {
        Self {
            tension: 0.0,
            harmony: 100.0,
            risk: 0.0,
            gap: 0.0,
            pattern: 0.0,
            compute: 0.0,
            load: 0.0,
            protection: 0.0,
            origin_shift: 0.0,
            updated_at: Utc::now().to_rfc3339(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OceanImpulse {
    pub action: String,        // reroute, scale, stabilize, optimize, protect
    pub target: String,        // agent, node, gateway, fabric
    pub intensity: u8,         // 0-5
    pub reason: String,
    pub timestamp: String,
}

impl OceanImpulse {
    fn reroute(reason: &str) -> Self {
        Self {
            action: "reroute".into(),
            target: "gateway".into(),
            intensity: 4,
            reason: reason.into(),
            timestamp: Utc::now().to_rfc3339(),
        }
    }

    fn scale(reason: &str) -> Self {
        Self {
            action: "scale".into(),
            target: "agents".into(),
            intensity: 4,
            reason: reason.into(),
            timestamp: Utc::now().to_rfc3339(),
        }
    }

    fn protect(reason: &str) -> Self {
        Self {
            action: "protect".into(),
            target: "gateway".into(),
            intensity: 5,
            reason: reason.into(),
            timestamp: Utc::now().to_rfc3339(),
        }
    }

    fn optimize(reason: &str) -> Self {
        Self {
            action: "optimize".into(),
            target: "agents".into(),
            intensity: 3,
            reason: reason.into(),
            timestamp: Utc::now().to_rfc3339(),
        }
    }

    fn stabilize(reason: &str) -> Self {
        Self {
            action: "stabilize".into(),
            target: "fabric".into(),
            intensity: 2,
            reason: reason.into(),
            timestamp: Utc::now().to_rfc3339(),
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct FabricSelfReport {
    pub summary: String,
    pub dominant_field: String,
    pub stability: f64,
    pub concern_level: f64,
    pub recommended_focus: String,
    pub timestamp: String,
}

// ─── Resonance Engine: Flow Field Physics ──────────────────────────────────

/// Resonance: fields influence each other as in biological brain
fn resonate(fields: &mut FlowFields) {
    // Gap increases risk
    fields.risk += fields.gap * 0.2;

    // Pattern increases compute demand
    fields.compute += fields.pattern * 0.15;

    // Tension decreases harmony
    fields.harmony -= fields.tension * 0.1;

    // Risk increases protection
    fields.protection += fields.risk * 0.25;

    // Load increases tension
    fields.tension += fields.load * 0.1;

    // Harmony decreases tension (natural stabilization)
    fields.tension -= fields.harmony * 0.05;

    // Origin shift increases risk
    fields.risk += fields.origin_shift * 0.1;

    // Clamp to natural bounds
    fields.tension = fields.tension.clamp(0.0, 10.0);
    fields.harmony = fields.harmony.clamp(0.0, 100.0);
    fields.risk = fields.risk.clamp(0.0, 10.0);
    fields.gap = fields.gap.clamp(0.0, 10.0);
    fields.pattern = fields.pattern.clamp(0.0, 10.0);
    fields.compute = fields.compute.clamp(0.0, 10.0);
    fields.load = fields.load.clamp(0.0, 10.0);
    fields.protection = fields.protection.clamp(0.0, 10.0);
    fields.origin_shift = fields.origin_shift.clamp(0.0, 10.0);
}

/// Natural damping: biological homeostasis
fn damp(fields: &mut FlowFields) {
    fields.tension *= 0.95;
    fields.risk *= 0.92;
    fields.gap *= 0.90;
    fields.pattern *= 0.93;
    fields.compute *= 0.94;
    fields.load *= 0.96;
    fields.protection *= 0.90;
    fields.origin_shift *= 0.88;
    fields.updated_at = Utc::now().to_rfc3339();
}

// ─── JONA: Guardian Layer (Ethical Filtering & Safety) ────────────────────

/// JONA filter: ethical, safe, calm recommendations
fn jona_filter_recommendation(fields: &FlowFields, concern: f64) -> String {
    if concern > 7.0 {
        return "stabilize_gently_and_reduce_pressure".into();
    }

    if fields.gap > 3.0 {
        return "improve_clarity_and_reduce_ambiguity".into();
    }

    if fields.load > 4.0 {
        return "scale_resources_in_a_balanced_way".into();
    }

    if fields.risk > 4.0 {
        return "strengthen_safeguards_carefully".into();
    }

    "maintain_harmony_and_monitor_softly".into()
}

/// JONA filter: calm, safe language
fn jona_filter_summary(text: String) -> String {
    text.replace("Concern", "Observed concern")
        .replace("Stability", "Current stability")
        .replace("dominant field", "leading influence")
}

// ─── JONA: Impulse Mesh Guardian ───────────────────────────────────────────

#[derive(Debug, Clone)]
pub struct JonaFilter;

impl JonaFilter {
    pub fn new() -> Self {
        Self
    }

    /// Filter impulse: safety, tone, stability before broadcast
    pub fn filter_impulse(&self, impulse: OceanImpulse, fields: &FlowFields) -> OceanImpulse {
        let mut filtered = impulse.clone();

        // 1) Reduce intensity if risk is high (safety)
        if fields.risk > 6.0 && filtered.intensity > 2 {
            filtered.intensity = (filtered.intensity - 1).max(1);
        }

        // 2) Soften language (tone)
        filtered.reason = self.filter_reason(&filtered.reason);

        // 3) Prevent unnecessary impulses if harmony is high
        if fields.harmony > 80.0 && filtered.action != "stabilize" {
            filtered.intensity = (filtered.intensity - 1).max(1);
        }

        // 4) Redirect to protection if risk is critical
        if fields.risk > 7.0 && filtered.action != "protect" {
            filtered.action = "protect".into();
            filtered.reason = "critical stabilization recommended".into();
            filtered.intensity = 4;
        }

        // 5) Clamp intensity to safe range
        filtered.intensity = filtered.intensity.clamp(1, 4);

        filtered
    }

    /// Soften language: prevent alarmism
    fn filter_reason(&self, reason: &str) -> String {
        reason
            .replace("high risk", "elevated risk")
            .replace("critical", "notable")
            .replace("instability", "variation")
            .replace("DANGER", "caution")
            .replace("FAILURE", "degradation")
            .replace("PANIC", "concern")
    }
}

// ─── Impulse Mesh: Distributed Decision Broadcast ─────────────────────────

#[async_trait::async_trait]
pub trait ImpulseSubscriber {
    async fn on_impulse(&self, impulse: OceanImpulse);
}

pub struct ImpulseMesh {
    pub jona: JonaFilter,
}

impl ImpulseMesh {
    pub fn new() -> Self {
        Self {
            jona: JonaFilter::new(),
        }
    }

    /// Broadcast impulse through JONA filtering
    pub async fn broadcast(
        &self,
        impulse: OceanImpulse,
        fields: &FlowFields,
        fabric: &SharedFabricState,
    ) {
        // JONA: filter impulse before broadcast
        let safe_impulse = self.jona.filter_impulse(impulse, fields);

        // Apply to fabric state
        apply_impulse_to_fabric(&safe_impulse, fabric).await;
    }
}

async fn apply_impulse_to_fabric(impulse: &OceanImpulse, fabric: &SharedFabricState) {
    let mut state = fabric.write().await;
    match impulse.action.as_str() {
        "reroute" => {
            state.active_origin = state.fallback_origin.clone();
            state.asi_signal = "reroute".into();
            state.decision_explanation = impulse.reason.clone();
        }
        "scale" => {
            state.asi_signal = "scale_up".into();
            state.decision_explanation = impulse.reason.clone();
        }
        "optimize" => {
            state.asi_signal = "optimize".into();
            state.decision_explanation = impulse.reason.clone();
        }
        "protect" => {
            state.asi_signal = "protect".into();
            state.decision_explanation = impulse.reason.clone();
        }
        "stabilize" => {
            state.asi_signal = "stabilize".into();
            state.decision_explanation = impulse.reason.clone();
        }
        _ => {}
    }
}

// ─── Ocean Core Decision Engine ─────────────────────────────────────────────

/// Ocean Core: decision from resonance, not raw events
fn ocean_decision(fields: &FlowFields) -> Option<OceanImpulse> {
    // High risk → protect
    if fields.risk > 4.0 || fields.protection > 3.5 {
        return Some(OceanImpulse::protect("high risk resonance"));
    }

    // Compute resonance → scale
    if fields.compute > 4.0 || fields.load > 4.0 {
        return Some(OceanImpulse::scale("compute resonance"));
    }

    // Origin instability → reroute
    if fields.origin_shift > 3.0 {
        return Some(OceanImpulse::reroute("origin instability resonance"));
    }

    // Gap resonance → optimize
    if fields.gap > 3.0 {
        return Some(OceanImpulse::optimize("gap resonance"));
    }

    // Tension high + harmony low → stabilize
    if fields.tension > 5.0 && fields.harmony < 50.0 {
        return Some(OceanImpulse::stabilize("tension in fabric"));
    }

    None
}

/// Build self-report from flow fields with JONA filtering
fn build_self_report(fields: &FlowFields) -> FabricSelfReport {
    let (dominant, value) = {
        let fields_vec = vec![
            ("tension", fields.tension),
            ("harmony", fields.harmony),
            ("risk", fields.risk),
            ("gap", fields.gap),
            ("pattern", fields.pattern),
            ("compute", fields.compute),
            ("load", fields.load),
            ("protection", fields.protection),
            ("origin_shift", fields.origin_shift),
        ];
        fields_vec
            .into_iter()
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
            .unwrap_or(("unknown", 0.0))
    };

    let stability = (fields.harmony - fields.tension - fields.risk).clamp(-5.0, 5.0);
    let concern = (fields.risk + fields.gap + (if fields.protection > 5.0 { 2.0 } else { 0.0 }))
        .min(10.0);

    // JONA: filtered recommendation
    let recommended = jona_filter_recommendation(fields, concern);

    // JONA: calm, safe summary
    let summary_raw = format!(
        "Current leading influence: {} ({:.2}). Current stability: {:.2}. Observed concern: {:.2}.",
        dominant.0, value, stability, concern
    );

    let summary = jona_filter_summary(summary_raw);

    FabricSelfReport {
        summary,
        dominant_field: dominant.0.to_string(),
        stability,
        concern_level: concern,
        recommended_focus: recommended,
        timestamp: Utc::now().to_rfc3339(),
    }
}

// ─── capability routing & autoscaling ──────────────────────────────────────

#[derive(Debug, Clone)]
pub struct CapabilityTarget {
    capability: String,
    target_capacity: usize,
}

/// Map Stigma event → (capability, target_capacity)
fn capability_router(ev: &StigmaEvent) -> Option<CapabilityTarget> {
    match (ev.source.as_str(), ev.kind.as_str(), ev.level) {
        // Trinity: ALBA/ALBI/JONA
        ("ALBA", "frame", 3..=u8::MAX) => Some(CapabilityTarget {
            capability: "network-monitoring".into(),
            target_capacity: 4,
        }),
        ("ALBI", "anomaly", 2..=u8::MAX) => Some(CapabilityTarget {
            capability: "pattern-recognition".into(),
            target_capacity: 6,
        }),
        ("JONA", "harmony", _) => Some(CapabilityTarget {
            capability: "insight-synthesis".into(),
            target_capacity: 3,
        }),

        // MALI: Meta-Analysis
        ("MALI", "prediction", 3..=u8::MAX) => Some(CapabilityTarget {
            capability: "meta-analysis".into(),
            target_capacity: 5,
        }),
        ("MALI", "pattern", 2..=u8::MAX) => Some(CapabilityTarget {
            capability: "pattern-analysis".into(),
            target_capacity: 4,
        }),

        // BLERINA: Gap Detection
        ("BLERINA", "gap", 4..=u8::MAX) => Some(CapabilityTarget {
            capability: "gap-detection".into(),
            target_capacity: 5,
        }),

        // LIAM: Tensor Processing
        ("LIAM", "eigen", 3..=u8::MAX) => Some(CapabilityTarget {
            capability: "tensor-processing".into(),
            target_capacity: 5,
        }),
        ("LIAM", "tensor", 3..=u8::MAX) => Some(CapabilityTarget {
            capability: "optimization".into(),
            target_capacity: 4,
        }),

        // ALDA: Labor Orchestration
        ("ALDA", "batch", 2..=u8::MAX) => Some(CapabilityTarget {
            capability: "labor-orchestration".into(),
            target_capacity: 6,
        }),

        // KLAJDI: Investigation
        ("KLAJDI", "anomaly", 2..=u8::MAX) => Some(CapabilityTarget {
            capability: "investigation".into(),
            target_capacity: 4,
        }),
        ("KLAJDI", "risk", 2..=u8::MAX) => Some(CapabilityTarget {
            capability: "risk-assessment".into(),
            target_capacity: 3,
        }),

        // ASI: Node Supervision
        ("ASI", "signal", _) => Some(CapabilityTarget {
            capability: "node-supervision".into(),
            target_capacity: 3,
        }),

        _ => None,
    }
}

/// Trigger autoscale for an agent capability
async fn trigger_autoscale(capability: &str, target: usize) {
    let client = reqwest::Client::new();
    let payload = serde_json::json!({
        "capability": capability,
        "target_capacity": target
    });

    let _ = client
        .post("http://10.10.0.1:9000/agents/scale")
        .json(&payload)
        .send()
        .await;
}

// ─────────────────────────────────────────────────────────────────────────────

type SharedFabricState = Arc<RwLock<FabricState>>;

async fn handle_trinity(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    match ev.kind.as_str() {
        "frame" => {
            s.harmony = (s.harmony - 0.1).max(0.0);
            s.anomalies.push("trinity_frame".into());
        }
        "anomaly" => {
            s.anomalies.push("trinity_anomaly".into());
        }
        "harmony" => {
            s.harmony = ev.payload["score"].as_f64().unwrap_or(100.0) as f32;
        }
        _ => {}
    }
    s.updated_at = ev.timestamp;
}

async fn handle_mali(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    if ev.kind == "pattern" {
        s.anomalies.push("mali_pattern".into());
        s.patterns.extend(vec_strings_from_payload(&ev.payload, "patterns"));
    }
    if ev.kind == "prediction" {
        s.predictions.extend(vec_strings_from_payload(&ev.payload, "predictions"));
        if ev.level >= 3 {
            s.asi_signal = "compute_overload".into();
            s.active_origin = s.compute_origin.clone();
            s.decision_explanation = "mali_prediction_rising".into();
        }
    }
    s.updated_at = ev.timestamp;
}

async fn handle_blerina(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    if ev.level >= 4 {
        s.asi_signal = "reroute".into();
        s.active_origin = s.fallback_origin.clone();
        s.decision_explanation = "blerina_gap_critical".into();
    }
    if let Some(gaps) = ev.payload["gaps"].as_array() {
        for g in gaps {
            s.gaps.push(format!("gap:{}", g.as_str().unwrap_or("unknown")));
            s.anomalies.push(format!("gap:{}", g.as_str().unwrap_or("unknown")));
        }
    }
    s.updated_at = ev.timestamp;
}

async fn handle_liam(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    if ev.kind == "tensor" && ev.level >= 3 {
        s.asi_signal = "optimize".into();
        s.decision_explanation = "liam_tensor_spike".into();
    }
    if ev.kind == "eigen" {
        s.anomalies.push("liam_eigen_spike".into());
    }
    if let Some(p) = maybe_string(&ev.payload, "dominant_pattern") {
        s.patterns.push(p);
    }
    s.updated_at = ev.timestamp;
}

async fn handle_alda(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    if ev.kind == "batch" && ev.payload["remaining"].as_u64().unwrap_or(0) > 1000 {
        s.asi_signal = "scale_up".into();
        s.active_origin = s.compute_origin.clone();
        s.decision_explanation = "alda_batch_overload".into();
    }
    if ev.level >= 3 {
        s.asi_signal = "compute_overload".into();
        s.active_origin = s.compute_origin.clone();
        s.decision_explanation = "alda_batch_pressure".into();
    }
    s.updated_at = ev.timestamp;
}

async fn handle_klajdi(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    if ev.kind == "anomaly" {
        s.anomalies.push("klajdi_anomaly".into());
        s.asi_signal = "reroute".into();
        s.active_origin = s.fallback_origin.clone();
        s.decision_explanation = "klajdi_anomaly_detected".into();
    }
    if ev.kind == "risk" {
        s.anomalies.push("klajdi_risk".into());
        s.risks.extend(vec_strings_from_payload(&ev.payload, "risks"));
    }
    s.updated_at = ev.timestamp;
}

async fn handle_asi(fabric: &SharedFabricState, ev: StigmaEvent) {
    let mut s = fabric.write().await;
    if ev.kind == "signal" {
        s.asi_signal = ev.payload["signal"].as_str().unwrap_or("stable").to_string();
    } else {
        s.asi_signal = ev.kind.clone();
    }
    match s.asi_signal.as_str() {
        "reroute" => {
            s.active_origin = s.fallback_origin.clone();
            s.decision_explanation = "asi_stigma_reroute".into();
        }
        "stable" => {
            s.active_origin = s.preferred_origin.clone();
            s.decision_explanation = "asi_stigma_stable".into();
        }
        _ => {}
    }
    s.updated_at = ev.timestamp;
}

// ─── dispatcher ────────────────────────────────────────────────────────────

async fn dispatch_event(
    fabric: &SharedFabricState,
    flow_fields: Arc<RwLock<FlowFields>>,
    impulse_mesh: Arc<RwLock<OceanImpulse>>,
    ev: StigmaEvent,
) {
    // 1) Update fabric state per-module
    match ev.source.as_str() {
        "ALBA" | "ALBI" | "JONA" => handle_trinity(fabric, ev.clone()).await,
        "MALI"    => handle_mali(fabric, ev.clone()).await,
        "BLERINA" => handle_blerina(fabric, ev.clone()).await,
        "LIAM"    => handle_liam(fabric, ev.clone()).await,
        "ALDA"    => handle_alda(fabric, ev.clone()).await,
        "KLAJDI"  => handle_klajdi(fabric, ev.clone()).await,
        "ASI"     => handle_asi(fabric, ev.clone()).await,
        "AGENT"   => {
            fabric.write().await.patterns.push("agent_task_submitted".into());
        }
        _ => {}
    }

    // 2) Update flow fields from stigma event
    {
        let mut fields = flow_fields.write().await;

        match ev.source.as_str() {
            "ALBA" | "ALBI" => {
                fields.tension += 0.5;
                if ev.kind == "anomaly" {
                    fields.protection += 0.3;
                }
            }
            "MALI" => {
                fields.pattern += ev.level as f64 * 0.2;
                if ev.kind == "prediction" && ev.level >= 3 {
                    fields.compute += 1.0;
                }
            }
            "BLERINA" => {
                fields.gap += ev.level as f64 * 0.3;
                if ev.level >= 4 {
                    fields.risk += 1.5;
                }
            }
            "LIAM" => {
                if ev.kind == "tensor" && ev.level >= 3 {
                    fields.compute += 0.8;
                }
                if ev.kind == "eigen" {
                    fields.pattern += 0.5;
                }
            }
            "ALDA" => {
                fields.load += ev.level as f64 * 0.2;
            }
            "KLAJDI" => {
                if ev.kind == "anomaly" || ev.kind == "risk" {
                    fields.risk += 0.8;
                }
            }
            "ASI" => {
                if ev.kind == "signal" {
                    let signal = ev.payload.get("signal").and_then(|v| v.as_str()).unwrap_or("");
                    if signal == "reroute" {
                        fields.origin_shift += 1.0;
                    }
                }
            }
            _ => {}
        }

        // 3) Resonance: fields influence each other
        resonate(&mut fields);

        // 4) Natural damping: homeostasis
        damp(&mut fields);
    }

    // 5) Ocean Core decision from resonance
    let impulse = {
        let fields = flow_fields.read().await;
        ocean_decision(&fields)
    };

    // 6) If impulse generated, guard it through JONA and apply it
    if let Some(impulse) = impulse {
        let safe_impulse = {
            let fields = flow_fields.read().await;
            let mesh = ImpulseMesh::new();
            mesh.jona.filter_impulse(impulse, &fields)
        };

        *impulse_mesh.write().await = safe_impulse.clone();

        let mut state = fabric.write().await;
        match safe_impulse.action.as_str() {
            "reroute" => {
                state.active_origin = state.fallback_origin.clone();
                state.decision_explanation = safe_impulse.reason;
            }
            "scale" => {
                state.asi_signal = "scale_up".into();
                state.decision_explanation = safe_impulse.reason;
            }
            "optimize" => {
                state.asi_signal = "optimize".into();
                state.decision_explanation = safe_impulse.reason;
            }
            "protect" => {
                state.asi_signal = "protect".into();
                state.decision_explanation = safe_impulse.reason;
            }
            "stabilize" => {
                state.asi_signal = "stabilize".into();
                state.decision_explanation = safe_impulse.reason;
            }
            _ => {}
        }
    }

    // 7) Capability routing: Check if event triggers autoscaling
    if let Some(cap_target) = capability_router(&ev) {
        trigger_autoscale(&cap_target.capability, cap_target.target_capacity).await;
    }
}

fn start_stigma_worker(app_state: AppState, mut rx: broadcast::Receiver<StigmaEvent>) {
    tokio::spawn(async move {
        while let Ok(ev) = rx.recv().await {
            dispatch_event(
                &app_state.fabric,
                app_state.flow_fields.clone(),
                app_state.impulse_mesh.clone(),
                ev,
            )
            .await;
        }
    });
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

/// Ocean Core Self-Report: Fabric consciousness with JONA filtering
async fn get_fabric_resonance(State(app_state): State<AppState>) -> Json<FabricSelfReport> {
    let fields = app_state.flow_fields.read().await;
    Json(build_self_report(&fields))
}

/// Get current FlowFields: Fabric's internal resonance state
async fn get_flow_fields(State(app_state): State<AppState>) -> Json<FlowFields> {
    Json(app_state.flow_fields.read().await.clone())
}

/// Get current OceanImpulse: Last decision broadcast
async fn get_ocean_impulse(State(app_state): State<AppState>) -> Json<OceanImpulse> {
    Json(app_state.impulse_mesh.read().await.clone())
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
            state.active_origin = state.preferred_origin.clone();
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
        state.preferred_origin = preferred.clone();
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
        state.active_origin = state.preferred_origin.clone();
        state.decision_explanation = payload.reason.clone().unwrap_or_else(|| "asi_stable".to_string());
    }

    let reason = payload.reason.unwrap_or_else(|| "none".to_string());
    let _ = app_state.stigma_bus.send(StigmaEvent {
        source: "ASI".to_string(),
        kind: payload.signal,
        level: 3,
        payload: serde_json::json!({ "reason": reason }),
        timestamp: Utc::now().to_rfc3339(),
    });

    Json(ApiResult {
        ok: true,
        message: format!("asi_signal_applied:{reason}"),
    })
}

async fn ingest_stigma(
    State(app_state): State<AppState>,
    Json(payload): Json<StigmaEvent>,
) -> Json<ApiResult> {
    let received_kind = payload.kind.clone();
    let _ = app_state.stigma_bus.send(payload);

    Json(ApiResult {
        ok: true,
        message: format!("stigma_received:{received_kind}"),
    })
}

async fn ingest_module_event(
    State(app_state): State<AppState>,
    source: &'static str,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    let event = StigmaEvent {
        source: source.to_string(),
        kind: payload.kind,
        level: payload.level,
        payload: payload.payload,
        timestamp: event_timestamp(payload.timestamp),
    };

    let _ = app_state.stigma_bus.send(event);

    Json(ApiResult {
        ok: true,
        message: format!("{source}_event_ingested"),
    })
}

async fn trinity_event(
    State(app_state): State<AppState>,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    ingest_module_event(State(app_state), "ALBA", Json(payload)).await
}

async fn mali_event(
    State(app_state): State<AppState>,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    ingest_module_event(State(app_state), "MALI", Json(payload)).await
}

async fn blerina_event(
    State(app_state): State<AppState>,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    ingest_module_event(State(app_state), "BLERINA", Json(payload)).await
}

async fn liam_event(
    State(app_state): State<AppState>,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    ingest_module_event(State(app_state), "LIAM", Json(payload)).await
}

async fn alda_event(
    State(app_state): State<AppState>,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    ingest_module_event(State(app_state), "ALDA", Json(payload)).await
}

async fn klajdi_event(
    State(app_state): State<AppState>,
    Json(payload): Json<GenericModuleEvent>,
) -> Json<ApiResult> {
    ingest_module_event(State(app_state), "KLAJDI", Json(payload)).await
}

async fn agent_submit(
    State(app_state): State<AppState>,
    Json(payload): Json<Value>,
) -> Json<ApiResult> {
    let _ = app_state.stigma_bus.send(StigmaEvent {
        source: "AGENT".to_string(),
        kind: "task_result".to_string(),
        level: 1,
        payload,
        timestamp: Utc::now().to_rfc3339(),
    });

    Json(ApiResult {
        ok: true,
        message: "agent_task_queued".to_string(),
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
    let preferred_origin = env::var("HQ_ORIGIN").unwrap_or_else(|_| "http://10.10.0.1:8000".to_string());
    let fallback_origin = env::var("FAILOVER_ORIGIN").unwrap_or_else(|_| "http://10.10.0.3:8000".to_string());
    let compute_origin = env::var("COMPUTE_ORIGIN").unwrap_or_else(|_| "http://10.10.0.2:8000".to_string());

    let (stigma_bus, stigma_rx) = create_stigma_bus();

    let app_state = AppState {
        fabric: Arc::new(RwLock::new(FabricState {
            preferred_origin: preferred_origin.clone(),
            active_origin: preferred_origin,
            fallback_origin,
            compute_origin,
            load: 0.1,
            latency_ms: 12,
            harmony: 90.0,
            asi_signal: "stable".to_string(),
            anomalies: Vec::new(),
            patterns: Vec::new(),
            gaps: Vec::new(),
            risks: Vec::new(),
            predictions: Vec::new(),
            decision_explanation: "initial_boot".to_string(),
            updated_at: Utc::now().to_rfc3339(),
        })),
        flow_fields: Arc::new(RwLock::new(FlowFields::new())),
            impulse_mesh: Arc::new(RwLock::new(OceanImpulse {
                action: "stabilize".into(),
                target: "fabric".into(),
                intensity: 1,
                reason: "initial_equilibrium".into(),
                timestamp: Utc::now().to_rfc3339(),
            })),
        latest_telemetry: Arc::new(RwLock::new(HashMap::new())),
        mesh_registry: Arc::new(RwLock::new(HashMap::new())),
        mesh_status: Arc::new(RwLock::new(HashMap::new())),
        stigma_bus,
    };

    start_stigma_worker(app_state.clone(), stigma_rx);

    let app = Router::new()
        .route("/health", get(health))
        .route("/fabric/state", get(get_fabric_state))
        .route("/fabric/explain", get(get_fabric_explain))
        .route("/fabric/resonance", get(get_fabric_resonance))
            .route("/fabric/flow", get(get_flow_fields))
            .route("/fabric/ocean/impulse", get(get_ocean_impulse))
        .route("/fabric/stigma", post(ingest_stigma))
        .route("/telemetry", post(ingest_telemetry))
        .route("/asi/signal", post(ingest_asi_signal))
        .route("/trinity/event", post(trinity_event))
        .route("/mali/event", post(mali_event))
        .route("/blerina/event", post(blerina_event))
        .route("/liam/event", post(liam_event))
        .route("/alda/event", post(alda_event))
        .route("/klajdi/event", post(klajdi_event))
        .route("/agents/submit", post(agent_submit))
        .route("/mesh/register", post(mesh_register))
        .route("/mesh/status", post(mesh_status))
        .with_state(app_state);

    let listener = TcpListener::bind("0.0.0.0:9000").await.unwrap();
    println!("ocean_core running on 0.0.0.0:9000");
    axum::serve(listener, app).await.unwrap();
}
