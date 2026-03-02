from __future__ import annotations

from pathlib import Path

from lagter_v1_excel import LagterV1ExcelBuilder


def run_test() -> None:
    builder = LagterV1ExcelBuilder()
    payload = builder.build_payload()
    validated = builder.validate_payload(payload)

    assert validated["version"] == "v1"
    assert len(validated["kpis"]) > 0
    assert len(validated["law_checks"]) == 3
    assert len(builder.process_map()) >= 6

    output = Path("excel-core/output/lagter_v1_test.xlsx")
    builder.write_workbook(output, validated)
    assert output.exists()

    print("LAGTER v1 test passed")


if __name__ == "__main__":
    run_test()
