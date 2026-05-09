"""Opaque cursor logical token (not wire-exposed verbatim)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CursorToken:
    """Structured cursor state; client never receives this raw."""

    provider_id: str
    operation: str
    resource: str
    provider_cursor: str
    issued_at_ns: int
    metadata: tuple[tuple[str, str], ...] = ()
