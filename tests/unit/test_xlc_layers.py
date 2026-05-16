"""Tests XLC Layers — WW/MM shtresa me matje nanoide për 'ALPHA' dhe raste të tjera."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XLC_DIR = ROOT / "ocean-core" / "xlc"
if str(XLC_DIR) not in sys.path:
    sys.path.insert(0, str(XLC_DIR))

from xlc_layers import LayerBuilder, LayerStack, Nanoide  # type: ignore

BUILDER = LayerBuilder()


# ---------------------------------------------------------------------------
# Ndërtimi bazë — "ALPHA"
# ---------------------------------------------------------------------------

def test_alpha_builds_ww_and_mm_layers() -> None:
    """'ALPHA' prodhon LayerStack me WW (12-dim), MM (12-dim) dhe CC (12-dim)."""
    stack = BUILDER.build("ALPHA")
    assert stack.sequence == "ALPHA"
    assert len(stack.ww.vector) == 12
    assert len(stack.mm.vector) == 12
    assert len(stack.cc.vector) == 12


def test_alpha_ww_and_mm_are_unit_vectors() -> None:
    """Të tre shtresat duhet të jenë vektorë unit (||v|| ≈ 1.0)."""
    stack = BUILDER.build("ALPHA")
    for layer in (stack.ww, stack.mm, stack.cc):
        norm = math.sqrt(sum(x * x for x in layer.vector))
        assert abs(norm - 1.0) < 1e-9, f"Layer {layer.name}: norm={norm}"


def test_alpha_ww_mm_are_different() -> None:
    """WW, MM dhe CC kanë profile të ndryshme nga njëra-tjetra."""
    stack = BUILDER.build("ALPHA")
    assert stack.ww.vector != stack.mm.vector
    assert stack.ww.vector != stack.cc.vector
    assert stack.mm.vector != stack.cc.vector


# ---------------------------------------------------------------------------
# Nanoide — matja e kohës
# ---------------------------------------------------------------------------

def test_nanoide_duration_is_positive() -> None:
    """Çdo shtresë (WW, MM, CC) duhet të ketë duration_ns > 0."""
    stack = BUILDER.build("ALPHA")
    assert stack.ww.nanoide.duration_ns > 0, "WW nanoide = 0"
    assert stack.mm.nanoide.duration_ns > 0, "MM nanoide = 0"
    assert stack.cc.nanoide.duration_ns > 0, "CC nanoide = 0"


def test_total_ns_is_positive_and_covers_layers() -> None:
    """total_ns duhet të jetë > 0 dhe >= sum i dy shtresave."""
    stack = BUILDER.build("ALPHA")
    assert stack.total_ns > 0
    assert stack.total_ns >= stack.ww.nanoide.duration_ns + stack.mm.nanoide.duration_ns


def test_nanoide_repr() -> None:
    """Nanoide.__repr__ duhet të përmbajë emrin e shtresës."""
    n = Nanoide("WW", 1000, 1500)
    assert "WW" in repr(n)
    assert "500" in repr(n)


# ---------------------------------------------------------------------------
# Identitet — e njëjta sekuencë prodhon stack identik
# ---------------------------------------------------------------------------

def test_same_sequence_identical_stack() -> None:
    """Dy ndërtime të 'ALPHA' prodhojnë vektorë identikë."""
    s1 = BUILDER.build("ALPHA")
    s2 = BUILDER.build("ALPHA")
    assert s1.ww.vector == s2.ww.vector
    assert s1.mm.vector == s2.mm.vector


def test_different_sequences_different_stacks() -> None:
    """'ALPHA' dhe 'BETA' prodhojnë stack-e të ndryshme."""
    sa = BUILDER.build("ALPHA")
    sb = BUILDER.build("BETA")
    assert sa.ww.vector != sb.ww.vector or sa.mm.vector != sb.mm.vector


# ---------------------------------------------------------------------------
# StackSimilarity — krahasimi shtresë-për-shtresë
# ---------------------------------------------------------------------------

def test_self_similarity_is_one() -> None:
    """Stack me veten e tij → combined similarity ≈ 1.0 (3 shtresa)."""
    stack = BUILDER.build("ALPHA")
    sim = stack.similarity_with(stack)
    assert abs(sim.combined - 1.0) < 1e-9
    assert abs(sim.sim_ww - 1.0) < 1e-9
    assert abs(sim.sim_mm - 1.0) < 1e-9
    assert abs(sim.sim_cc - 1.0) < 1e-9


def test_alpha_vs_beta_combined_less_than_one() -> None:
    """'ALPHA' vs 'BETA' → combined < 1.0 (nuk janë identike)."""
    sa = BUILDER.build("ALPHA")
    sb = BUILDER.build("BETA")
    sim = sa.similarity_with(sb)
    assert sim.combined < 1.0


def test_opens_at_threshold_same_stack() -> None:
    """E njëjta sekuencë → opens_at(0.9999) = True."""
    stack = BUILDER.build("ALPHA")
    sim = stack.similarity_with(stack)
    assert sim.opens_at(0.9999) is True


def test_opens_at_threshold_different_stack() -> None:
    """Sekuencë e ndryshme → opens_at(0.9999) = False."""
    sa = BUILDER.build("ALPHA")
    sb = BUILDER.build("OMEGA")
    sim = sa.similarity_with(sb)
    assert sim.opens_at(0.9999) is False


def test_compare_latency_is_measured() -> None:
    """compare_ns duhet të jetë > 0."""
    stack = BUILDER.build("ALPHA")
    sim = stack.similarity_with(stack)
    assert sim.compare_ns > 0


def test_cc_layer_is_cross_product_of_ww_mm() -> None:
    """CC duhet të jetë unit vector i produktit element-wise WW*MM."""
    import math
    stack = BUILDER.build("ALPHA")
    raw = [a * b for a, b in zip(stack.ww.vector, stack.mm.vector)]
    norm = math.sqrt(sum(x * x for x in raw))
    expected = [x / norm for x in raw]
    assert stack.cc.vector == expected


def test_cc_layer_name_is_cc() -> None:
    stack = BUILDER.build("ALPHA")
    assert stack.cc.name == "CC"


def test_sim_has_three_layer_scores() -> None:
    """StackSimilarity duhet të ketë sim_ww, sim_mm dhe sim_cc."""
    sa = BUILDER.build("ALPHA")
    sb = BUILDER.build("BETA")
    sim = sa.similarity_with(sb)
    assert hasattr(sim, "sim_ww")
    assert hasattr(sim, "sim_mm")
    assert hasattr(sim, "sim_cc")
    assert hasattr(sim, "combined")


# ---------------------------------------------------------------------------
# Raste kufitare
# ---------------------------------------------------------------------------

def test_single_letter_stack() -> None:
    """Sekuencë me 1 shkronjë ndërtohet pa gabim."""
    for letter in "AWMZ":
        stack = BUILDER.build(letter)
        assert stack.sequence == letter
        assert len(stack.ww.vector) == 12
        assert len(stack.mm.vector) == 12


def test_unknown_chars_stripped() -> None:
    """'AL PHA 99!' → sekuenca finale = 'ALPHA'."""
    stack = BUILDER.build("AL PHA 99!")
    assert stack.sequence == "ALPHA"


def test_unicode_script_is_supported() -> None:
    """Skriptet jo-latine duhet të ndërtohen pa ValueError."""
    stack = BUILDER.build("مرحبا")
    assert stack.sequence == "مرحبا"
    assert len(stack.ww.vector) == 12
    assert len(stack.mm.vector) == 12


def test_cjk_script_is_supported() -> None:
    """Han/CJK duhet të ruhet si sekuencë e vlefshme."""
    stack = BUILDER.build("你好世界")
    assert stack.sequence == "你好世界"
    assert len(stack.cc.vector) == 12


def test_empty_after_strip_raises() -> None:
    """Sekuencë pa shkronja të njohura → ValueError."""
    import pytest
    with pytest.raises(ValueError):
        BUILDER.build("123 !!")
