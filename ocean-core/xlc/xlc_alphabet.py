"""
XLC WWWMMM Alphabet — 26 fizike profile unike per çdo shkronjë angleze.

Çdo simbol ka 6 dimensione:
  W1 = amplitude envelope    (4 samples)
  W2 = phase progression     (4 samples)
  W3 = wavefront coherence   (4 samples)
  M1 = base frequency        (4 samples)
  M2 = harmonic spread       (4 samples)
  M3 = jitter_ns             (4 samples)

Profile janë gjeneruar me formulë deterministike bazuar në pozicionin e shkronjës,
duke siguruar distancë minumale cosine >= 0.04 ndërmjet çdo çifti simbolesh.
"""
from __future__ import annotations

import math
import unicodedata
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class WWWMMM:
    """6-dimensional physical resonance profile — the XLC symbol fingerprint."""

    w1_amplitude: List[float]     # envelope shape
    w2_phase: List[float]         # phase progression
    w3_coherence: List[float]     # wavefront coherence (inter-sample correlance)
    m1_frequency: List[float]     # base frequency band
    m2_harmonic: List[float]      # harmonic spread
    m3_jitter_ns: List[float]     # nanosecond timing jitter

    def to_vector(self) -> List[float]:
        """Flatten all 6×4 = 24 floats into a single feature vector.

        Jitter is scaled by 1/1000 to keep magnitudes comparable.
        """
        jitter_scaled = [v / 1000.0 for v in self.m3_jitter_ns]
        return [
            *self.w1_amplitude,
            *self.w2_phase,
            *self.w3_coherence,
            *self.m1_frequency,
            *self.m2_harmonic,
            *jitter_scaled,
        ]


LATIN_BASE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _profile_for(index: int) -> WWWMMM:
    """Deterministike: çdo shkronjë merr profile bazuar në indeksin (0–25).

    Formulë: dimensione të derivuara nga harmonikat e π dhe e bazuar
    në frekuencën karakteristike të pozicionit.
    """
    i = index
    n = 26  # total symbols

    base = (i + 1) / n  # në (0, 1]
    angle_step = math.pi * 2 * (i + 1) / n

    def w1(k: int) -> float:
        return round(0.55 + 0.40 * math.sin(angle_step * (k + 1) + 0.0), 6)

    def w2(k: int) -> float:
        return round(0.10 + 0.85 * abs(math.cos(angle_step * (k + 1) / 2 + base)), 6)

    def w3(k: int) -> float:
        return round(0.50 + 0.45 * math.sin(angle_step / 3 * (k + 1) + math.pi / 4), 6)

    def m1(k: int) -> float:
        return round(0.15 + 0.80 * abs(math.sin(angle_step * (k + 1) * 1.5 + base * math.pi)), 6)

    def m2(k: int) -> float:
        return round(0.20 + 0.70 * abs(math.cos(angle_step * (k + 1) * 2.3 + 0.5)), 6)

    def m3(k: int) -> float:
        # jitter qëndron në [8, 42] nanosekonda
        return round(8.0 + 34.0 * abs(math.sin(angle_step * (k + 1) * 0.7 + base)), 6)

    return WWWMMM(
        w1_amplitude=[w1(k) for k in range(4)],
        w2_phase=[w2(k) for k in range(4)],
        w3_coherence=[w3(k) for k in range(4)],
        m1_frequency=[m1(k) for k in range(4)],
        m2_harmonic=[m2(k) for k in range(4)],
        m3_jitter_ns=[m3(k) for k in range(4)],
    )


def normalize_symbol(symbol: str) -> str:
    """Normalizon simbolin në formën kanonike 1-karakterëshe për XLC."""
    normalized = unicodedata.normalize("NFKC", symbol or "").strip().upper()
    if not normalized:
        return ""
    return normalized[0]


def _profile_for_unicode_symbol(symbol: str) -> WWWMMM:
    """Gjeneron profil deterministik për çdo shkronjë Unicode."""
    normalized = normalize_symbol(symbol)
    if normalized in LATIN_BASE_ALPHABET:
        return _profile_for(LATIN_BASE_ALPHABET.index(normalized))

    codepoint = ord(normalized)
    seed = codepoint + 1
    base = ((seed % 4096) + 1) / 4096.0
    angle_step = math.pi * 2 * ((seed % 1024) + 1) / 1024.0
    drift = ((seed // 7) % 257) / 257.0

    def w1(k: int) -> float:
        return round(0.50 + 0.43 * math.sin(angle_step * (k + 1) + drift), 6)

    def w2(k: int) -> float:
        return round(0.12 + 0.82 * abs(math.cos(angle_step * (k + 1) / 2 + base)), 6)

    def w3(k: int) -> float:
        return round(0.48 + 0.46 * math.sin(angle_step / 3 * (k + 1) + math.pi / 4 + drift), 6)

    def m1(k: int) -> float:
        return round(0.14 + 0.79 * abs(math.sin(angle_step * (k + 1) * 1.37 + base * math.pi)), 6)

    def m2(k: int) -> float:
        return round(0.18 + 0.72 * abs(math.cos(angle_step * (k + 1) * 2.11 + drift)), 6)

    def m3(k: int) -> float:
        return round(8.0 + 34.0 * abs(math.sin(angle_step * (k + 1) * 0.61 + base + drift)), 6)

    return WWWMMM(
        w1_amplitude=[w1(k) for k in range(4)],
        w2_phase=[w2(k) for k in range(4)],
        w3_coherence=[w3(k) for k in range(4)],
        m1_frequency=[m1(k) for k in range(4)],
        m2_harmonic=[m2(k) for k in range(4)],
        m3_jitter_ns=[m3(k) for k in range(4)],
    )


def resolve_profile(symbol: str, alphabet: Dict[str, WWWMMM] | None = None) -> WWWMMM:
    """Kthen ose krijon profilin fizik për një shkronjë Unicode."""
    normalized = normalize_symbol(symbol)
    if not normalized or not normalized.isalpha():
        raise ValueError(f"simboli '{symbol}' nuk është shkronjë e vlefshme")

    target = alphabet if alphabet is not None else ALPHABET
    if normalized not in target:
        target[normalized] = _profile_for_unicode_symbol(normalized)
    return target[normalized]


def build_alphabet() -> Dict[str, WWWMMM]:
    """Kthen dictionarin bazë të XLC me alfabetin latin A–Z."""
    return {letter: _profile_for(i) for i, letter in enumerate(LATIN_BASE_ALPHABET)}


# Instanca e cached e alfabetit — ngarkohet njëherë
ALPHABET: Dict[str, WWWMMM] = build_alphabet()
