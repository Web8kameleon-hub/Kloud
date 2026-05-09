"""
💠 Smart Orchestrator + NeuroTrigger Integration
UI port: 5555
Skana, monitoron dhe reagon në kohë reale
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
import threading, time, json, os
from pathlib import Path
from datetime import datetime
from backend.system.neuro_trigger import NeuroTrigger
from backend.system.exporter import generate_pdf_report
from backend.system.email_reporter import send_daily_report
# include NeuroReset router so /neuro/* endpoints are available on this orchestrator
from backend.system.neuro_reset import router as neuro_reset_router

app = FastAPI(title="Kloud Orchestrator 5555")

# mount neuro reset API
app.include_router(neuro_reset_router)

BASE = Path(__file__).resolve().parent
RUNTIME = BASE / "runtime"
TRIGGER_FILE = RUNTIME / "triggers.json"
SCAN_FILE = RUNTIME / "scan_results.json"
REPORTS = RUNTIME / "reports"
RUNTIME.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

trigger = NeuroTrigger()


@app.get("/", response_class=HTMLResponse)
def dashboard():
        events = load_events()
        scan_data = load_scan()
        reports = list_recent_reports()
        event_summary = summarize_events(events)
        module_summary = summarize_modules(scan_data)
        now_txt = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        event_cards = render_event_timeline(events)
        module_cards = render_module_grid(scan_data)
        report_cards = render_report_list(reports)

        html = f"""
        <html>
        <head>
            <meta http-equiv="refresh" content="15" />
            <title>Kloud Orchestrator 5555</title>
            <style>
                :root {{
                    color-scheme: dark;
                    --bg: #05060a;
                    --card: #12131a;
                    --accent: #4c6ef5;
                    --accent-soft: rgba(76, 110, 245, 0.2);
                    --danger: #ff6b6b;
                    --warning: #f08c00;
                    --success: #51cf66;
                    --text: #f1f3f5;
                    --muted: #868e96;
                }}
                body {{
                    font-family: "Segoe UI", Arial, sans-serif;
                    background: var(--bg);
                    color: var(--text);
                    margin: 0;
                    padding: 24px;
                }}
                h1, h2, h3 {{ margin: 0 0 12px 0; }}
                a {{ color: var(--accent); }}
                .header {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:16px; margin-bottom:24px; }}
                .summary-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin-bottom:24px; }}
                .summary-card {{ background: var(--card); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:16px; box-shadow:0 8px 18px rgba(0,0,0,0.25); }}
                .summary-card span.label {{ display:block; font-size:13px; text-transform:uppercase; letter-spacing:0.08em; color:var(--muted); margin-bottom:8px; }}
                .summary-card span.value {{ font-size:28px; font-weight:600; }}
                .summary-card span.meta {{ display:block; margin-top:6px; font-size:13px; color:var(--muted); }}
                .actions {{ display:flex; flex-wrap:wrap; gap:12px; }}
                .actions button {{
                    background: var(--accent);
                    color: white;
                    border: none;
                    padding: 10px 18px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                }}
                .actions button.secondary {{ background: rgba(241, 243, 245, 0.08); color: var(--text); }}
                .actions button:hover {{ filter: brightness(1.08); }}
                section {{
                    background: var(--card);
                    border-radius: 12px;
                    border: 1px solid rgba(255,255,255,0.05);
                    padding: 18px;
                    margin-bottom: 18px;
                }}
                section h3 {{ display:flex; justify-content:space-between; align-items:center; font-size:18px; margin-bottom:12px; }}
                .timeline {{ display:flex; flex-direction:column; gap:10px; }}
                .timeline-item {{
                    background: rgba(255, 255, 255, 0.04);
                    border-radius: 8px;
                    padding: 12px 14px;
                    border-left: 4px solid var(--accent);
                }}
                .timeline-item.error {{ border-left-color: var(--danger); }}
                .timeline-item.warn {{ border-left-color: var(--warning); }}
                .timeline-item small {{ display:block; color:var(--muted); margin-top:6px; font-size:12px; }}
                .module-grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:12px; }}
                .module-card {{ background: rgba(255,255,255,0.04); border-radius:10px; padding:14px; border:1px solid rgba(255,255,255,0.05); position:relative; }}
                .module-card .status {{ font-size:13px; color:var(--muted); margin-bottom:6px; }}
                .module-card .metrics {{ font-size:13px; color:var(--muted); margin-top:8px; }}
                .pill {{ display:inline-block; padding:4px 8px; border-radius:999px; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.04em; }}
                .pill.ok {{ background: rgba(81, 207, 102, 0.18); color: var(--success); }}
                .pill.warn {{ background: rgba(240, 140, 0, 0.18); color: var(--warning); }}
                .pill.err {{ background: rgba(255, 107, 107, 0.18); color: var(--danger); }}
                .heal-btn {{ margin-top:10px; display:inline-flex; align-items:center; gap:6px; background:var(--accent-soft); color:var(--accent); border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; }}
                .heal-btn:hover {{ background: rgba(76,110,245,0.3); }}
                .reports ul {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:8px; }}
                .reports li {{ display:flex; justify-content:space-between; padding:10px 12px; background:rgba(255,255,255,0.04); border-radius:8px; font-size:13px; }}
                .empty {{ color: var(--muted); font-style: italic; }}
                @media (max-width: 600px) {{ body {{ padding:16px; }} }}
            </style>
            <script>
                async function triggerHeal(moduleName) {{
                    const btn = document.querySelector(`[data-module="${{moduleName}}"]`);
                    if (!btn) return;
                    btn.disabled = true;
                    btn.textContent = "Healing...";
                    try {{
                        const res = await fetch('/api/heal', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}},
                            body: JSON.stringify({{ module: moduleName }})
                        }});
                        const payload = await res.json();
                        btn.textContent = payload.result || 'Triggered';
                        btn.classList.add('secondary');
                    }} catch (err) {{
                        btn.textContent = 'Failed';
                    }}
                    setTimeout(() => window.location.reload(), 2000);
                }}
            </script>
        </head>
        <body>
            <div class="header">
                <div>
                    <h1>🧠 Kloud Smart Orchestrator</h1>
                      <p style="color:var(--muted);">NeuroTrigger Active &bull; Last refresh {now_txt}</p>
                </div>
                <div class="actions">
                    <button onclick="window.location='/api/export/pdf'">📄 Export PDF</button>
                      <button class="secondary" onclick="fetch('/api/send-now', {{method: 'POST'}}).then(()=>alert('Report send triggered'))">Send Daily Report</button>
                    <button class="secondary" onclick="window.location='/docs'">API Docs</button>
                </div>
            </div>

            <div class="summary-grid">
                <div class="summary-card">
                    <span class="label">Total Events</span>
                    <span class="value">{event_summary['total']}</span>
                                <span class="meta">Errors {event_summary['errors']} &bull; Warnings {event_summary['warnings']}</span>
                                <span class="meta">Last event: {event_summary['last_seen']}</span>
                </div>
                <div class="summary-card">
                    <span class="label">Modules Monitored</span>
                    <span class="value">{module_summary['total']}</span>
                                <span class="meta">Healthy {module_summary['healthy']} &bull; Attention {module_summary['attention']}</span>
                                <span class="meta">Avg CPU {module_summary['avg_cpu']}% &bull; Avg RAM {module_summary['avg_ram']}%</span>
                </div>
                <div class="summary-card">
                    <span class="label">Auto-Heal triggers</span>
                    <span class="value">{event_summary['auto_heal']}</span>
                    <span class="meta">Within last 24h</span>
                </div>
                <div class="summary-card">
                    <span class="label">Reports</span>
                    <span class="value">{len(reports)}</span>
                    <span class="meta">Newest: {report_cards['latest']}</span>
                </div>
            </div>

            <section>
                <h3>Recent System Events<span style="color:var(--muted); font-size:13px;">Last 10 entries</span></h3>
                {event_cards['html']}
            </section>

            <section>
            <h3>Modules</h3>
                {module_cards}
            </section>

            <section class="reports">
                        <h3>Latest Reports</h3>
                {report_cards['html']}
            </section>
        </body>
        </html>
        """
        return HTMLResponse(html)


@app.get("/api/events")
def get_events():
    if TRIGGER_FILE.exists():
        data = json.loads(TRIGGER_FILE.read_text(encoding="utf-8"))
        return JSONResponse(data)
    return JSONResponse([])


@app.get("/api/scan")
def get_scan():
    if SCAN_FILE.exists():
        data = json.loads(SCAN_FILE.read_text(encoding="utf-8"))
        return JSONResponse(data)
    return JSONResponse([])


@app.post("/api/heal")
async def heal_now(request: Request):
    data = await request.json()
    module = data.get("module")
    if not module:
        return JSONResponse({"error": "missing module"}, status_code=400)
    result = trigger.restart_module(module)
    return JSONResponse({"result": result})


@app.get("/api/export/pdf")
def export_pdf():
    """Gjeneron raport PDF automatik"""
    report_path = generate_pdf_report()
    return FileResponse(report_path, media_type="application/pdf", filename=report_path.name)


@app.post("/api/send-now")
def send_now():
    """Trigger send of the daily PDF report immediately (for testing/manual send)."""
    path = send_daily_report()
    return {"ok": True, "file": str(path)}


@app.get("/reports/{filename}")
def download_report(filename: str):
    target = (REPORTS / filename).resolve()
    if not target.exists() or REPORTS not in target.parents:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(target, media_type="application/pdf", filename=target.name)


def load_events():
    if not TRIGGER_FILE.exists():
        return []
    try:
        return json.loads(TRIGGER_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def load_scan():
    if not SCAN_FILE.exists():
        return {}
    try:
        return json.loads(SCAN_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def summarize_events(events):
    errors = sum(1 for e in events if "error" in e.get("category", "").lower())
    warnings = sum(1 for e in events if "warn" in e.get("category", "").lower())
    auto_heal = sum(1 for e in events if "restart" in e.get("message", "").lower())
    last_seen = events[-1]["readable_time"] if events else "—"
    return {
        "total": len(events),
        "errors": errors,
        "warnings": warnings,
        "auto_heal": auto_heal,
        "last_seen": last_seen,
    }


def summarize_modules(modules):
    total = len(modules)
    healthy = 0
    attention = 0
    cpu_total = 0.0
    ram_total = 0.0
    for info in modules.values():
        status = str(info.get("status", "unknown")).lower()
        if status in {"active", "healthy", "ok"}:
            healthy += 1
        else:
            attention += 1
        cpu_total += float(info.get("cpu", 0) or 0)
        ram_total += float(info.get("ram", 0) or 0)
    divisor = max(total, 1)
    return {
        "total": total,
        "healthy": healthy,
        "attention": attention,
        "avg_cpu": round(cpu_total / divisor, 1),
        "avg_ram": round(ram_total / divisor, 1),
    }


def render_event_timeline(events):
    if not events:
        return {"html": "<p class='empty'>No trigger events yet</p>"}
    items = []
    for event in reversed(events[-10:]):
        level = ""
        category = str(event.get("category", "")).lower()
        if "error" in category:
            level = "error"
        elif "warn" in category:
            level = "warn"
        severity_cls = level or "ok"
        message = event.get("message", "")
        items.append(
            f"<div class='timeline-item {severity_cls}'><strong>{event.get('category','N/A')}</strong><br>{message}<small>{event.get('readable_time','')}</small></div>"
        )
    return {"html": "<div class='timeline'>" + "".join(items) + "</div>"}


def render_module_grid(modules):
    if not modules:
        return "<p class='empty'>No module telemetry yet</p>"
    cards = []
    for name, info in modules.items():
        status = str(info.get("status", "unknown")).lower()
        pill_class = "ok"
        if status in {"degraded", "warn", "warning"}:
            pill_class = "warn"
        elif status in {"error", "offline", "critical"}:
            pill_class = "err"
        title = info.get("status", "Unknown").title()
        cpu = info.get("cpu", 0)
        ram = info.get("ram", 0)
        lat = info.get("latency", info.get("latency_ms"))
        latency_txt = f" &bull; Latency {lat}ms" if lat is not None else ""
        cards.append(
            """
            <div class='module-card'>
              <div class='status'><span class='pill {pill}'>{title}</span></div>
              <h4>{name}</h4>
              <div class='metrics'>CPU {cpu}% &bull; RAM {ram}%{latency}</div>
              <button class='heal-btn' data-module='{name}' onclick="triggerHeal('{name}')">&#9881; Heal Now</button>
            </div>
            """.format(pill=pill_class, name=name, title=title, cpu=cpu, ram=ram, latency=latency_txt)
        )
    return "<div class='module-grid'>" + "".join(cards) + "</div>"


def list_recent_reports(limit: int = 5):
    if not REPORTS.exists():
        return []
    reports = sorted(REPORTS.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    return reports[:limit]


def render_report_list(reports):
    if not reports:
        return {"html": "<p class='empty'>No reports generated yet</p>", "latest": "—"}
    items = []
    latest = "—"
    for idx, path in enumerate(reports):
        ts = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        url = f"/reports/{path.name}"
        items.append(f"<li><span>{path.name}</span><span>{ts} &bull; <a href='{url}'>Download</a></span></li>")
        if idx == 0:
            latest = ts
    return {"html": "<ul>" + "".join(items) + "</ul>", "latest": latest}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)


