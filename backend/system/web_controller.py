from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn, json, time, os

from smart_scanner import SmartScanner
from auto_monitor import AutoMonitor
from exporter import Exporter

BASE = Path(__file__).resolve().parent
RUNTIME = BASE / "runtime"
RUNTIME.mkdir(exist_ok=True)
RESULTS = RUNTIME / "scan_results.json"

app = FastAPI(title="Smart Orchestrator (Kloud)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HTML = """
<!doctype html><html><head><meta charset="utf-8"><title>Kloud — Smart Orchestrator</title>
<style>
body{font-family:Arial;background:#0a0a0a;color:#e0e0e0;margin:0;padding:16px}
h1{color:#33ccff}
button{background:#33ccff;color:#001;padding:10px 16px;border:none;border-radius:8px;margin:6px;cursor:pointer}
table{border-collapse:collapse;width:100%;margin-top:14px}
th,td{border-bottom:1px solid #222;padding:8px;text-align:left}
.pill{padding:2px 8px;border-radius:10px}
.ok{background:#0d381a;color:#12e46b}.warn{background:#382d0d;color:#ffb400}.bad{background:#3a0d0d;color:#ff5f5f}
small{color:#9aa}
</style></head><body>
<h1>🧠 Kloud — Smart Orchestrator</h1>
<p>Skano automatikisht backend/frontend/docs/demo, monitoro për 10 sekonda dhe eksportoje raportin.</p>
<div>
  <button onclick="scan()">🔎 SCAN & MONITOR (10s)</button>
  <button onclick="exp('json')">📥 Export JSON</button>
  <button onclick="exp('cbor')">📥 Export CBOR</button>
  <button onclick="exp('pdf')">📄 Export PDF</button>
</div>
<div id="msg"></div>
<table id="tbl"><thead>
<tr><th>Module</th><th>Root</th><th>Type</th><th>Port</th><th>Health</th><th>CPU%</th><th>RAM%</th><th>Latency(ms)</th><th>Format</th><th>Updated</th></tr>
</thead><tbody></tbody></table>
<script>
async function load(){
  const r = await fetch('/results'); const data = await r.json();
  const tb = document.querySelector('#tbl tbody'); tb.innerHTML='';
  (data.modules||[]).forEach(m=>{
    const st = m.health && m.health.ok ? 'ok' : (m.health && m.health.status ? 'warn' : 'bad');
    const fmt = (m.intel && m.intel.format) ? m.intel.format : '';
    const row = `<tr>
      <td>${m.name}</td>
      <td><small>${m.root||''}</small></td>
      <td>${m.kind||''}</td>
      <td>${m.port||''}</td>
      <td><span class="pill ${st}">${m.health&&m.health.status?m.health.status:(m.health&&m.health.ok?'OK':'DOWN')}</span></td>
      <td>${m.metrics && m.metrics.cpu!=null ? m.metrics.cpu : ''}</td>
      <td>${m.metrics && m.metrics.ram!=null ? m.metrics.ram : ''}</td>
      <td>${m.metrics && m.metrics.latency_ms!=null ? m.metrics.latency_ms : ''}</td>
      <td>${fmt}</td>
      <td>${m.updated ? new Date(m.updated*1000).toLocaleTimeString() : ''}</td>
    </tr>`;
    tb.innerHTML += row;
  });
}
async function scan(){
  document.getElementById('msg').innerText='Duke skanuar dhe monitoruar (10s)...';
  const r = await fetch('/scan', {method:'POST'});
  const j = await r.json();
  document.getElementById('msg').innerText = 'Scan done: '+ (j.count||0)+' module';
  load();
}
async function exp(fmt){
  const w = window.open('/export/'+fmt, '_blank');
}
load(); setInterval(load, 5000);
</script>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML

@app.get("/results")
def results():
    if RESULTS.exists():
        return JSONResponse(json.loads(RESULTS.read_text(encoding="utf-8")))
    return JSONResponse({"modules": [], "generated_at": time.time()})

@app.post("/scan")
def scan():
    scanner = SmartScanner()
    modules = scanner.scan_all()             # zbulim automatik i moduleve + porta/health endpoints
    monitor = AutoMonitor()
    measured = monitor.observe(modules, duration_sec=10)  # monitorim real 10s
    payload = {"modules": measured, "generated_at": time.time()}
    RESULTS.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"ok": True, "count": len(measured)}

@app.get("/export/json")
def export_json():
    if not RESULTS.exists(): raise HTTPException(404, "No results")
    return Response(RESULTS.read_bytes(), media_type="application/json", headers={
        "Content-Disposition": "attachment; filename=kloud_report.json"
    })

@app.get("/export/cbor")
def export_cbor():
    if not RESULTS.exists(): raise HTTPException(404, "No results")
    exp = Exporter()
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    blob = exp.to_cbor(data)   # hedh gabim të qartë nëse s’ke cbor2
    return Response(blob, media_type="application/cbor", headers={
        "Content-Disposition": "attachment; filename=kloud_report.cbor"
    })

@app.get("/export/pdf")
def export_pdf():
    if not RESULTS.exists(): raise HTTPException(404, "No results")
    exp = Exporter()
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    pdf_path = exp.to_pdf(data, out_dir=RUNTIME / "reports")
    return Response(open(pdf_path, "rb").read(), media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={Path(pdf_path).name}"
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5555)


