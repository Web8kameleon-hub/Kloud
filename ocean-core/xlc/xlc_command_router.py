"""
XLCCommandRouter — ruter komandash mbi XLC Resonance Engine.

Regjistron komanda si fjalë kyçe (p.sh. "START", "RESET", "MODE_WWW_MMM"),
skanon tekstin input me inspect_scan dhe kthen komandën me rezonancën më të lartë.

Rregulla:
- NO_FAKE_DATA: çdo similarity nga dot-product real; nëse asnjë komandë nuk kalon
  threshold kthen route_name=None, raporti ka opened=False.
- Nanoide (perf_counter_ns) maten për çdo operacion.
- Nuk ka fallback/mock data.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from xlc_inspector import XLCInspectionReport, XLCInspector  # type: ignore
from xlc_layers import LayerBuilder  # type: ignore


@dataclass(frozen=True)
class RouteResult:
    """Rezultat i plotë i routing-ut për observability."""

    input_text: str
    route_name: Optional[str]          # None nëse asnjë komandë nuk hapet
    report: Optional[XLCInspectionReport]  # raporti i komandës fituesë
    all_scores: Dict[str, float]        # {command: combined} për çdo komandë
    router_ns: int                      # kohëzgjatja totale e routing-ut

    @property
    def matched(self) -> bool:
        return self.route_name is not None

    def as_dict(self) -> dict:
        return {
            "input_text": self.input_text,
            "route_name": self.route_name,
            "matched": self.matched,
            "report": self.report.as_dict() if self.report else None,
            "all_scores": self.all_scores,
            "router_ns": self.router_ns,
        }


class XLCCommandRouter:
    """
    Router i komandave bazuar në XLC resonance scan.

    Shembull:
        router = XLCCommandRouter()
        router.register("START")
        router.register("RESET")
        router.register("MODE_WWW")

        result = router.route("A je START tani")
        # result.route_name == "START", result.matched == True
        # result.report.opened == True, result.report.scan_mode == True
    """

    def __init__(
        self,
        builder: LayerBuilder | None = None,
        threshold: float = 0.9999,
        max_extra_window: int = 2,
    ) -> None:
        if not (0.0 < threshold <= 1.0):
            raise ValueError("threshold duhet të jetë në (0.0, 1.0]")
        if max_extra_window < 0:
            raise ValueError("max_extra_window duhet të jetë >= 0")

        self._builder = builder if builder is not None else LayerBuilder()
        self._inspector = XLCInspector(builder=self._builder)
        self._threshold = threshold
        self._max_extra_window = max_extra_window
        # ruajmë listë të renditur sipas regjistrimit për determinizëm
        self._commands: List[str] = []

    # ------------------------------------------------------------------
    # Regjistrim
    # ------------------------------------------------------------------

    def register(self, command: str) -> "XLCCommandRouter":
        """Regjistron një komandë si fjalë kyçe rezonante.

        Kthen self për method-chaining.
        Heq karaktere jo-shkronja nga komanda dhe ruan skriptet Unicode.
        """
        if not command:
            raise ValueError("command nuk mund të jetë bosh")
        normalized = self._builder.normalize_text(command)
        if not normalized:
            raise ValueError(
                f"command '{command}' nuk ka asnjë shkronjë të vlefshme"
            )
        if normalized not in self._commands:
            self._commands.append(normalized)
        return self

    def register_many(self, commands: List[str]) -> "XLCCommandRouter":
        """Regjistron shumë komanda njëkohësisht."""
        for c in commands:
            self.register(c)
        return self

    @property
    def commands(self) -> Tuple[str, ...]:
        """Lista e komandave të regjistruara (read-only)."""
        return tuple(self._commands)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def route(self, input_text: str) -> RouteResult:
        """Skanon input_text dhe kthen komandën me rezonancën më të lartë.

        Nëse asnjë komandë nuk arrin threshold, route_name=None, matched=False.
        """
        if not self._commands:
            raise RuntimeError(
                "XLCCommandRouter nuk ka komanda të regjistruara; "
                "thirr router.register('COMMAND') para route()"
            )

        t0 = time.perf_counter_ns()

        best_name: Optional[str] = None
        best_report: Optional[XLCInspectionReport] = None
        all_scores: Dict[str, float] = {}

        for cmd in self._commands:
            report = self._inspector.inspect_scan(
                candidate_text=input_text,
                reference_text=cmd,
                threshold=self._threshold,
                max_extra_window=self._max_extra_window,
            )
            all_scores[cmd] = report.combined

            if best_report is None or report.combined > best_report.combined:
                best_report = report
                best_name = cmd

        t1 = time.perf_counter_ns()

        # vetëm nëse komanda fituese ka hapur threshold
        if best_report is not None and best_report.opened:
            return RouteResult(
                input_text=input_text,
                route_name=best_name,
                report=best_report,
                all_scores=all_scores,
                router_ns=t1 - t0,
            )

        return RouteResult(
            input_text=input_text,
            route_name=None,
            report=best_report,  # ruhet për diagnostikim (opened=False)
            all_scores=all_scores,
            router_ns=t1 - t0,
        )
