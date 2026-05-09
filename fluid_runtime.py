"""
Global WWWMMM Fluid auto-activation runtime.

This module is intentionally side-effect safe and can be imported from
sitecustomize/usercustomize in any service entrypoint.
"""

from __future__ import annotations

import os
from typing import Dict


TRUTHY = {"1", "true", "yes", "on"}


def _is_enabled(value: str) -> bool:
    return value.strip().lower() in TRUTHY


def _apply_defaults() -> Dict[str, str]:
    defaults: Dict[str, str] = {
        "FLUID_AUTOSTART": "true",
        "WWWMMM_AUTORUN": "true",
        "PRIMARY_RESONANT_PROFILE": "wwwmmm-ndb-stigma-tide-rezonance-nanogrid",
        "ADAPTIVE_COMPAT_MODE": "true",
        "OLD_MODE_ON_MISMATCH": "true",
        "RESONANT_WRITE_MODE": "new-first",
        "RESONANT_FALLBACK_MODE": "old-modus",
    }

    for key, val in defaults.items():
        os.environ.setdefault(key, val)

    return defaults


def activate_wwwmmm_fluid() -> bool:
    """
    Activate global fluid mode defaults for all services.

    Returns True when activation is applied or already active.
    """
    _apply_defaults()

    if not _is_enabled(os.environ.get("FLUID_AUTOSTART", "true")):
        return False

    os.environ["WWWMMM_AUTORUN"] = "true"
    os.environ.setdefault("FLUID_ACTIVE", "1")
    os.environ.setdefault("FLUID_ACTIVATION_SOURCE", "sitecustomize")
    return True


# Import-time activation for automatic behavior across the repo.
activate_wwwmmm_fluid()
