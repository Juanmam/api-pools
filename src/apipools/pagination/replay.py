"""Deterministic replay checkpoints (additive to PaginationEngine)."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .trace import PageTrace, PaginationTrace


def encode_ordering_value(value: Any) -> str:
    """Canonical JSON-ish encoding for stable checkpoint comparison."""
    return json.dumps(value, sort_keys=True, default=str)


def lineage_hash_for_state(
    seen_item_ids: Iterable[str],
    seen_next_cursors: Iterable[str],
    pages_completed: int,
) -> str:
    """Deterministic lineage fingerprint without embedding full traces."""
    body = (
        "|".join(sorted(seen_item_ids))
        + "\n"
        + "|".join(sorted(seen_next_cursors))
        + "\n"
        + str(int(pages_completed))
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReplayCheckpoint:
    """Minimal immutable boundary for deterministic resume."""

    cursor: str | None  # outbound client pagination token after this page
    page_index: int  # 0-based index of last completed trace page (= trace_anchor)
    last_item_id: str
    ordering_value: str  # canonical JSON-encoded ordering key / tail value
    lineage_hash: str
    trace_anchor: int

    def aligns_with_trace(self, *, trace_page: PageTrace) -> bool:
        if trace_page.cursor_out != self.cursor:
            return False
        if trace_page.item_ids:
            if trace_page.item_ids[-1] != self.last_item_id:
                return False
        elif self.last_item_id:
            return False
        if self.ordering_value:
            if not trace_page.ordering_values:
                return False
            if encode_ordering_value(trace_page.ordering_values[-1]) != self.ordering_value:
                return False
        elif trace_page.ordering_values:
            return False
        return True


def subset_trace_through_anchor(trace: PaginationTrace, anchor: int) -> PaginationTrace:
    if anchor < 0 or anchor >= trace.length:
        raise ValueError("trace_anchor out of range")

    return PaginationTrace(pages=tuple(trace.pages[: anchor + 1]))


def hydrate_state_from_trace_prefix(trace: PaginationTrace, anchor: int):  # -> PaginationState
    """Defer import cycle: returns PaginationState from engine module."""

    # Local import avoids circular imports at runtime
    from .engine import PaginationState

    subset = subset_trace_through_anchor(trace, anchor)

    seen_item_ids: set[str] = set()
    seen_next_cursors: set[str] = set()
    last_ordering: Any | None = None
    pages_completed = subset.length

    for page in subset.pages:
        for iid in page.item_ids:
            seen_item_ids.add(iid)
        if page.cursor_out is not None:
            seen_next_cursors.add(page.cursor_out)
        for ov in page.ordering_values:
            last_ordering = ov

    return PaginationState(
        seen_item_ids=seen_item_ids,
        seen_next_cursors=seen_next_cursors,
        last_ordering_value=last_ordering,
        pages_seen=pages_completed,
        trace=subset,
        warnings=list(),
    )
