"""Pagination invariant harness for provider-agnostic cursor flows."""

import re
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from apipools.canonical import CanonicalPost, FieldStatus, SemanticField
from apipools.capabilities import CapabilityContract, CapabilityLevel
from apipools.errors import ExpiredCursorError, PaginationInvariantError
from apipools.pagination import (
    CursorPaginationService,
    PaginationConfig,
    PaginationEngine,
    PaginationFetchResult,
    PaginationState,
)
from support.mocks import MockInstagramAPI
from support.twitter_mock import MockTwitterAPI


def _post(post_id: str) -> dict:
    n = int(post_id.split("-")[1])
    return {
        "pk": post_id,
        "caption": f"post {n}",
        "owner": {"id": f"u-{n}"},
        "taken_at_iso": f"2026-05-07T10:{n:02d}:00Z",
    }


@dataclass
class HarnessProvider:
    """Provider double with explicit page script and forward-only cursors."""

    page_script: dict[str | None, tuple[list[dict], str | None]]
    binding_id: str = "harness_provider"

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        return (
            CapabilityContract(
                resource="post",
                operation="list",
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
            CapabilityContract(
                resource="post",
                operation="read",
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
        )

    @staticmethod
    def normalize_post(
        wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalPost, str | None]:
        # Local minimal canonical mapping for harness-only tests.
        def field(name: str, value: str | None) -> SemanticField[str]:
            if name not in projection:
                return SemanticField(status=FieldStatus.UNREQUESTED)
            if value is None:
                return SemanticField(status=FieldStatus.MISSING)
            return SemanticField(status=FieldStatus.VALUE, value=value)

        post = CanonicalPost(
            id=wire["pk"],
            text=field("text", wire.get("caption")),
            author_id=field("author_id", wire["owner"]["id"]),
            created_at=field("created_at", wire["taken_at_iso"]),
        )
        return post, None

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        items, next_cursor = self.page_script.get(provider_cursor, ([], None))
        page_items = items[:limit]
        return {
            "items": page_items,
            "next_max_id": next_cursor,
            "more_available": next_cursor is not None,
        }

    def fetch_post(self, provider_post_id: str) -> dict:
        return _post(provider_post_id)

    def fetch_comment(self, provider_comment_id: str) -> dict:
        raise NotImplementedError

    @staticmethod
    def normalize_comment(wire: dict, projection: set[str], version: str):
        raise NotImplementedError


def _ordering_key(post: CanonicalPost) -> int:
    match = re.search(r"(\d+)$", post.id)
    return int(match.group(1)) if match else 0


def _run_engine(
    provider,
    *,
    page_limit: int = 2,
    initial_cursor: str | None = None,
    pagination: CursorPaginationService | None = None,
) -> tuple[list[str], PaginationState]:
    engine = PaginationEngine(
        PaginationConfig(
            strict_mode=True,
            ordering_key=_ordering_key,
            max_pages=100,
            require_contiguous_order=True,
            return_trace=True,
        )
    )
    state = PaginationState()
    token_cursor = initial_cursor
    ids: list[str] = []

    if pagination is None:
        pagination = CursorPaginationService(
            b"apipools-validation-slice-secret",
            binding_id=getattr(provider, "binding_id", "harness_provider"),
            ttl_seconds=3600.0,
            max_store_entries=256,
        )

    while True:

        def fetch(token: str | None, limit: int) -> PaginationFetchResult[dict]:
            provider_cursor = pagination.resolve(token, operation="list", resource="post")
            wire_page = provider.list_posts(provider_cursor=provider_cursor, limit=limit)
            next_token = pagination.issue(
                operation="list",
                resource="post",
                provider_cursor=wire_page["next_max_id"],
            )
            return PaginationFetchResult(
                items=wire_page["items"],
                next_cursor=next_token,
                has_more=wire_page["more_available"],
            )

        def normalize(raw: dict) -> tuple[CanonicalPost, str | None]:
            return provider.normalize_post(
                wire=raw,
                projection={"text", "author_id", "created_at"},
                version="v1",
            )

        page = engine.paginate(
            fetch=fetch,
            cursor_token=token_cursor,
            normalize=normalize,
            state=state,
            limit=page_limit,
            operation="list",
            resource="post",
        )
        ids.extend(item.id for item in page.items)
        if page.next_cursor is None:
            break
        token_cursor = page.next_cursor

    return ids, state


@pytest.mark.parametrize("provider", [MockInstagramAPI(), MockTwitterAPI()])
def test_stable_pagination_invariants_hold(provider) -> None:
    ids, state = _run_engine(provider, page_limit=2)
    assert len(ids) == len(set(ids))
    assert state.trace.length >= 1
    assert state.trace.length == state.pages_seen
    first = state.trace.pages[0]
    assert first.cursor_in is None
    assert tuple(ids[: len(first.item_ids)]) == first.item_ids


def test_duplicate_injection_is_detected() -> None:
    provider = HarnessProvider(
        page_script={
            None: ([_post("p-1"), _post("p-2")], "c1"),
            "c1": ([_post("p-2"), _post("p-3")], None),
        }
    )
    with pytest.raises(PaginationInvariantError, match="Pagination invariant violation") as err:
        _run_engine(provider, page_limit=2)
    assert err.value.page_index is not None
    assert err.value.trace_snapshot is not None
    assert err.value.trace_snapshot.length >= 1
    assert err.value.detail in err.value.trace_snapshot.pages[-1].anomalies


def test_missing_items_between_pages_is_detected() -> None:
    provider = HarnessProvider(
        page_script={
            None: ([_post("p-1"), _post("p-2")], "c1"),
            "c1": ([_post("p-4"), _post("p-5")], None),
        }
    )
    with pytest.raises(PaginationInvariantError, match="Pagination invariant violation") as err:
        _run_engine(provider, page_limit=2)
    assert err.value.trace_snapshot is not None
    assert "gap_detected_between_pages" in err.value.trace_snapshot.pages[-1].anomalies


def test_out_of_order_responses_are_detected() -> None:
    provider = HarnessProvider(
        page_script={
            None: ([_post("p-1"), _post("p-3")], "c1"),
            "c1": ([_post("p-2"), _post("p-4")], None),
        }
    )
    with pytest.raises(PaginationInvariantError, match="Pagination invariant violation") as err:
        _run_engine(provider, page_limit=2)
    assert err.value.trace_snapshot is not None
    assert err.value.page_index is not None
    assert err.value.detail in err.value.trace_snapshot.pages[-1].anomalies


def test_cursor_invalidation_is_explicit() -> None:
    pagination = CursorPaginationService(
        b"apipools-validation-slice-secret",
        binding_id="mock_instagram",
        ttl_seconds=10.0,
        max_store_entries=64,
    )
    with patch("time.monotonic", return_value=0.0):
        provider = MockInstagramAPI()
        wire_page = provider.list_posts(provider_cursor=None, limit=2)
        cursor = pagination.issue(
            operation="list",
            resource="post",
            provider_cursor=wire_page["next_max_id"],
        )

    assert cursor is not None
    with patch("time.monotonic", return_value=999.0):
        with pytest.raises(ExpiredCursorError):
            _run_engine(
                MockInstagramAPI(),
                page_limit=2,
                initial_cursor=cursor,
                pagination=pagination,
            )
