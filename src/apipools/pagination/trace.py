"""Deterministic pagination execution trace models."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PageTrace:
    cursor_in: str | None
    cursor_out: str | None
    item_ids: tuple[str, ...]
    ordering_values: tuple[Any, ...]
    has_more: bool
    anomalies: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaginationTrace:
    pages: tuple[PageTrace, ...] = ()

    def append(self, page_trace: PageTrace) -> "PaginationTrace":
        return PaginationTrace(pages=(*self.pages, page_trace))

    @property
    def length(self) -> int:
        return len(self.pages)
