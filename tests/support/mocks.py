"""Mock provider adapters for validation and pagination tests."""

from __future__ import annotations

from dataclasses import dataclass

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityContract, CapabilityLevel

from .legacy_normalization import normalize_comment_v1, normalize_post_v1


@dataclass
class MockInstagramAPI:
    """Mock adapter returning non-canonical wire shapes."""

    call_count: int = 0
    binding_id: str = "mock_instagram"

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        return (
            CapabilityContract(
                resource="post",
                operation="read",
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
            CapabilityContract(
                resource="post",
                operation="list",
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
            CapabilityContract(
                resource="comment",
                operation="read",
                level=CapabilityLevel.PARTIAL,
                supported_fields=frozenset({"id", "post_id", "author_id", "created_at"}),
                unsupported_fields=frozenset({"text"}),
            ),
        )

    @staticmethod
    def normalize_post(wire: dict, projection: set[str], version: str) -> tuple[CanonicalPost, str | None]:
        return normalize_post_v1(wire=wire, projection=projection, version=version)

    @staticmethod
    def normalize_comment(wire: dict, projection: set[str], version: str) -> tuple[CanonicalComment, str | None]:
        return normalize_comment_v1(wire=wire, projection=projection, version=version)

    def fetch_post(self, provider_post_id: str) -> dict:
        self.call_count += 1
        return {
            "pk": provider_post_id,
            "caption": "hello world",
            "owner": {"id": "u-1"},
            "taken_at_iso": "2026-05-07T10:00:00Z",
        }

    def fetch_comment(self, provider_comment_id: str) -> dict:
        self.call_count += 1
        return {
            "pk": provider_comment_id,
            "media_pk": "p-1",
            "owner": {"id": "u-2"},
            "taken_at_iso": "2026-05-07T11:00:00Z",
            # Intentionally no comment text to exercise explicit partiality.
        }

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        self.call_count += 1
        if provider_cursor is None:
            return {
                "items": [
                    {
                        "pk": "p-1",
                        "caption": "post 1",
                        "owner": {"id": "u-1"},
                        "taken_at_iso": "2026-05-07T10:00:00Z",
                    },
                    {
                        "pk": "p-2",
                        "caption": "post 2",
                        "owner": {"id": "u-2"},
                        "taken_at_iso": "2026-05-07T10:05:00Z",
                    },
                ][:limit],
                "next_max_id": "provider-page-2",
                "more_available": True,
            }
        return {
            "items": [
                {
                    "pk": "p-3",
                    "caption": "post 3",
                    "owner": {"id": "u-3"},
                    "taken_at_iso": "2026-05-07T10:10:00Z",
                }
            ][:limit],
            "next_max_id": None,
            "more_available": False,
        }
