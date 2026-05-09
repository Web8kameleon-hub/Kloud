from pathlib import Path
from email.message import EmailMessage
import smtplib, ssl, os, time

from backend.system.exporter import generate_pdf_report  # use the project exporter

# Env needed:
# SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
# REPORT_TO (default: amati.bau@gmail.com)
# REPORT_FROM (optional)

def send_daily_report():
    pdf_path = generate_pdf_report()  # creates PDF in runtime/reports/
    to_addr = os.getenv("REPORT_TO", "amati.bau@gmail.com")
    from_addr = os.getenv("REPORT_FROM", os.getenv("SMTP_USER", "no-reply@kloud.local"))

    msg = EmailMessage()
    msg["Subject"] = f"Kloud Daily System Report — {time.strftime('%Y-%m-%d')}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content("Përshëndetje,\n\nGjeni bashkëngjitur raportin ditor të Kloud.\n\n— Smart Orchestrator")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf",
                       filename=Path(pdf_path).name)

    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    pwd  = os.getenv("SMTP_PASS")

    if not (user and pwd):
        raise RuntimeError("Mungojnë SMTP_USER/SMTP_PASS në environment.")

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(user, pwd)
        server.send_message(msg)
    return pdf_path


