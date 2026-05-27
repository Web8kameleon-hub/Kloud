from __future__ import annotations

import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS = [
    re.compile(r"\b_get_mock_\w+"),
    re.compile(r"return mock data", re.IGNORECASE),
    re.compile(r"returning mock", re.IGNORECASE),
    re.compile(r"for now, return mock data", re.IGNORECASE),
    re.compile(r"generate reasonable demo data", re.IGNORECASE),
    re.compile(r"fallback.*simulat", re.IGNORECASE),
    re.compile(r"Replace with sensor data", re.IGNORECASE),
]

SCAN_ROOTS = [
    Path("apps/api"),
]

ALLOWLIST = {
    Path("scripts/ci/check_no_fake.py"),
}


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for file_path in root.rglob("*.py"):
            relative = file_path.as_posix()
            if "__pycache__" in relative or ".mypy_cache" in relative:
                continue
            files.append(file_path)
    return files


def main() -> int:
    violations: list[str] = []
    for file_path in iter_python_files():
        relative = Path(file_path.as_posix())
        if relative in ALLOWLIST:
            continue
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError as exc:
            violations.append(f"{file_path}:0: unreadable: {exc}")
            continue
        for line_number, line in enumerate(lines, start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        f"{file_path}:{line_number}: forbidden no-fake pattern: {line.strip()}"
                    )
                    break

    if violations:
        print("No fake gate failed:")
        for violation in violations:
            print(violation)
        return 1

    print("No fake gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
