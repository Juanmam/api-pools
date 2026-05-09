"""TikTok Login Kit / Open API v2 video bindings (PARTIAL, video-as-post)."""

from __future__ import annotations

import json
from dataclasses import dataclass

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityContract, CapabilityLevel
from apipools.errors import NormalizationError, UnsupportedCapabilityError

from .deps import require_social_live
from .http import GraphHttpTransport
from .normalize_tiktok import normalize_tiktok_video_post_v1
from .oauth import AccessTokenSource

_VIDEO_FIELDS = "id,title,video_description,create_time,duration,cover_image_url,share_url"
_LIST_URL = "https://open.tiktokapis.com/v2/video/list/"
_QUERY_URL = "https://open.tiktokapis.com/v2/video/query/"


def _assert_tiktok_ok(payload: dict) -> None:
    err = payload.get("error")
    if not isinstance(err, dict):
        return
    code = err.get("code")
    if isinstance(code, str) and code.lower() == "ok":
        return
    if code in ("0", 0, None):
        return
    raise NormalizationError(
        message="TikTok API returned a non-OK error envelope.",
        operation="read",
        resource="post",
        detail=json.dumps(err, sort_keys=True),
    )


def _video_wire(node: dict, creator_open_id: str) -> dict:
    ct = node.get("create_time")
    return {
        "_provider": "tiktok_open_v2_video",
        "id": str(node.get("id") or ""),
        "title": node.get("title"),
        "video_description": node.get("video_description"),
        "create_time": None if ct is None else str(ct),
        "creator_open_id": creator_open_id,
    }


@dataclass
class TikTokOpenBinding:
    """
    Video listing and single-video query for the authorized TikTok user.

    ``creator_open_id`` is the OAuth ``open_id`` for the bearer token (caller-supplied).

    Comment reads are not declared in ``capabilities()``; ``fetch_comment`` always raises.
    """

    creator_open_id: str
    token_source: AccessTokenSource
    transport: GraphHttpTransport | None = None
    call_count: int = 0

    def __post_init__(self) -> None:
        require_social_live()

    @property
    def binding_id(self) -> str:
        return f"tiktok_open_v2:{self.creator_open_id}"

    def _transport(self) -> GraphHttpTransport:
        return self.transport or GraphHttpTransport()

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token_source()}"}

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
        )

    def fetch_post(self, provider_post_id: str) -> dict:
        self.call_count += 1
        tr = self._transport()
        body = {"filters": {"video_ids": [provider_post_id]}}
        data = tr.request_json(
            "POST",
            _QUERY_URL,
            params={"fields": _VIDEO_FIELDS},
            headers=self._auth_headers(),
            json_body=body,
        )
        _assert_tiktok_ok(data)
        payload = data.get("data")
        inner = payload if isinstance(payload, dict) else {}
        videos = inner.get("videos") or []
        if not videos:
            raise NormalizationError(
                message="TikTok video query returned no items for id.",
                operation="read",
                resource="post",
                detail=f"id={provider_post_id}",
            )
        return _video_wire(videos[0], self.creator_open_id)

    def fetch_comment(self, provider_comment_id: str) -> dict:
        raise UnsupportedCapabilityError(
            message="TikTok Open API video.list / video.query does not expose comment reads.",
            operation="read",
            resource="comment",
            detail=f"ignored_id={provider_comment_id!r}",
        )

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        self.call_count += 1
        tr = self._transport()
        body: dict[str, object] = {"max_count": max(1, min(limit, 20))}
        if provider_cursor:
            cur = json.loads(provider_cursor)
            if cur.get("cursor") is not None:
                body["cursor"] = cur["cursor"]

        data = tr.request_json(
            "POST",
            _LIST_URL,
            params={"fields": _VIDEO_FIELDS},
            headers=self._auth_headers(),
            json_body=body,
        )
        _assert_tiktok_ok(data)
        payload = data.get("data")
        inner = payload if isinstance(payload, dict) else {}
        videos = inner.get("videos") or []
        has_more = bool(inner.get("has_more"))
        next_cursor_val = inner.get("cursor")
        items = [_video_wire(v, self.creator_open_id) for v in videos][:limit]
        next_max_id = None
        if has_more and next_cursor_val is not None:
            next_max_id = json.dumps({"cursor": next_cursor_val})
        return {
            "items": items,
            "next_max_id": next_max_id,
            "more_available": has_more,
        }

    def normalize_post(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalPost, str | None]:
        return normalize_tiktok_video_post_v1(wire, projection, version)

    def normalize_comment(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalComment, str | None]:
        raise NormalizationError(
            message="TikTok binding does not normalize comments.",
            operation="read",
            resource="comment",
            detail=f"unexpected_wire_keys={sorted(wire)!r}",
        )


__all__ = ["TikTokOpenBinding"]
