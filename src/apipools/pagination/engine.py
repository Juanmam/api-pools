"""Provider-agnostic pagination engine and invariant enforcement."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from ..errors import PaginationInvariantError
from .page import Page
from .replay import (
    ReplayCheckpoint,
    encode_ordering_value,
    hydrate_state_from_trace_prefix,
    lineage_hash_for_state,
)
from .trace import PageTrace, PaginationTrace

WireT = TypeVar("WireT")
ItemT = TypeVar("ItemT")


@dataclass(frozen=True)
class PaginationFetchResult(Generic[WireT]):
    """Normalized fetch envelope from any provider adapter."""

    items: Sequence[WireT]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True)
class PaginationConfig:
    """Engine behavior knobs for correctness enforcement."""

    strict_mode: bool = True
    ordering_key: str | Callable[[Any], Any] | None = "id"
    max_pages: int = 100
    require_contiguous_order: bool = False
    return_trace: bool = False
    emit_replay_checkpoint: bool = False


@dataclass
class PaginationState:
    """Cross-page lineage state for one forward-only stream."""

    seen_item_ids: set[str] = field(default_factory=set)
    seen_next_cursors: set[str] = field(default_factory=set)
    last_ordering_value: Any | None = None
    pages_seen: int = 0
    warnings: list[str] = field(default_factory=list)
    trace: PaginationTrace = field(default_factory=PaginationTrace)
    last_trace: PaginationTrace | None = None
    last_replay_checkpoint: ReplayCheckpoint | None = None


class PaginationEngine:
    """Single authority for pagination correctness invariants."""

    def __init__(self, config: PaginationConfig | None = None) -> None:
        self._config = config or PaginationConfig()

    def paginate(
        self,
        *,
        fetch: Callable[[str | None, int], PaginationFetchResult[WireT]],
        cursor_token: str | None,
        normalize: Callable[[WireT], tuple[ItemT, str | None]],
        state: PaginationState,
        limit: int,
        operation: str,
        resource: str,
    ) -> Page[ItemT]:
        page_index = state.pages_seen
        state.pages_seen += 1
        anomalies: list[str] = []

        self._enforce(
            state.pages_seen <= self._config.max_pages,
            "max_pages_exceeded",
            operation=operation,
            resource=resource,
            state=state,
            page_index=page_index,
            cursor=cursor_token,
            anomalies=anomalies,
        )

        fetched = fetch(cursor_token, limit)
        self._enforce(
            not (fetched.has_more and fetched.next_cursor is None),
            "has_more_without_next_cursor",
            operation=operation,
            resource=resource,
            state=state,
            page_index=page_index,
            cursor=cursor_token,
            anomalies=anomalies,
        )
        self._enforce(
            not ((not fetched.has_more) and fetched.next_cursor is not None),
            "next_cursor_present_when_has_more_false",
            operation=operation,
            resource=resource,
            state=state,
            page_index=page_index,
            cursor=cursor_token,
            anomalies=anomalies,
        )
        self._enforce(
            not (fetched.has_more and len(fetched.items) == 0),
            "empty_page_with_has_more",
            operation=operation,
            resource=resource,
            state=state,
            page_index=page_index,
            cursor=cursor_token,
            anomalies=anomalies,
        )
        self._enforce(
            fetched.next_cursor != cursor_token or fetched.next_cursor is None,
            "cursor_reuse_detected",
            operation=operation,
            resource=resource,
            state=state,
            page_index=page_index,
            cursor=cursor_token,
            anomalies=anomalies,
        )
        self._enforce(
            fetched.next_cursor not in state.seen_next_cursors,
            "cursor_lineage_loop_detected",
            operation=operation,
            resource=resource,
            state=state,
            page_index=page_index,
            cursor=cursor_token,
            anomalies=anomalies,
        )

        items: list[ItemT] = []
        gaps: list[str] = []
        item_ids: list[str] = []
        ordering_values: list[Any] = []
        for raw in fetched.items:
            item, gap = normalize(raw)
            try:
                item_id = _item_id(item)
                ordering_value = (
                    _ordering_value(item, self._config.ordering_key)
                    if self._config.ordering_key is not None
                    else None
                )
                self._enforce_monotonic(
                    ordering_value,
                    state,
                    operation=operation,
                    resource=resource,
                    page_index=page_index,
                    cursor=cursor_token,
                    anomalies=anomalies,
                    offending_item=item,
                )
            except ValueError as exc:
                anomalies.append(f"invalid_item_shape:{exc}")
                raise PaginationInvariantError(
                    message="Pagination invariant violation.",
                    operation=operation,
                    resource=resource,
                    detail=f"invalid_item_shape:{exc}",
                    page_index=page_index,
                    cursor=cursor_token,
                    offending_item=item,
                    trace_snapshot=self._snapshot_with_anomaly(state, cursor_token, anomalies),
                ) from exc
            self._enforce(
                item_id not in state.seen_item_ids,
                "duplicate_item_detected",
                operation=operation,
                resource=resource,
                state=state,
                page_index=page_index,
                cursor=cursor_token,
                anomalies=anomalies,
                offending_item=item,
            )
            state.seen_item_ids.add(item_id)
            items.append(item)
            item_ids.append(item_id)
            if ordering_value is not None:
                ordering_values.append(ordering_value)
            if gap:
                gaps.append(gap)

        if fetched.next_cursor is not None:
            state.seen_next_cursors.add(fetched.next_cursor)

        page_trace = PageTrace(
            cursor_in=cursor_token,
            cursor_out=fetched.next_cursor,
            item_ids=tuple(item_ids),
            ordering_values=tuple(ordering_values),
            has_more=fetched.has_more,
            anomalies=tuple(anomalies),
        )
        state.trace = state.trace.append(page_trace)
        if self._config.return_trace:
            state.last_trace = state.trace
        if self._config.emit_replay_checkpoint:
            last_id = item_ids[-1] if item_ids else ""
            ov_enc = encode_ordering_value(ordering_values[-1]) if ordering_values else ""
            state.last_replay_checkpoint = ReplayCheckpoint(
                cursor=fetched.next_cursor,
                page_index=page_index,
                last_item_id=last_id,
                ordering_value=ov_enc,
                lineage_hash=lineage_hash_for_state(
                    state.seen_item_ids,
                    state.seen_next_cursors,
                    state.pages_seen,
                ),
                trace_anchor=page_index,
            )

        return Page(
            items=items,
            next_cursor=fetched.next_cursor,
            has_more=fetched.has_more,
            gap="; ".join(gaps) if gaps else None,
        )

    def _enforce_monotonic(
        self,
        ordering_value: Any,
        state: PaginationState,
        *,
        operation: str,
        resource: str,
        page_index: int,
        cursor: str | None,
        anomalies: list[str],
        offending_item: Any | None = None,
    ) -> None:
        if ordering_value is None:
            return
        if state.last_ordering_value is not None:
            self._enforce(
                ordering_value >= state.last_ordering_value,
                "non_monotonic_ordering_detected",
                operation=operation,
                resource=resource,
                state=state,
                page_index=page_index,
                cursor=cursor,
                anomalies=anomalies,
                offending_item=offending_item,
            )
            if self._config.require_contiguous_order:
                if isinstance(ordering_value, int) and isinstance(state.last_ordering_value, int):
                    self._enforce(
                        ordering_value == state.last_ordering_value + 1,
                        "gap_detected_between_pages",
                        operation=operation,
                        resource=resource,
                        state=state,
                        page_index=page_index,
                        cursor=cursor,
                        anomalies=anomalies,
                        offending_item=offending_item,
                    )
        state.last_ordering_value = ordering_value

    def _enforce(
        self,
        condition: bool,
        detail: str,
        *,
        operation: str,
        resource: str,
        state: PaginationState,
        page_index: int,
        cursor: str | None,
        anomalies: list[str],
        offending_item: Any | None = None,
    ) -> None:
        if condition:
            return
        anomalies.append(detail)
        if self._config.strict_mode:
            raise PaginationInvariantError(
                message="Pagination invariant violation.",
                operation=operation,
                resource=resource,
                detail=detail,
                page_index=page_index,
                cursor=cursor,
                offending_item=offending_item,
                trace_snapshot=self._snapshot_with_anomaly(state, cursor, anomalies),
            )
        state.warnings.append(detail)

    @staticmethod
    def _snapshot_with_anomaly(
        state: PaginationState, cursor: str | None, anomalies: list[str]
    ) -> PaginationTrace:
        if not anomalies:
            return state.trace
        provisional = PageTrace(
            cursor_in=cursor,
            cursor_out=None,
            item_ids=(),
            ordering_values=(),
            has_more=False,
            anomalies=tuple(anomalies),
        )
        return state.trace.append(provisional)

    def resume_from_checkpoint(
        self,
        *,
        checkpoint: ReplayCheckpoint,
        trace: PaginationTrace,
        fetch: Callable[[str | None, int], PaginationFetchResult[WireT]],
        normalize: Callable[[WireT], tuple[ItemT, str | None]],
        limit: int,
        operation: str,
        resource: str,
    ) -> Page[ItemT]:
        """Continue pagination after validating a trace-linked replay boundary."""

        def _replay_violation(detail: str) -> PaginationInvariantError:
            return PaginationInvariantError(
                message="Replay checkpoint validation failed.",
                operation=operation,
                resource=resource,
                detail=detail,
                trace_snapshot=trace,
            )

        if checkpoint.trace_anchor != checkpoint.page_index:
            raise _replay_violation("replay_checkpoint_anchor_page_index_mismatch")
        if trace.length <= checkpoint.trace_anchor:
            raise _replay_violation("trace_shorter_than_checkpoint_anchor")
        trace_page = trace.pages[checkpoint.trace_anchor]
        if not checkpoint.aligns_with_trace(trace_page=trace_page):
            raise _replay_violation("replay_checkpoint_trace_alignment_failed")
        hydrated = hydrate_state_from_trace_prefix(trace, checkpoint.trace_anchor)
        expected_lineage = lineage_hash_for_state(
            hydrated.seen_item_ids,
            hydrated.seen_next_cursors,
            hydrated.pages_seen,
        )
        if expected_lineage != checkpoint.lineage_hash:
            raise _replay_violation("replay_lineage_hash_mismatch")
        hydrated.last_replay_checkpoint = None
        return self.paginate(
            fetch=fetch,
            cursor_token=checkpoint.cursor,
            normalize=normalize,
            state=hydrated,
            limit=limit,
            operation=operation,
            resource=resource,
        )


def _item_id(item: Any) -> str:
    if isinstance(item, dict) and "id" in item:
        return str(item["id"])
    if hasattr(item, "id"):
        return str(getattr(item, "id"))
    raise ValueError("Unable to extract item id for pagination invariant checks.")


def _ordering_value(item: Any, ordering_key: str | Callable[[Any], Any]) -> Any:
    if callable(ordering_key):
        return ordering_key(item)
    if isinstance(item, dict):
        if ordering_key not in item:
            raise ValueError(f"Ordering key '{ordering_key}' is missing on item dict.")
        return item[ordering_key]
    if not hasattr(item, ordering_key):
        raise ValueError(f"Ordering key '{ordering_key}' is missing on item object.")
    return getattr(item, ordering_key)
