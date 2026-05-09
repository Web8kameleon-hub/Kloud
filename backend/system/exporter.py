from datetime import datetime
import json
from pathlib import Path

# Lazy import reportlab - only when needed
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    _REPORTLAB_AVAILABLE = True
except ImportError:
    _REPORTLAB_AVAILABLE = False
    A4 = None
    canvas = None

BASE = Path(__file__).resolve().parent
RUNTIME = BASE / "runtime"
TRIGGER_FILE = RUNTIME / "triggers.json"
SCAN_FILE = RUNTIME / "scan_results.json"
REPORTS = RUNTIME / "reports"

def generate_pdf_report():
    if not _REPORTLAB_AVAILABLE:
        raise ImportError("reportlab not installed. Install with: pip install reportlab")
    
    REPORTS.mkdir(exist_ok=True)
    report_name = f"kloud_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_path = REPORTS / report_name
    c = canvas.Canvas(str(report_path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "Kloud System Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    y = height - 100

    def write_line(txt, font="Helvetica", size=9, dy=12):
        nonlocal y
        if y < 100: c.showPage(); y = height - 100
        c.setFont(font, size)
        c.drawString(50, y, txt)
        y -= dy

    # Events
    if TRIGGER_FILE.exists():
        events = json.loads(TRIGGER_FILE.read_text(encoding="utf-8"))
        write_line("Recent Events:", "Helvetica-Bold", 11, 15)
        for e in reversed(events[-10:]):
            write_line(f"- [{e['category']}] {e['message']} ({e['readable_time']})")
    else:
        write_line("No trigger events found")

    # Scan results
    if SCAN_FILE.exists():
        data = json.loads(SCAN_FILE.read_text(encoding="utf-8"))
        write_line("", dy=20)
        write_line("Module Status:", "Helvetica-Bold", 11, 15)
        # support list or dict shapes
        if isinstance(data, dict) and data.get('modules') is None:
            for m, info in data.items():
                write_line(f"- {m}: CPU {info.get('cpu',0)}% | RAM {info.get('ram',0)}% | {info.get('status','unknown')}")
        else:
            modules = data.get('modules', []) if isinstance(data, dict) else []
            for m in modules:
                write_line(f"- {m.get('name')}: CPU {m.get('metrics',{}).get('cpu','?')}% | RAM {m.get('metrics',{}).get('ram','?')}% | {m.get('health',{}).get('status','unknown')}")
    else:
        write_line("", dy=20)
        write_line("No scan data found")

    c.save()
    return report_path


