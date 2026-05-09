"""Minimal integrated routes for the app.

Provides a small APIRouter with /health and /info endpoints so the main app can
mount and exercise basic behavior without requiring the full system.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

router = APIRouter()


def get_service_name() -> str:
	# example dependency that could be replaced by a real service later
	return "Kloud-integrated"


@router.get("/health")
def health():
	return {"status": "ok"}


@router.get("/info")
def info(service: str = Depends(get_service_name)):
	return {"service": service, "description": "Minimal integrated routes"}


