"""Live Facebook Graph (Page feed) binding for ``SocialAPIStrategy``."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityContract, CapabilityLevel

from .deps import require_social_live
from .http import GraphHttpTransport
from .meta_client import MetaGraphClient
from .normalize_meta import (
    normalize_facebook_graph_comment_v1,
    normalize_facebook_graph_post_v1,
)
from .oauth import AccessTokenSource


def _post_node_to_wire(node: dict) -> dict:
    from_data = node.get("from") or {}
    return {
        "_provider": "facebook_graph",
        "id": str(node.get("id", "")),
        "message": node.get("message"),
        "created_time": node.get("created_time"),
        "author_id": str(from_data["id"]) if from_data.get("id") else None,
    }


def _comment_node_to_wire(node: dict) -> dict:
    parent = node.get("parent") or {}
    from_data = node.get("from") or {}
    return {
        "_provider": "facebook_graph_comment",
        "id": str(node.get("id", "")),
        "post_id": str(parent["id"]) if parent.get("id") else "",
        "message": node.get("message"),
        "created_time": node.get("created_time"),
        "author_id": str(from_data["id"]) if from_data.get("id") else None,
    }


_POST_FIELDS = "id,message,created_time,from"
_COMMENT_FIELDS = "id,message,created_time,from,parent"


@dataclass
class FacebookGraphBinding:
    """
    Page-backed feed binding (requires ``pages_read_engagement``, ``pages_show_list``, etc.,
    depending on scenario — see Meta developer docs).

    Uses Graph API pagination cursors serialized into ``next_max_id``.
    """

    page_id: str
    token_source: AccessTokenSource
    graph_version: str = "v21.0"
    transport: GraphHttpTransport | None = None
    _graph: MetaGraphClient | None = field(default=None, repr=False)
    call_count: int = 0

    def __post_init__(self) -> None:
        require_social_live()

    @property
    def binding_id(self) -> str:
        return f"facebook_graph:{self.page_id}"

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
        data = self._client().get_object(
            provider_post_id,
            fields=_POST_FIELDS,
        )
        return _post_node_to_wire(data)

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
            "fields": _POST_FIELDS,
            "limit": max(1, min(limit, 100)),
        }
        if provider_cursor:
            cur = json.loads(provider_cursor)
            if cur.get("after"):
                params["after"] = cur["after"]
        data = self._client().get_object(f"{self.page_id}/feed", **params)
        items = [_post_node_to_wire(x) for x in data.get("data") or []]
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
        return normalize_facebook_graph_post_v1(wire, projection, version)

    def normalize_comment(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalComment, str | None]:
        return normalize_facebook_graph_comment_v1(wire, projection, version)


__all__ = ["FacebookGraphBinding"]
