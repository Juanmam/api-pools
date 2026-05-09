"""Structured semantic interoperability errors."""

from dataclasses import dataclass
from typing import Any


@dataclass
class InteroperabilityError(Exception):
    """Base semantic interoperability failure."""

    message: str
    operation: str
    resource: str
    detail: str | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        suffix = f" detail={self.detail}" if self.detail else ""
        return (
            f"{self.__class__.__name__}: {self.message} "
            f"(operation={self.operation}, resource={self.resource}){suffix}"
        )


class UnsupportedCapabilityError(InteroperabilityError):
    """Requested capability is not supported by provider contract."""


class PartialCapabilityError(InteroperabilityError):
    """Requested floor is full, but capability only supports partial."""


class NormalizationError(InteroperabilityError):
    """Canonical mapping cannot be performed lawfully."""


class VersionMismatchError(InteroperabilityError):
    """Unsupported canonical version requested."""


class CrossProviderInconsistencyError(InteroperabilityError):
    """Multiple providers produce inconsistent structural semantics."""


class CapabilityMismatchError(InteroperabilityError):
    """Requested canonical fields cannot be fully resolved for a provider."""


@dataclass
class PaginationInvariantError(InteroperabilityError):
    """Pagination correctness invariant was violated."""

    page_index: int | None = None
    cursor: str | None = None
    offending_item: Any | None = None
    trace_snapshot: Any | None = None


class InvalidCursorError(InteroperabilityError):
    """Cursor envelope is malformed or violates encoding contract (non-determinism)."""


class ExpiredCursorError(InteroperabilityError):
    """Cursor TTL elapsed, was evicted, or unknown to the bounded store."""


class TamperedCursorError(InteroperabilityError):
    """Cursor integrity check failed (forgery or mutation)."""
