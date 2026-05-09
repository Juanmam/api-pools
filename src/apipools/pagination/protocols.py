"""Typing protocols for pagination storage backends."""

from __future__ import annotations

from typing import Protocol

from .token import CursorToken


class OpaqueCursorStorage(Protocol):
    """Stateful backing for opaque cursor keys ↔ logical tokens."""

    def put(self, key: str, token: CursorToken) -> None:
        """Associate a hashed store key with a logical cursor token."""

    def get(self, key: str, *, operation: str, resource: str) -> CursorToken:
        """Return the logical token or raise interoperability pagination errors."""


__all__ = ["OpaqueCursorStorage"]
