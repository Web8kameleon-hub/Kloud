"""
XLC Layers — 3-shtresa WW / MM / CC me matje nanoide.

Koncepti:
  Çdo sekuencë (p.sh. "ALPHA") ndahet në TRE shtresa fizike:

    Layer WW (Wave):            w1_amplitude + w2_phase + w3_coherence  → 12 dims
    Layer MM (Momentum):        m1_frequency + m2_harmonic + m3_jitter  → 12 dims
    Layer CC (Cross-Corr WW⊗MM): produkti element-wise WW×MM, normalizuar → 12 dims

  Çdo shtresë prodhohet nga superpozicioni i vektorëve të simboleve,
  pastaj normalizohet (unit vector).

  CC = "lidhja" ndërmjet valës dhe momentumit — shpreh sa dy shtresat
  janë në rezonancë me njëra-tjetrën. Dy sekuenca identike → CC identik.
  Sekuenca e ndryshme → CC i ndryshëm, edhe kur WW ose MM rastësisht ngjajnë.

  Koha e ndërtimit të çdo shtrese matet në **nanoide** (ns) me perf_counter_ns.
  "Nanoide" = njësia e brendshme XLC për timing inter-shtresë.

  LayerStack = [WW, MM, CC] + metadata nanoide per shtresë.
  combined = mean(sim_ww, sim_mm, sim_cc) — 3-shtresë, rezolucion maksimal.

  Rregull NO_FAKE_DATA: asnjë similarity e hardcoded — çdo vlerë vjen
  nga llogaritje reale dot-product.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from xlc_alphabet import ALPHABET, WWWMMM, resolve_profile  # type: ignore

# ---------------------------------------------------------------------------
# Low-level math (numpy)
# ---------------------------------------------------------------------------

def _dot(a: List[float], b: List[float]) -> float:
    return float(np.dot(a, b))


def _normalize(v: List[float]) -> List[float]:
    arr = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(arr))
    return (arr / n).tolist() if n > 0.0 else arr.tolist()


def _mean_vectors(vectors: List[List[float]]) -> List[float]:
    return np.array(vectors, dtype=np.float64).mean(axis=0).tolist()


# ---------------------------------------------------------------------------
# Nanoide — njësia e brendshme e timing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Nanoide:
    """Matja e kohës për ndërtimin e një shtrese (në nanosekonda)."""
    layer_name: str
    start_ns: int
    end_ns: int

    @property
    def duration_ns(self) -> int:
        return self.end_ns - self.start_ns

    def __repr__(self) -> str:
        return f"Nanoide({self.layer_name}: {self.duration_ns} ns)"


# ---------------------------------------------------------------------------
# LayerPrint — fingerprint i një shtrese
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LayerPrint:
    """Fingerprint i normalizuar i një shtrese (WW, MM, ose CC)."""
    name: str           # "WW", "MM", ose "CC"
    vector: List[float] # 12-dimensional unit vector
    nanoide: Nanoide    # koha e ndërtimit

    def similarity_with(self, other: "LayerPrint") -> float:
        """Cosine similarity — meqë të dyja janë unit vectors, ky është dot product."""
        if self.name != other.name:
            raise ValueError(
                f"nuk mund të krahasosh shtresë '{self.name}' me '{other.name}'"
            )
        return _dot(self.vector, other.vector)


# ---------------------------------------------------------------------------
# LayerStack — stack i plotë WW + MM për një sekuencë
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LayerStack:
    """Stack 3-shtresë WW+MM+CC për një sekuencë simbolesh.

    Atribute:
        sequence:   sekuenca origjinale (uppercase, vetëm shkronja të njohura)
        ww:         LayerPrint Wave (12-dim)
        mm:         LayerPrint Momentum (12-dim)
        cc:         LayerPrint Cross-Correlation WW⊗MM (12-dim)
        total_ns:   koha totale e ndërtimit (ns)
    """
    sequence: str
    ww: LayerPrint
    mm: LayerPrint
    cc: LayerPrint
    total_ns: int

    def similarity_with(self, other: "LayerStack") -> "StackSimilarity":
        """Krahason dy stack-e shtresë-për-shtresë (3 layers).

        combined = mean(sim_ww, sim_mm, sim_cc) — rezolucion maksimal.
        Asnjëherë nuk gjeneron vlerë false.
        """
        t0 = time.perf_counter_ns()
        sim_ww = self.ww.similarity_with(other.ww)
        sim_mm = self.mm.similarity_with(other.mm)
        sim_cc = self.cc.similarity_with(other.cc)
        combined = (sim_ww + sim_mm + sim_cc) / 3.0
        t1 = time.perf_counter_ns()
        return StackSimilarity(
            sim_ww=sim_ww,
            sim_mm=sim_mm,
            sim_cc=sim_cc,
            combined=combined,
            compare_ns=t1 - t0,
        )


@dataclass(frozen=True)
class StackSimilarity:
    """Rezultati i krahasimit të dy LayerStack-eve (3 shtresa)."""
    sim_ww: float      # similarity shtresa WW
    sim_mm: float      # similarity shtresa MM
    sim_cc: float      # similarity shtresa CC (cross-correlation)
    combined: float    # mean i 3 shtresave
    compare_ns: int    # koha e krahasimit në ns

    def opens_at(self, threshold: float) -> bool:
        """Dera hapet nëse combined >= threshold."""
        return self.combined >= threshold


# ---------------------------------------------------------------------------
# LayerBuilder — ndërton LayerStack nga sekuencë + alfabet
# ---------------------------------------------------------------------------

class LayerBuilder:
    """Ndërton LayerStack me matje nanoide per çdo shtresë.

    Shembull:
        builder = LayerBuilder()
        stack = builder.build("ALPHA")
        # stack.ww   → Layer Wave (12-dim, matur në ns)
        # stack.mm   → Layer Momentum (12-dim, matur në ns)
        # stack.total_ns → koha totale
    """

    def __init__(self, alphabet: Dict[str, WWWMMM] | None = None) -> None:
        self._alphabet = alphabet if alphabet is not None else ALPHABET

    def normalize_text(self, text: str) -> str:
        """Nxjerr vetëm shkronjat e vlefshme dhe krijon profile sipas nevojës."""
        known: List[str] = []
        for ch in (text or "").upper():
            if not ch.isalpha():
                continue
            resolve_profile(ch, self._alphabet)
            known.append(ch)
        return "".join(known)

    def build(self, text: str) -> LayerStack:
        """Ndërton LayerStack nga teksti.

        Raises:
            ValueError: nëse asnjë karakter nuk gjendet në alfabet
        """
        t_total_start = time.perf_counter_ns()
        known: List[str] = list(self.normalize_text(text))
        if not known:
            raise ValueError(
                f"sekuenca '{text}' nuk ka asnjë simbol të njohur në alfabet"
            )

        profiles = [resolve_profile(ch, self._alphabet) for ch in known]

        # ── shtresa WW (Wave) ──────────────────────────────────────────────
        t_ww_start = time.perf_counter_ns()
        ww_arr = np.array(
            [[*p.w1_amplitude, *p.w2_phase, *p.w3_coherence] for p in profiles],
            dtype=np.float64,
        )  # (N, 12)
        ww_mean_arr = ww_arr.mean(axis=0)
        ww_n = float(np.linalg.norm(ww_mean_arr))
        ww_unit_arr = ww_mean_arr / ww_n if ww_n > 0.0 else ww_mean_arr
        ww_unit = ww_unit_arr.tolist()
        t_ww_end = time.perf_counter_ns()

        # ── shtresa MM (Momentum) ──────────────────────────────────────────
        t_mm_start = time.perf_counter_ns()
        mm_arr = np.array(
            [[*p.m1_frequency, *p.m2_harmonic, *[v / 1000.0 for v in p.m3_jitter_ns]]
             for p in profiles],
            dtype=np.float64,
        )  # (N, 12)
        mm_mean_arr = mm_arr.mean(axis=0)
        mm_n = float(np.linalg.norm(mm_mean_arr))
        mm_unit_arr = mm_mean_arr / mm_n if mm_n > 0.0 else mm_mean_arr
        mm_unit = mm_unit_arr.tolist()
        t_mm_end = time.perf_counter_ns()

        # ── shtresa CC (Cross-Correlation WW⊗MM) ──────────────────────────
        t_cc_start = time.perf_counter_ns()
        cc_raw_arr = ww_unit_arr * mm_unit_arr  # element-wise (12,)
        cc_n = float(np.linalg.norm(cc_raw_arr))
        cc_unit_arr = cc_raw_arr / cc_n if cc_n > 0.0 else cc_raw_arr
        cc_unit = cc_unit_arr.tolist()
        t_cc_end = time.perf_counter_ns()

        t_total_end = time.perf_counter_ns()

        ww_layer = LayerPrint(
            name="WW",
            vector=ww_unit,
            nanoide=Nanoide("WW", t_ww_start, t_ww_end),
        )
        mm_layer = LayerPrint(
            name="MM",
            vector=mm_unit,
            nanoide=Nanoide("MM", t_mm_start, t_mm_end),
        )
        cc_layer = LayerPrint(
            name="CC",
            vector=cc_unit,
            nanoide=Nanoide("CC", t_cc_start, t_cc_end),
        )

        return LayerStack(
            sequence="".join(known),
            ww=ww_layer,
            mm=mm_layer,
            cc=cc_layer,
            total_ns=t_total_end - t_total_start,
        )
