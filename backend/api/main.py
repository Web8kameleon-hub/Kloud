"""Dynamic entrypoint for backend API service."""

from __future__ import annotations

import importlib
import os
from types import ModuleType
from typing import Any

_DEFAULT_MODULE = "backend.api.app_impl"


def _load_module() -> ModuleType:
    module_name = (
        os.getenv("KLOUD_BACKEND_API_APP_MODULE", _DEFAULT_MODULE).strip()
        or _DEFAULT_MODULE
    )
    try:
        return importlib.import_module(module_name)
    except Exception as primary_error:
        if module_name != _DEFAULT_MODULE:
            try:
                return importlib.import_module(_DEFAULT_MODULE)
            except Exception:
                pass
        raise RuntimeError(
            f"Unable to load backend app module '{module_name}'. "
            "Set KLOUD_BACKEND_API_APP_MODULE to a valid module path."
        ) from primary_error


_module = _load_module()

if not hasattr(_module, "app"):
    raise RuntimeError(
        f"Module '{_module.__name__}' does not expose a FastAPI 'app' instance"
    )

app = getattr(_module, "app")


def __getattr__(name: str) -> Any:
    return getattr(_module, name)
