"""Shared CORS configuration for FastAPI services."""

from __future__ import annotations

import os
from typing import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_ALLOWED_ORIGINS = [
    "https://clisonix.com",
    "https://www.clisonix.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

DEFAULT_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
DEFAULT_ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Accept",
    "X-Requested-With",
    "X-API-Key",
]


def _parse_origins(value: str | None, fallback: Iterable[str]) -> list[str]:
    if value:
        parsed = [origin.strip() for origin in value.split(",") if origin.strip()]
        if parsed:
            return parsed
    return list(fallback)


def apply_standard_cors(
    app: FastAPI,
    *,
    env_var: str = "ALLOWED_ORIGINS",
    default_origins: Iterable[str] = DEFAULT_ALLOWED_ORIGINS,
    allow_credentials: bool = True,
) -> None:
    """Apply the shared CORS policy to a FastAPI app."""
    allowed_origins = _parse_origins(os.getenv(env_var), default_origins)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=DEFAULT_ALLOWED_METHODS,
        allow_headers=DEFAULT_ALLOWED_HEADERS,
        allow_credentials=allow_credentials,
    )
