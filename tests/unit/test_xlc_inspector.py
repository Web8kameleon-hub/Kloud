"""Tests XLC Inspector — raport i detajuar për candidate/reference."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
XLC_DIR = ROOT / "ocean-core" / "xlc"
if str(XLC_DIR) not in sys.path:
    sys.path.insert(0, str(XLC_DIR))

from xlc_inspector import XLCInspector  # type: ignore

INSPECTOR = XLCInspector()


def test_same_sequence_opens_true() -> None:
    report = INSPECTOR.inspect("CLX", "CLX")
    assert report.opened is True
    assert abs(report.combined - 1.0) < 1e-9


def test_different_sequence_opens_false_at_strict_threshold() -> None:
    report = INSPECTOR.inspect("CLY", "CLX", threshold=0.9999)
    assert report.opened is False
    assert report.combined < 1.0


def test_direct_question_is_filtered_to_known_symbols() -> None:
    report = INSPECTOR.inspect("A je CLX?", "CLX")
    assert report.candidate_sequence == "AJECLX"
    assert report.reference_sequence == "CLX"


def test_report_contains_real_timings() -> None:
    report = INSPECTOR.inspect("CLX", "CLX")
    assert report.build_candidate_ns > 0
    assert report.build_reference_ns > 0
    assert report.compare_ns > 0
    assert report.inspect_ns > 0


def test_report_json_is_valid_and_has_opened() -> None:
    report = INSPECTOR.inspect("CLX", "CLX")
    payload = json.loads(report.to_json())
    assert payload["opened"] is True
    assert "sim_cc" in payload


def test_invalid_threshold_raises() -> None:
    with pytest.raises(ValueError):
        INSPECTOR.inspect("CLX", "CLX", threshold=0.0)


def test_scan_mode_detects_keyword_inside_sentence() -> None:
    report = INSPECTOR.inspect_scan("A je CLX?", "CLX", threshold=0.9999)
    assert report.scan_mode is True
    assert report.source_sequence == "AJECLX"
    assert report.candidate_sequence == "CLX"
    assert report.opened is True
    assert report.windows_evaluated > 0


def test_scan_mode_keeps_non_match_closed() -> None:
    report = INSPECTOR.inspect_scan("A je CLY?", "CLX", threshold=0.9999)
    assert report.scan_mode is True
    assert report.opened is False
    assert report.candidate_sequence != "CLX"


def test_unicode_exact_match_opens_true() -> None:
    report = INSPECTOR.inspect("Привет", "Привет")
    assert report.opened is True
    assert report.candidate_sequence == "ПРИВЕТ"


def test_unicode_scan_mode_detects_cjk_keyword() -> None:
    report = INSPECTOR.inspect_scan("你好世界", "世界", threshold=0.9999)
    assert report.scan_mode is True
    assert report.candidate_sequence == "世界"
    assert report.opened is True
