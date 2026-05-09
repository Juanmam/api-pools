"""Canonical semantic models for the minimal validation slice."""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class FieldStatus(str, Enum):
    """Explicit partiality states."""

    VALUE = "value"
    UNREQUESTED = "unrequested"
    UNSUPPORTED = "unsupported"
    MISSING = "missing"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"
    UNMAPPABLE = "unmappable"
    REDACTED = "redacted"


@dataclass(frozen=True)
class SemanticField(Generic[T]):
    """A field that carries explicit semantic partiality status."""

    status: FieldStatus
    value: T | None = None

    def __post_init__(self) -> None:
        if self.status is FieldStatus.VALUE and self.value is None:
            raise ValueError("FieldStatus.VALUE requires a concrete value.")
        if self.status is not FieldStatus.VALUE and self.value is not None:
            raise ValueError("Non-VALUE semantic fields must not carry a value.")


@dataclass(frozen=True)
class CanonicalPost:
    """Canonical Post@v1."""

    id: str
    text: SemanticField[str]
    author_id: SemanticField[str]
    created_at: SemanticField[str]


@dataclass(frozen=True)
class CanonicalComment:
    """Canonical Comment@v1."""

    id: str
    post_id: str
    text: SemanticField[str]
    author_id: SemanticField[str]
    created_at: SemanticField[str]
