"""Canonical semantic pagination envelope."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page(Generic[T]):
    items: Sequence[T]
    next_cursor: str | None
    has_more: bool
    gap: str | None = None
