"""Generate a PDF telemetry report from logs."""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Iterable, List

import matplotlib
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402  # pylint: disable=wrong-import-order

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "telemetry.jsonl"
REPORT_FILE = BASE_DIR / "reports" / "telemetry_report.pdf"
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

REQUIRED_COLUMNS = {"function", "duration_ms", "input_bytes", "output_bytes"}


def load_logs() -> pd.DataFrame:
    """Load telemetry rows from the JSONL log file."""
    if not LOG_FILE.exists():
        print(f"Log file not found at {LOG_FILE}")
        return pd.DataFrame()

    records: List[dict] = []
    with LOG_FILE.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def _figure_to_image_buffer(fig) -> BytesIO:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def create_charts(df: pd.DataFrame) -> List[BytesIO]:
    charts: List[BytesIO] = []

    if {"function", "duration_ms"}.issubset(df.columns) and not df.empty:
        avg_duration = df.groupby("function")["duration_ms"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4))
        avg_duration.plot(kind="barh", ax=ax, color="#2E86AB")
        ax.set_title("Average duration per function (ms)")
        ax.set_xlabel("Duration (ms)")
        charts.append(_figure_to_image_buffer(fig))

    if {"function", "input_bytes", "output_bytes"}.issubset(df.columns) and not df.empty:
        summary = (
            df.groupby("function")
            .agg(avg_input=("input_bytes", "mean"), avg_output=("output_bytes", "mean"))
            .sort_index()
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        summary.plot(kind="bar", ax=ax, color={"avg_input": "#E07A5F", "avg_output": "#3D5A80"})
        ax.set_title("Average payload size (bytes)")
        ax.set_ylabel("Bytes")
        charts.append(_figure_to_image_buffer(fig))

    return charts


def _build_summary_table(df: pd.DataFrame) -> Table | None:
    if not {"function"}.issubset(df.columns):
        return None

    agg_columns = {"function": ("function", "count")}
    if "duration_ms" in df:
        agg_columns["avg_ms"] = ("duration_ms", "mean")
    if "input_bytes" in df:
        agg_columns["avg_in"] = ("input_bytes", "mean")
    if "output_bytes" in df:
        agg_columns["avg_out"] = ("output_bytes", "mean")

    summary = (
        df.groupby("function")
        .agg(**agg_columns)
        .rename(columns={"function": "calls"})
        .round(2)
        .reset_index()
    )

    headers = list(summary.columns)
    rows: List[Iterable] = summary.values.tolist()
    table = Table([headers, *rows])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ]
        )
    )
    return table


def build_report(df: pd.DataFrame, charts: Iterable[BytesIO]) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(REPORT_FILE), pagesize=A4)
    elements = [
        Paragraph("kloud Telemetry Report", styles["Title"]),
        Paragraph(f"Generated: {datetime.utcnow().isoformat()} UTC", styles["Normal"]),
        Spacer(1, 12),
    ]

    if df.empty:
        elements.append(Paragraph("No telemetry entries were found.", styles["Normal"]))
        doc.build(elements)
        print(f"Report saved to: {REPORT_FILE}")
        return

    total_duration_s = df["duration_ms"].sum() / 1000 if "duration_ms" in df else 0
    total_bytes = 0
    if "input_bytes" in df:
        total_bytes += df["input_bytes"].sum()
    if "output_bytes" in df:
        total_bytes += df["output_bytes"].sum()
    throughput = (total_bytes / total_duration_s) if total_duration_s > 0 else 0

    unique_functions = df["function"].nunique() if "function" in df else 0
    total_calls = len(df)

    elements.extend(
        [
            Paragraph(f"Functions analysed: {unique_functions}", styles["Normal"]),
            Paragraph(f"Total invocations: {total_calls}", styles["Normal"]),
            Paragraph(f"Average throughput: {throughput / 1024:.2f} KB/s", styles["Normal"]),
            Spacer(1, 12),
        ]
    )

    for chart in charts:
        elements.append(Image(chart, width=400, height=250))
        elements.append(Spacer(1, 12))

    summary_table = _build_summary_table(df)
    if summary_table is not None:
        elements.append(Paragraph("Function summary:", styles["Heading2"]))
        elements.append(summary_table)

    doc.build(elements)
    print(f"Report saved to: {REPORT_FILE}")


def main() -> None:
    df = load_logs()
    charts = create_charts(df) if not df.empty else []
    build_report(df, charts)


if __name__ == "__main__":
    main()


