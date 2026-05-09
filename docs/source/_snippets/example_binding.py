# Example-only: implement ``SocialSemanticBinding`` in your application.
# (Not executed by Sphinx; included via literalinclude in quickstart.)

from __future__ import annotations

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityContract, CapabilityLevel


class MyBinding:
    binding_id = "example"

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        return (
            CapabilityContract(
                resource="post",
                operation="read",
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "text"}),
                unsupported_fields=frozenset(),
            ),
        )

    def fetch_post(self, provider_post_id: str) -> dict:
        return {"id": provider_post_id, "text": "hello"}

    def fetch_comment(self, provider_comment_id: str) -> dict:
        return {"id": provider_comment_id}

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        return {"items": [], "next_max_id": None, "more_available": False}

    def normalize_post(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalPost, str | None]:
        raise NotImplementedError  # map wire → CanonicalPost in your adapter

    def normalize_comment(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalComment, str | None]:
        raise NotImplementedError
