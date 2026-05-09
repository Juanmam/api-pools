"""Semantic ports for bindings (third-party adapters implement these patterns)."""

from __future__ import annotations

from typing import Protocol

from .canonical import CanonicalComment, CanonicalPost
from .capabilities import CapabilityContract


class CapabilityDeclarer(Protocol):
    """Declares static capability tuples."""

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        """Return the binding's capability contracts."""


class SocialSemanticBinding(Protocol):
    """Wire + normalization port for a social-style bounded strategy (example domain contract)."""

    binding_id: str

    def capabilities(self) -> tuple[CapabilityContract, ...]: ...

    def fetch_post(self, provider_post_id: str) -> dict: ...

    def fetch_comment(self, provider_comment_id: str) -> dict: ...

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict: ...

    def normalize_post(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalPost, str | None]: ...

    def normalize_comment(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalComment, str | None]: ...


__all__ = ["CapabilityDeclarer", "SocialSemanticBinding"]
