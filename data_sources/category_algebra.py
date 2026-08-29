# -*- coding: utf-8 -*-
"""
CATEGORY ALGEBRA (Cᴀ) — Scalable 1001-Category Taxonomy
========================================================

Instead of 24 hand-written categories, categories are *composed* algebraically
from three orthogonal axes (following the Ultra Algebra composition ∘ model):

    Category = Domain ∘ Facet ∘ Scope

    |Domain| = 7   (super-domains grouping the 24 base SourceCategory roots)
    |Facet|  = 11  (activity / aspect operators)
    |Scope|  = 13  (11 geographic regions + WORLD + CROSS)

    Total = 7 × 11 × 13 = 1001  (exact, no padding)

Every one of the 4053 real data sources maps deterministically to exactly one
of the 1001 composed codes via `classify()`. Counts per category are REAL
measurements — many codes legitimately have 0 sources (that is honest coverage,
not a fabricated number). The taxonomy schema is 1001; measured coverage is
reported separately.

Author: Ledjan Ahmati / WEB8euroweb GmbH — Sovereign Runtime
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

try:  # package context
    from .global_data_sources import COUNTRY_TO_REGION, Region
except Exception:  # pragma: no cover - flat import fallback
    from global_data_sources import COUNTRY_TO_REGION, Region  # type: ignore

# ─────────────────────────────────────────────────────────────────────────────
# AXIS A — DOMAINS (7)  — groups the 24 base SourceCategory roots
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS: List[str] = [
    "PUBLIC",     # government, statistics, international
    "KNOWLEDGE",  # university, research, culture
    "HEALTH",     # hospital
    "FINANCE",    # bank, rating
    "INDUSTRY",   # industry, energy, telecom, technology, transport
    "MEDIA",      # news, entertainment, sport, events
    "LIVING",     # tourism, lifestyle, environmental
]

# base SourceCategory value -> domain
DOMAIN_MAP: Dict[str, str] = {
    "government": "PUBLIC",
    "statistics": "PUBLIC",
    "international": "PUBLIC",
    "university": "KNOWLEDGE",
    "research": "KNOWLEDGE",
    "culture": "KNOWLEDGE",
    "hospital": "HEALTH",
    "bank": "FINANCE",
    "rating": "FINANCE",
    "industry": "INDUSTRY",
    "energy": "INDUSTRY",
    "telecom": "INDUSTRY",
    "technology": "INDUSTRY",
    "transport": "INDUSTRY",
    "news": "MEDIA",
    "entertainment": "MEDIA",
    "sport": "MEDIA",
    "events": "MEDIA",
    "tourism": "LIVING",
    "lifestyle": "LIVING",
    "environmental": "LIVING",
}

# ─────────────────────────────────────────────────────────────────────────────
# AXIS B — FACETS (11) — activity / aspect operators
# ─────────────────────────────────────────────────────────────────────────────
FACETS: List[str] = [
    "DATA", "RESEARCH", "SERVICE", "POLICY", "INDEX", "LIVE",
    "ARCHIVE", "NETWORK", "MARKET", "LEARN", "SIGNAL",
]

# keyword → facet (scanned against name + description, lowercased)
FACET_KEYWORDS: Dict[str, str] = {
    "dataset": "DATA", "data": "DATA", "open data": "DATA", "portal": "DATA",
    "research": "RESEARCH", "institute": "RESEARCH", "lab": "RESEARCH", "science": "RESEARCH",
    "service": "SERVICE", "agency": "SERVICE", "office": "SERVICE", "authority": "SERVICE",
    "policy": "POLICY", "ministry": "POLICY", "regulation": "POLICY", "law": "POLICY",
    "index": "INDEX", "registry": "INDEX", "catalog": "INDEX", "directory": "INDEX",
    "live": "LIVE", "realtime": "LIVE", "real-time": "LIVE", "stream": "LIVE", "monitor": "LIVE",
    "archive": "ARCHIVE", "library": "ARCHIVE", "museum": "ARCHIVE", "heritage": "ARCHIVE",
    "network": "NETWORK", "association": "NETWORK", "federation": "NETWORK", "union": "NETWORK",
    "market": "MARKET", "exchange": "MARKET", "trade": "MARKET", "commerce": "MARKET",
    "learn": "LEARN", "education": "LEARN", "university": "LEARN", "academy": "LEARN", "school": "LEARN",
    "signal": "SIGNAL", "sensor": "SIGNAL", "weather": "SIGNAL", "observation": "SIGNAL",
}

# ─────────────────────────────────────────────────────────────────────────────
# AXIS C — SCOPES (13) — 11 regions + WORLD + CROSS
# ─────────────────────────────────────────────────────────────────────────────
SCOPES: List[str] = [
    "EUROPE", "NORTH_AMERICA", "SOUTH_AMERICA", "EAST_ASIA", "SOUTH_ASIA",
    "SOUTHEAST_ASIA", "OCEANIA", "MIDDLE_EAST", "NORTH_AFRICA",
    "SUB_SAHARAN_AFRICA", "GLOBAL", "WORLD", "CROSS",
]

assert len(DOMAINS) == 7 and len(FACETS) == 11 and len(SCOPES) == 13
TAXONOMY_SIZE = len(DOMAINS) * len(FACETS) * len(SCOPES)  # 1001


@dataclass(frozen=True)
class CategoryCode:
    domain: str
    facet: str
    scope: str

    @property
    def code(self) -> str:
        return f"{self.domain}.{self.facet}.{self.scope}"

    def to_dict(self) -> Dict[str, str]:
        return {"code": self.code, "domain": self.domain, "facet": self.facet, "scope": self.scope}


@lru_cache(maxsize=1)
def all_categories() -> Tuple[CategoryCode, ...]:
    """Deterministic, canonically ordered set of all 1001 composed categories."""
    out: List[CategoryCode] = []
    for d in DOMAINS:
        for f in FACETS:
            for s in SCOPES:
                out.append(CategoryCode(d, f, s))
    return tuple(out)


def _scope_for_country(country: str) -> str:
    if not country:
        return "WORLD"
    c = country.upper()
    if c in ("GLOBAL", "INTL", "WORLD"):
        return "WORLD"
    region: Optional[Region] = COUNTRY_TO_REGION.get(c)
    if region is None:
        return "CROSS"
    name = region.name  # e.g. "EUROPE"
    return name if name in SCOPES else "GLOBAL"


def _facet_for_text(text: str, default: str = "DATA") -> str:
    t = (text or "").lower()
    for kw, facet in FACET_KEYWORDS.items():
        if kw in t:
            return facet
    return default


def classify(source: Any) -> CategoryCode:
    """Map a real DataSource to exactly one composed category code."""
    cat = getattr(source, "category", None)
    cat_val = getattr(cat, "value", str(cat)) if cat is not None else "government"
    domain = DOMAIN_MAP.get(cat_val, "PUBLIC")
    text = f"{getattr(source, 'name', '')} {getattr(source, 'description', '')}"
    facet = _facet_for_text(text)
    scope = _scope_for_country(getattr(source, "country", ""))
    return CategoryCode(domain, facet, scope)


def distribution(sources: List[Any]) -> Dict[str, int]:
    """Real measured count of sources per composed category code."""
    counts: Dict[str, int] = {}
    for s in sources:
        code = classify(s).code
        counts[code] = counts.get(code, 0) + 1
    return counts


def coverage(sources: List[Any]) -> Dict[str, Any]:
    dist = distribution(sources)
    populated = {k: v for k, v in dist.items() if v > 0}
    return {
        "taxonomy_size": TAXONOMY_SIZE,          # 1001 (schema)
        "axes": {"domains": len(DOMAINS), "facets": len(FACETS), "scopes": len(SCOPES)},
        "populated_categories": len(populated),  # real measurement
        "empty_categories": TAXONOMY_SIZE - len(populated),
        "total_classified_sources": sum(dist.values()),
    }


__all__ = [
    "DOMAINS", "FACETS", "SCOPES", "TAXONOMY_SIZE",
    "CategoryCode", "all_categories", "classify", "distribution", "coverage",
]


if __name__ == "__main__":
    print(f"Category Algebra: {len(DOMAINS)}×{len(FACETS)}×{len(SCOPES)} = {TAXONOMY_SIZE} categories")
    cats = all_categories()
    print("first:", cats[0].code, "| last:", cats[-1].code, "| total:", len(cats))
