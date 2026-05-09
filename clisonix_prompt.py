"""
Kloud Module Map Loader
============================
Loads the module map and provides routing utilities.
Internal configuration is read from environment variables.

Usage:
    from kloud_prompt import get_module_map, get_user_prompt, get_route
    
    # Get user-facing prompt
    prompt = get_user_prompt()
    
    # Get route for a module
    route = get_route("ocean")  # Returns "/api/ocean"
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

# Module map file location
MODULE_MAP_FILE = "KLOUD_MODULE_MAP.md"

# Public routes only (no ports, no containers)
ROUTES = {
    "ocean": "/api/ocean",
    "chat": "/api/chat",
    "trinity": "/api/trinity",
    "zurich": "/api/zurich",
    "alba": "/api/alba",
    "albi": "/api/albi",
    "jona": "/api/jona",
}


def _find_module_map() -> Path:
    """Find the module map file."""
    # Environment variable (recommended for Docker)
    env_path = os.environ.get("KLOUD_MODULE_MAP_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    
    # Search from current file upward
    current = Path(__file__).resolve().parent
    for _ in range(5):
        map_path = current / MODULE_MAP_FILE
        if map_path.exists():
            return map_path
        current = current.parent
    
    return None


@lru_cache(maxsize=1)
def get_module_map() -> str:
    """Load and cache the module map content."""
    map_path = _find_module_map()
    if map_path:
        with open(map_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def get_route(module_name: str) -> str:
    """Get the API route for a module."""
    return ROUTES.get(module_name, f"/api/{module_name}")


def get_all_routes() -> Dict[str, str]:
    """Get all module routes."""
    return ROUTES.copy()


def get_safety_rules() -> list:
    """Get safety rules."""
    return [
        "Never invent facts",
        "Never provide medical/legal/financial advice",
        "Always cite sources",
    ]


# Auto-load on import
_map = get_module_map()
if _map:
    print(f"[Kloud] Module map loaded")


if __name__ == "__main__":
    print("ROUTES:", get_all_routes())
    print("MAP:", "loaded" if get_module_map() else "not found")

