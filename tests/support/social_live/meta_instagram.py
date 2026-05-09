"""Live Instagram Graph (Business/Creator IG user media) binding."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityContract, CapabilityLevel

from .deps import require_social_live
from .http import GraphHttpTransport
from .meta_client import MetaGraphClient
from .normalize_meta import (
    normalize_instagram_graph_comment_v1,
    normalize_instagram_graph_post_v1,
)
from .oauth import AccessTokenSource

_MEDIA_FIELDS = "id,caption,media_type,permalink,timestamp,owner{id,username}"
_COMMENT_FIELDS = "id,text,timestamp,username,user{id,username},media{id}"


def _media_node_to_wire(node: dict) -> dict:
    owner = node.get("owner") or {}
    oid = owner.get("id") or owner.get("username")
    return {
        "_provider": "instagram_graph",
        "id": str(node.get("id", "")),
        "caption": node.get("caption"),
        "timestamp": node.get("timestamp"),
        "author_id": str(oid) if oid else None,
    }


def _comment_node_to_wire(node: dict) -> dict:
    media = node.get("media") or {}
    user_blk = node.get("user") or {}
    ig_id = user_blk.get("id")
    uname = node.get("username") or user_blk.get("username")
    return {
        "_provider": "instagram_graph_comment",
        "id": str(node.get("id", "")),
        "media_id": str(media.get("id", "")),
        "text": node.get("text"),
        "timestamp": node.get("timestamp"),
        "author_id": str(ig_id) if ig_id else None,
        "username": str(uname) if uname else None,
    }


@dataclass
class InstagramGraphBinding:
    """
    Instagram User media timeline via Graph ``/{ig-user-id}/media``.

    Requires the appropriate Instagram Graph permissions and a valid user/Page token.
    """

    instagram_user_id: str
    token_source: AccessTokenSource
    graph_version: str = "v21.0"
    transport: GraphHttpTransport | None = None
    _graph: MetaGraphClient | None = field(default=None, repr=False)
    call_count: int = 0

    def __post_init__(self) -> None:
        require_social_live()

    @property
    def binding_id(self) -> str:
        return f"instagram_graph:{self.instagram_user_id}"

    def _client(self) -> MetaGraphClient:
        if self._graph is None:
            self._graph = MetaGraphClient(
                self.token_source,
                graph_version=self.graph_version,
                transport=self.transport,
            )
        return self._graph

    def close(self) -> None:
        if self._graph is not None:
            self._graph.close()

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
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "post_id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
        )

    def fetch_post(self, provider_post_id: str) -> dict:
        self.call_count += 1
        data = self._client().get_object(provider_post_id, fields=_MEDIA_FIELDS)
        return _media_node_to_wire(data)

    def fetch_comment(self, provider_comment_id: str) -> dict:
        self.call_count += 1
        data = self._client().get_object(
            provider_comment_id,
            fields=_COMMENT_FIELDS,
        )
        return _comment_node_to_wire(data)

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        self.call_count += 1
        params: dict[str, object] = {
            "fields": _MEDIA_FIELDS,
            "limit": max(1, min(limit, 100)),
        }
        if provider_cursor:
            cur = json.loads(provider_cursor)
            if cur.get("after"):
                params["after"] = cur["after"]
        data = self._client().get_object(f"{self.instagram_user_id}/media", **params)
        items = [_media_node_to_wire(x) for x in data.get("data") or []]
        paging = data.get("paging") or {}
        cursors = paging.get("cursors") or {}
        after = cursors.get("after")
        has_more = paging.get("next") is not None
        next_max_id = json.dumps({"after": after}) if after and has_more else None
        return {
            "items": items[:limit],
            "next_max_id": next_max_id,
            "more_available": has_more,
        }

    def normalize_post(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalPost, str | None]:
        return normalize_instagram_graph_post_v1(wire, projection, version)

    def normalize_comment(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalComment, str | None]:
        return normalize_instagram_graph_comment_v1(wire, projection, version)


__all__ = ["InstagramGraphBinding"]
