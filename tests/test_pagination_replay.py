"""ReplayCheckpoint and resume_from_checkpoint behavior."""

from dataclasses import replace

import pytest

from apipools.errors import PaginationInvariantError
from apipools.pagination import (
    PaginationConfig,
    PaginationEngine,
    PaginationFetchResult,
    PaginationState,
)


def _norm(wire: dict) -> tuple[dict, None]:

    return wire, None


def test_resume_from_checkpoint_continues_forward() -> None:

    engine = PaginationEngine(
        PaginationConfig(
            ordering_key="n",
            emit_replay_checkpoint=True,
            return_trace=False,
        )
    )

    state = PaginationState()

    def fetch_p1(cursor: str | None, limit: int) -> PaginationFetchResult[dict]:

        assert cursor is None

        return PaginationFetchResult(
            items=[{"id": "a", "n": 1}],
            next_cursor="c1",
            has_more=True,
        )

    engine.paginate(
        fetch=fetch_p1,
        cursor_token=None,
        normalize=_norm,
        state=state,
        limit=10,
        operation="list",
        resource="post",
    )

    ck = state.last_replay_checkpoint

    assert ck is not None

    assert ck.cursor == "c1"

    assert ck.page_index == 0

    def fetch_p2(cursor: str | None, limit: int) -> PaginationFetchResult[dict]:

        assert cursor == "c1"

        return PaginationFetchResult(
            items=[{"id": "b", "n": 2}],
            next_cursor=None,
            has_more=False,
        )

    page2 = engine.resume_from_checkpoint(
        checkpoint=ck,
        trace=state.trace,
        fetch=fetch_p2,
        normalize=_norm,
        limit=10,
        operation="list",
        resource="post",
    )

    assert [i["id"] for i in page2.items] == ["b"]

    assert page2.next_cursor is None


def test_resume_rejects_duplicate_items() -> None:

    engine = PaginationEngine(PaginationConfig(ordering_key="n", emit_replay_checkpoint=True))

    state = PaginationState()

    engine.paginate(
        fetch=lambda c, _: PaginationFetchResult(
            items=[{"id": "a", "n": 1}],
            next_cursor="c1",
            has_more=True,
        ),
        cursor_token=None,
        normalize=_norm,
        state=state,
        limit=10,
        operation="list",
        resource="post",
    )

    ck = state.last_replay_checkpoint

    assert ck is not None

    def bad_fetch(cursor: str | None, limit: int) -> PaginationFetchResult[dict]:

        return PaginationFetchResult(
            items=[{"id": "a", "n": 1}],
            next_cursor=None,
            has_more=False,
        )

    with pytest.raises(PaginationInvariantError) as err:
        engine.resume_from_checkpoint(
            checkpoint=ck,
            trace=state.trace,
            fetch=bad_fetch,
            normalize=_norm,
            limit=10,
            operation="list",
            resource="post",
        )

    assert err.value.detail == "duplicate_item_detected"


def test_resume_rejects_ordering_regression() -> None:

    engine = PaginationEngine(PaginationConfig(ordering_key="n", emit_replay_checkpoint=True))

    state = PaginationState()

    engine.paginate(
        fetch=lambda c, _: PaginationFetchResult(
            items=[{"id": "a", "n": 5}],
            next_cursor="c1",
            has_more=True,
        ),
        cursor_token=None,
        normalize=_norm,
        state=state,
        limit=10,
        operation="list",
        resource="post",
    )

    ck = state.last_replay_checkpoint

    def bad_fetch(cursor: str | None, limit: int) -> PaginationFetchResult[dict]:

        return PaginationFetchResult(
            items=[{"id": "b", "n": 3}],
            next_cursor=None,
            has_more=False,
        )

    with pytest.raises(PaginationInvariantError) as err:
        engine.resume_from_checkpoint(
            checkpoint=ck,
            trace=state.trace,
            fetch=bad_fetch,
            normalize=_norm,
            limit=10,
            operation="list",
            resource="post",
        )

    assert err.value.detail == "non_monotonic_ordering_detected"


def test_resume_rejects_lineage_hash_mismatch() -> None:

    engine = PaginationEngine(PaginationConfig(ordering_key="n", emit_replay_checkpoint=True))

    state = PaginationState()

    engine.paginate(
        fetch=lambda c, _: PaginationFetchResult(
            items=[{"id": "a", "n": 1}],
            next_cursor="c1",
            has_more=True,
        ),
        cursor_token=None,
        normalize=_norm,
        state=state,
        limit=10,
        operation="list",
        resource="post",
    )

    ck = replace(state.last_replay_checkpoint, lineage_hash="deadbeef")

    def fetch_ok(cursor: str | None, limit: int) -> PaginationFetchResult[dict]:

        return PaginationFetchResult(
            items=[{"id": "b", "n": 2}],
            next_cursor=None,
            has_more=False,
        )

    with pytest.raises(PaginationInvariantError) as err:
        engine.resume_from_checkpoint(
            checkpoint=ck,
            trace=state.trace,
            fetch=fetch_ok,
            normalize=_norm,
            limit=10,
            operation="list",
            resource="post",
        )

    assert err.value.detail == "replay_lineage_hash_mismatch"


def test_replay_checkpoint_fields_are_deterministic() -> None:

    cfg = PaginationConfig(ordering_key="n", emit_replay_checkpoint=True)

    e1 = PaginationEngine(cfg)

    e2 = PaginationEngine(cfg)

    s1 = PaginationState()

    s2 = PaginationState()

    fetch = lambda c, _: PaginationFetchResult(
        items=[{"id": "a", "n": 1}, {"id": "b", "n": 2}],
        next_cursor="c1",
        has_more=True,
    )

    e1.paginate(
        fetch=fetch,
        cursor_token=None,
        normalize=_norm,
        state=s1,
        limit=10,
        operation="list",
        resource="post",
    )

    e2.paginate(
        fetch=fetch,
        cursor_token=None,
        normalize=_norm,
        state=s2,
        limit=10,
        operation="list",
        resource="post",
    )

    assert s1.last_replay_checkpoint == s2.last_replay_checkpoint


def test_resume_rejects_anchor_page_index_mismatch() -> None:
    engine = PaginationEngine(PaginationConfig(ordering_key="n", emit_replay_checkpoint=True))
    state = PaginationState()

    engine.paginate(
        fetch=lambda c, _: PaginationFetchResult(
            items=[{"id": "a", "n": 1}],
            next_cursor="c1",
            has_more=True,
        ),
        cursor_token=None,
        normalize=_norm,
        state=state,
        limit=10,
        operation="list",
        resource="post",
    )
    ck = replace(state.last_replay_checkpoint, page_index=99)
    with pytest.raises(PaginationInvariantError) as err:
        engine.resume_from_checkpoint(
            checkpoint=ck,
            trace=state.trace,
            fetch=lambda c, _: PaginationFetchResult(items=[], next_cursor=None, has_more=False),
            normalize=_norm,
            limit=10,
            operation="list",
            resource="post",
        )
    assert err.value.detail == "replay_checkpoint_anchor_page_index_mismatch"


def test_resume_rejects_trace_cursor_mismatch() -> None:

    engine = PaginationEngine(PaginationConfig(ordering_key="n", emit_replay_checkpoint=True))

    state = PaginationState()

    engine.paginate(
        fetch=lambda c, _: PaginationFetchResult(
            items=[{"id": "a", "n": 1}],
            next_cursor="c1",
            has_more=True,
        ),
        cursor_token=None,
        normalize=_norm,
        state=state,
        limit=10,
        operation="list",
        resource="post",
    )

    ck = state.last_replay_checkpoint

    bad_page = replace(
        state.trace.pages[0],
        cursor_out="wrong",
    )

    bad_trace = replace(state.trace, pages=(bad_page,))

    with pytest.raises(PaginationInvariantError) as err:
        engine.resume_from_checkpoint(
            checkpoint=ck,
            trace=bad_trace,
            fetch=lambda c, _: PaginationFetchResult(items=[], next_cursor=None, has_more=False),
            normalize=_norm,
            limit=10,
            operation="list",
            resource="post",
        )

    assert err.value.detail == "replay_checkpoint_trace_alignment_failed"
