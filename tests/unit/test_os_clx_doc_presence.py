from pathlib import Path


def test_os_clx_doc_exists() -> None:
    path = Path(__file__).resolve().parents[2] / "docs" / "fabric-p0" / "OS_CLX.md"
    assert path.exists(), "OS_CLX.md must exist for runtime contract baseline"
