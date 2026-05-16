"""
XLC Inspector — krahasim i thellë i dy sekuencave me raport observability.

Ky modul ndërton LayerStack për candidate/reference, llogarit similarity 3-shtresore
(WW, MM, CC), merr vendim me threshold dhe kthen raport të serializueshëm JSON.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict

from xlc_layers import LayerBuilder  # type: ignore


@dataclass(frozen=True)
class XLCInspectionReport:
    """Raport i plotë i inspektimit për observability/panel."""

    candidate_input: str
    reference_input: str
    candidate_sequence: str
    reference_sequence: str
    sim_ww: float
    sim_mm: float
    sim_cc: float
    combined: float
    threshold: float
    opened: bool
    build_candidate_ns: int
    build_reference_ns: int
    compare_ns: int
    inspect_ns: int
    source_sequence: str | None = None
    scan_mode: bool = False
    windows_evaluated: int = 1

    @property
    def resonance_score(self) -> float:
        """Alias semantik për combined similarity."""
        return self.combined

    def as_dict(self) -> Dict[str, Any]:
        return {
            "candidate_input": self.candidate_input,
            "reference_input": self.reference_input,
            "candidate_sequence": self.candidate_sequence,
            "reference_sequence": self.reference_sequence,
            "sim_ww": self.sim_ww,
            "sim_mm": self.sim_mm,
            "sim_cc": self.sim_cc,
            "combined": self.combined,
            "threshold": self.threshold,
            "opened": self.opened,
            "build_candidate_ns": self.build_candidate_ns,
            "build_reference_ns": self.build_reference_ns,
            "compare_ns": self.compare_ns,
            "inspect_ns": self.inspect_ns,
            "source_sequence": self.source_sequence,
            "scan_mode": self.scan_mode,
            "windows_evaluated": self.windows_evaluated,
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=True, separators=(",", ":"))


class XLCInspector:
    """Inspector për pyetje direkte dhe krahasim me sekuencë reference."""

    def __init__(self, builder: LayerBuilder | None = None) -> None:
        self._builder = builder if builder is not None else LayerBuilder()

    def inspect(
        self,
        candidate_text: str,
        reference_text: str,
        threshold: float = 0.9999,
    ) -> XLCInspectionReport:
        """Krahason candidate kundrejt reference dhe kthen raport të plotë."""
        if not (0.0 < threshold <= 1.0):
            raise ValueError("threshold duhet të jetë në (0.0, 1.0]")

        t0 = time.perf_counter_ns()

        t_build_candidate_start = time.perf_counter_ns()
        candidate_stack = self._builder.build(candidate_text)
        t_build_candidate_end = time.perf_counter_ns()

        t_build_reference_start = time.perf_counter_ns()
        reference_stack = self._builder.build(reference_text)
        t_build_reference_end = time.perf_counter_ns()

        sim = candidate_stack.similarity_with(reference_stack)
        opened = sim.opens_at(threshold)

        t1 = time.perf_counter_ns()

        return XLCInspectionReport(
            candidate_input=candidate_text,
            reference_input=reference_text,
            candidate_sequence=candidate_stack.sequence,
            reference_sequence=reference_stack.sequence,
            sim_ww=sim.sim_ww,
            sim_mm=sim.sim_mm,
            sim_cc=sim.sim_cc,
            combined=sim.combined,
            threshold=threshold,
            opened=opened,
            build_candidate_ns=t_build_candidate_end - t_build_candidate_start,
            build_reference_ns=t_build_reference_end - t_build_reference_start,
            compare_ns=sim.compare_ns,
            inspect_ns=t1 - t0,
            source_sequence=candidate_stack.sequence,
            scan_mode=False,
            windows_evaluated=1,
        )

    def inspect_scan(
        self,
        candidate_text: str,
        reference_text: str,
        threshold: float = 0.9999,
        max_extra_window: int = 2,
    ) -> XLCInspectionReport:
        """Skannon sekuencën candidate me dritare për të kapur keyword rezonante.

        E dobishme për pyetje të gjata ku fjala kyçe është e embeduar,
        p.sh. "A je CLX?" kundrejt reference "CLX".
        """
        if not (0.0 < threshold <= 1.0):
            raise ValueError("threshold duhet të jetë në (0.0, 1.0]")
        if max_extra_window < 0:
            raise ValueError("max_extra_window duhet të jetë >= 0")

        t0 = time.perf_counter_ns()

        t_build_reference_start = time.perf_counter_ns()
        reference_stack = self._builder.build(reference_text)
        t_build_reference_end = time.perf_counter_ns()

        source_sequence = self._builder.normalize_text(candidate_text)
        if not source_sequence:
            raise ValueError(
                f"sekuenca '{candidate_text}' nuk ka asnjë simbol të njohur në alfabet"
            )

        ref_len = len(reference_stack.sequence)
        min_w = max(1, ref_len)
        max_w = min(len(source_sequence), ref_len + max_extra_window)

        # Kandidati është shumë i shkurtër — asnjë dritare e mundshme
        if max_w < min_w or len(source_sequence) < min_w:
            t1 = time.perf_counter_ns()
            dummy_stack = self._builder.build(source_sequence)
            sim = dummy_stack.similarity_with(reference_stack)
            return XLCInspectionReport(
                candidate_input=candidate_text,
                reference_input=reference_text,
                candidate_sequence=dummy_stack.sequence,
                reference_sequence=reference_stack.sequence,
                sim_ww=sim.sim_ww,
                sim_mm=sim.sim_mm,
                sim_cc=sim.sim_cc,
                combined=sim.combined,
                threshold=threshold,
                opened=False,
                build_candidate_ns=0,
                build_reference_ns=t_build_reference_end - t_build_reference_start,
                compare_ns=sim.compare_ns,
                inspect_ns=t1 - t0,
                source_sequence=source_sequence,
                scan_mode=True,
                windows_evaluated=0,
            )

        best_report: XLCInspectionReport | None = None
        windows = 0

        for w in range(min_w, max_w + 1):
            for i in range(0, len(source_sequence) - w + 1):
                windows += 1
                candidate_slice = source_sequence[i : i + w]
                t_build_candidate_start = time.perf_counter_ns()
                candidate_stack = self._builder.build(candidate_slice)
                t_build_candidate_end = time.perf_counter_ns()

                sim = candidate_stack.similarity_with(reference_stack)
                opened = sim.opens_at(threshold)

                current = XLCInspectionReport(
                    candidate_input=candidate_text,
                    reference_input=reference_text,
                    candidate_sequence=candidate_stack.sequence,
                    reference_sequence=reference_stack.sequence,
                    sim_ww=sim.sim_ww,
                    sim_mm=sim.sim_mm,
                    sim_cc=sim.sim_cc,
                    combined=sim.combined,
                    threshold=threshold,
                    opened=opened,
                    build_candidate_ns=t_build_candidate_end - t_build_candidate_start,
                    build_reference_ns=t_build_reference_end - t_build_reference_start,
                    compare_ns=sim.compare_ns,
                    inspect_ns=0,
                    source_sequence=source_sequence,
                    scan_mode=True,
                    windows_evaluated=0,
                )

                if best_report is None or current.combined > best_report.combined:
                    best_report = current

        t1 = time.perf_counter_ns()
        assert best_report is not None
        return XLCInspectionReport(
            candidate_input=best_report.candidate_input,
            reference_input=best_report.reference_input,
            candidate_sequence=best_report.candidate_sequence,
            reference_sequence=best_report.reference_sequence,
            sim_ww=best_report.sim_ww,
            sim_mm=best_report.sim_mm,
            sim_cc=best_report.sim_cc,
            combined=best_report.combined,
            threshold=best_report.threshold,
            opened=best_report.opened,
            build_candidate_ns=best_report.build_candidate_ns,
            build_reference_ns=best_report.build_reference_ns,
            compare_ns=best_report.compare_ns,
            inspect_ns=t1 - t0,
            source_sequence=source_sequence,
            scan_mode=True,
            windows_evaluated=windows,
        )
