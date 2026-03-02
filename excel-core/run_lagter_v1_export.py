from __future__ import annotations

from pathlib import Path

from lagter_v1_excel import build_lagter_v1_excel


if __name__ == "__main__":
    output = Path("excel-core/output/lagter_v1_dashboard.xlsx")
    file_path = build_lagter_v1_excel(output)
    print(f"LAGTER v1 Excel exported: {file_path}")
