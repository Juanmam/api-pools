"""Demo CoreProvider implementations for multi-binding tests (not shipped in ``apipools``)."""

from __future__ import annotations

from dataclasses import dataclass

from apipools.capabilities import CapabilityContract, CapabilityLevel
from apipools.core.providers.base import ProviderRequest


@dataclass
class ProviderA:
    provider_id: str = "provider_a"
    cursor_kind: str = "cursor"
    execution_count: int = 0

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
        )

    def execute(self, request: ProviderRequest) -> dict:
        self.execution_count += 1
        if request.operation == "read":
            return {
                "provider_id": self.provider_id,
                "item": {
                    "id": "a-post-1",
                    "text": "provider-a text",
                    "author_id": "a-user-1",
                    "created_at": "2026-05-07T12:00:00Z",
                },
                "cursor_format": self.cursor_kind,
            }
        return {
            "provider_id": self.provider_id,
            "items": [
                {
                    "id": "a-post-1",
                    "text": "provider-a list text",
                    "author_id": "a-user-1",
                    "created_at": "2026-05-07T12:00:00Z",
                }
            ][: request.limit],
            "next_cursor": "opaque-a-next" if request.cursor is None else None,
            "has_more": request.cursor is None,
            "cursor_format": self.cursor_kind,
        }


@dataclass
class ProviderB:
    provider_id: str = "provider_b"
    cursor_kind: str = "offset"
    execution_count: int = 0

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        return (
            CapabilityContract(
                resource="post",
                operation="read",
                level=CapabilityLevel.PARTIAL,
                supported_fields=frozenset({"id", "text", "author_id"}),
                unsupported_fields=frozenset({"created_at", "rich_media_metadata"}),
            ),
            CapabilityContract(
                resource="post",
                operation="list",
                level=CapabilityLevel.PARTIAL,
                supported_fields=frozenset({"id", "text", "author_id"}),
                unsupported_fields=frozenset({"created_at", "rich_media_metadata"}),
            ),
        )

    def execute(self, request: ProviderRequest) -> dict:
        self.execution_count += 1
        if request.operation == "read":
            return {
                "provider_id": self.provider_id,
                "item": {
                    "id": "b-post-1",
                    "text": "provider-b text",
                    "author_id": "b-user-1",
                },
                "cursor_format": self.cursor_kind,
            }
        offset = int(request.cursor or "0")
        return {
            "provider_id": self.provider_id,
            "items": [
                {
                    "id": f"b-post-{offset + 1}",
                    "text": "provider-b list text",
                    "author_id": "b-user-1",
                }
            ][: request.limit],
            "next_cursor": str(offset + request.limit) if offset == 0 else None,
            "has_more": offset == 0,
            "cursor_format": self.cursor_kind,
        }
