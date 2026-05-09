"""Second mock provider for heterogeneity pressure testing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from apipools.canonical import CanonicalComment, CanonicalPost, FieldStatus, SemanticField
from apipools.capabilities import CapabilityContract, CapabilityLevel
from apipools.errors import NormalizationError, VersionMismatchError


@dataclass
class MockTwitterAPI:
    """Mock provider with intentional capability and data limitations."""

    call_count: int = 0
    binding_id: str = "mock_twitter"

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        return (
            CapabilityContract(
                resource="post",
                operation="read",
                level=CapabilityLevel.PARTIAL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset({"rich_media_metadata"}),
            ),
            CapabilityContract(
                resource="post",
                operation="list",
                level=CapabilityLevel.PARTIAL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset({"rich_media_metadata"}),
            ),
            CapabilityContract(
                resource="comment",
                operation="read",
                level=CapabilityLevel.UNSUPPORTED,
                supported_fields=frozenset(),
                unsupported_fields=frozenset({"id", "post_id", "text", "author_id", "created_at"}),
            ),
        )

    @staticmethod
    def _assert_version(version: str, operation: str, resource: str) -> None:
        if version != "v1":
            raise VersionMismatchError(
                message="Unsupported canonical version target.",
                operation=operation,
                resource=resource,
                detail=f"requested={version}, supported=v1",
            )

    @staticmethod
    def _to_iso8601(raw_ts: str) -> str:
        parsed = datetime.strptime(raw_ts, "%Y/%m/%d %H:%M:%S")
        return parsed.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z")

    @staticmethod
    def normalize_post(wire: dict, projection: set[str], version: str) -> tuple[CanonicalPost, str | None]:
        MockTwitterAPI._assert_version(version, "read", "post")
        try:
            post_id = wire["tweet_id"]
            created_at_raw = wire["created_time"]
        except KeyError as exc:
            raise NormalizationError(
                message="Unmappable provider payload for post.",
                operation="read",
                resource="post",
                detail=f"missing_key={exc}",
            ) from exc

        gap_parts: list[str] = []

        if "text" in projection:
            raw_text = wire.get("tweet_text")
            if raw_text is None:
                text_field = SemanticField[str](status=FieldStatus.MISSING)
            else:
                if len(raw_text) > 20:
                    gap_parts.append("post.text truncated_by_provider_limit")
                text_field = SemanticField(status=FieldStatus.VALUE, value=raw_text[:20])
        else:
            text_field = SemanticField[str](status=FieldStatus.UNREQUESTED)

        if "author_id" in projection:
            author = wire.get("author")
            if author is None:
                author_field = SemanticField[str](status=FieldStatus.UNKNOWN)
                gap_parts.append("post.author_id unknown_from_provider")
            else:
                author_id = author.get("user_key")
                if author_id is None:
                    author_field = SemanticField[str](status=FieldStatus.UNKNOWN)
                    gap_parts.append("post.author_id unknown_from_provider")
                else:
                    author_field = SemanticField(status=FieldStatus.VALUE, value=author_id)
        else:
            author_field = SemanticField[str](status=FieldStatus.UNREQUESTED)

        created_at_field = (
            SemanticField(
                status=FieldStatus.VALUE,
                value=MockTwitterAPI._to_iso8601(created_at_raw),
            )
            if "created_at" in projection
            else SemanticField(status=FieldStatus.UNREQUESTED)
        )

        post = CanonicalPost(
            id=post_id,
            text=text_field,
            author_id=author_field,
            created_at=created_at_field,
        )
        return post, ("; ".join(gap_parts) if gap_parts else None)

    @staticmethod
    def normalize_comment(wire: dict, projection: set[str], version: str) -> tuple[CanonicalComment, str | None]:
        MockTwitterAPI._assert_version(version, "read", "comment")
        raise NormalizationError(
            message="Comment normalization should never execute for unsupported capability.",
            operation="read",
            resource="comment",
            detail=f"wire={wire}, projection={sorted(projection)}",
        )

    def fetch_post(self, provider_post_id: str) -> dict:
        self.call_count += 1
        if provider_post_id == "t-missing-author":
            return {
                "tweet_id": provider_post_id,
                "tweet_text": "Short provider text",
                "author": None,
                "created_time": "2026/05/07 12:00:00",
            }
        return {
            "tweet_id": provider_post_id,
            "tweet_text": "This is a longer tweet text that will be truncated",
            "author": {"user_key": "tw-u-1"},
            "created_time": "2026/05/07 12:00:00",
        }

    def fetch_comment(self, provider_comment_id: str) -> dict:
        self.call_count += 1
        return {"id": provider_comment_id}

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        self.call_count += 1
        offset = int(provider_cursor) if provider_cursor else 0
        items = [
            {
                "tweet_id": "t-1",
                "tweet_text": "A provider tweet body with truncation",
                "author": {"user_key": "tw-u-1"},
                "created_time": "2026/05/07 12:00:00",
            },
            {
                "tweet_id": "t-2",
                "tweet_text": "Another provider tweet body",
                "author": None,
                "created_time": "2026/05/07 12:01:00",
            },
            {
                "tweet_id": "t-3",
                "tweet_text": None,
                "author": {"user_key": "tw-u-3"},
                "created_time": "2026/05/07 12:02:00",
            },
        ]
        page_items = items[offset : offset + limit]
        next_offset = offset + len(page_items)
        has_more = next_offset < len(items)
        return {
            "items": page_items,
            "next_max_id": str(next_offset) if has_more else None,
            "more_available": has_more,
        }
