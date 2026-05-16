"""Dynamic API entrypoint for Kloud.

This module resolves the active FastAPI app at runtime so deployments can
standardize on `main:app` while still selecting the underlying module
through environment configuration.
"""

from __future__ import annotations

import importlib
import os
from types import ModuleType
from typing import Any

_DEFAULT_MODULE = "apps.api.main"


def _load_module() -> ModuleType:
    module_name = (
        os.getenv("KLOUD_APP_MODULE", _DEFAULT_MODULE).strip() or _DEFAULT_MODULE
    )
    try:
        return importlib.import_module(module_name)
    except Exception as primary_error:
        # Fallback to the canonical API module if custom module import fails.
        if module_name != _DEFAULT_MODULE:
            try:
                return importlib.import_module(_DEFAULT_MODULE)
            except Exception:
                pass
        raise RuntimeError(
            f"Unable to load app module '{module_name}'. "
            f"Set KLOUD_APP_MODULE to a valid module path."
        ) from primary_error


_module = _load_module()

if not hasattr(_module, "app"):
    raise RuntimeError(
        f"Module '{_module.__name__}' does not expose a FastAPI 'app' instance"
    )

app = getattr(_module, "app")


def __getattr__(name: str) -> Any:
    """Expose symbols from the resolved module for compatibility."""
    return getattr(_module, name)
