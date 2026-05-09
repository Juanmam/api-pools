"""Reference social strategy for tests (not part of the installable library API)."""

from __future__ import annotations

import re

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityRegistry
from apipools.errors import NormalizationError
from apipools.pagination import (
    CursorPaginationService,
    Page,
    PaginationConfig,
    PaginationEngine,
    PaginationFetchResult,
    PaginationState,
)
from apipools.protocols import SocialSemanticBinding

from .constants import DEFAULT_VALIDATION_CURSOR_SECRET
from .mocks import MockInstagramAPI

_LIST_OPERATION = "list"
_LIST_RESOURCE = "post"


class SocialAPIStrategy:
    """Bounded-context strategy exercising capabilities, normalization, and pagination."""

    def __init__(
        self,
        provider: SocialSemanticBinding | None = None,
        *,
        cursor_ttl_seconds: float = 3600.0,
        cursor_max_store_entries: int = 256,
    ) -> None:
        self.provider = provider or MockInstagramAPI()
        self.capabilities = CapabilityRegistry(self.provider.capabilities())
        binding_id = getattr(self.provider, "binding_id", "mock_instagram")
        self._pagination = CursorPaginationService(
            DEFAULT_VALIDATION_CURSOR_SECRET,
            binding_id=binding_id,
            ttl_seconds=cursor_ttl_seconds,
            max_store_entries=cursor_max_store_entries,
        )
        self._pagination_engine = PaginationEngine(
            PaginationConfig(
                strict_mode=True,
                ordering_key=_post_ordering_key,
                max_pages=100,
            )
        )
        self._pagination_state = PaginationState()
        self._expected_next_cursor: str | None = None

    def read_post(
        self,
        post_id: str,
        projection: set[str],
        *,
        require_full: bool = True,
        version: str = "v1",
    ) -> tuple[CanonicalPost, str | None]:
        validation = self.capabilities.validate(
            resource="post",
            operation="read",
            requested_fields=projection,
            require_full=require_full,
        )
        wire = self.provider.fetch_post(post_id)
        post, norm_gap = self.provider.normalize_post(wire=wire, projection=projection, version=version)
        if not post.id:
            raise NormalizationError(
                message="Canonical post identity missing.",
                operation="read",
                resource="post",
            )
        gap = validation.gap
        if norm_gap:
            gap = norm_gap if gap is None else f"{gap}; {norm_gap}"
        return post, gap

    def read_comment(
        self,
        comment_id: str,
        projection: set[str],
        *,
        require_full: bool = False,
        version: str = "v1",
    ) -> tuple[CanonicalComment, str | None]:
        validation = self.capabilities.validate(
            resource="comment",
            operation="read",
            requested_fields=projection,
            require_full=require_full,
        )
        wire = self.provider.fetch_comment(comment_id)
        comment, norm_gap = self.provider.normalize_comment(wire=wire, projection=projection, version=version)

        gap = validation.gap
        if norm_gap:
            gap = norm_gap if gap is None else f"{gap}; {norm_gap}"
        return comment, gap

    def list_posts(
        self,
        *,
        projection: set[str],
        cursor: str | None = None,
        limit: int = 2,
        require_full: bool = True,
        version: str = "v1",
    ) -> Page[CanonicalPost]:
        validation = self.capabilities.validate(
            resource="post",
            operation="list",
            requested_fields=projection,
            require_full=require_full,
        )
        if cursor is None or cursor != self._expected_next_cursor:
            self._pagination_state = PaginationState()

        def fetch_page(token: str | None, page_limit: int) -> PaginationFetchResult[dict]:
            provider_cursor = self._pagination.resolve(token, operation=_LIST_OPERATION, resource=_LIST_RESOURCE)
            wire_page = self.provider.list_posts(provider_cursor=provider_cursor, limit=page_limit)
            next_cursor = self._pagination.issue(
                operation=_LIST_OPERATION,
                resource=_LIST_RESOURCE,
                provider_cursor=wire_page["next_max_id"],
            )
            return PaginationFetchResult(
                items=wire_page["items"],
                next_cursor=next_cursor,
                has_more=wire_page["more_available"],
            )

        def normalize_item(item: dict) -> tuple[CanonicalPost, str | None]:
            return self.provider.normalize_post(wire=item, projection=projection, version=version)

        page = self._pagination_engine.paginate(
            fetch=fetch_page,
            cursor_token=cursor,
            normalize=normalize_item,
            state=self._pagination_state,
            limit=limit,
            operation=_LIST_OPERATION,
            resource=_LIST_RESOURCE,
        )

        gap = validation.gap
        if page.gap:
            gap = page.gap if gap is None else f"{gap}; {page.gap}"
        self._expected_next_cursor = page.next_cursor
        return Page(
            items=page.items,
            next_cursor=page.next_cursor,
            has_more=page.has_more,
            gap=gap,
        )


def _post_ordering_key(post: CanonicalPost) -> int:
    match = re.search(r"(\d+)$", post.id)
    if match is not None:
        return int(match.group(1))
    return 0
