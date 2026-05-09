"""Thin execution ports; semantic core stays transport-agnostic."""

from typing import Any, Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)


class TransportCallable(Protocol[T_co]):
    """Single-shot execution hook (HTTP client, RPC stub, mocked transport)."""

    def __call__(self, *, operation: str, resource: str, payload: dict[str, Any]) -> T_co:
        """Return wire-level or parsed transport result."""


__all__ = ["TransportCallable"]
