"""Lazy dependency check for HTTP-backed test bindings (``dev`` extra)."""

from __future__ import annotations


def require_social_live() -> None:
    try:
        import httpx  # noqa: F401
    except ImportError as exc:  # pragma: no cover - exercised on missing extra
        raise RuntimeError(
            'Live social test bindings require HTTP; install dev deps: pip install -e ".[dev]"'
        ) from exc
