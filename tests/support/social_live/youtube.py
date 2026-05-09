"""YouTube Data API v3 binding (video-as-post, playlist uploads listing)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from apipools.canonical import CanonicalComment, CanonicalPost
from apipools.capabilities import CapabilityContract, CapabilityLevel

from .deps import require_social_live
from .http import GraphHttpTransport
from .normalize_youtube import normalize_youtube_comment_v1, normalize_youtube_video_post_v1
from .oauth import AccessTokenSource


def _video_wire_from_snippet(vid: str, snippet: dict) -> dict:
    return {
        "_provider": "youtube_data_v3_video",
        "id": vid,
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "channel_id": snippet.get("channelId"),
        "published_at": snippet.get("publishedAt"),
    }


def _comment_wire_from_resource(row: dict) -> dict | None:
    sid = row.get("id")
    snippet_raw = row.get("snippet")
    sn: dict = snippet_raw if isinstance(snippet_raw, dict) else {}
    cid = sid
    vid = sn.get("videoId")
    if not cid:
        return None
    author = sn.get("authorChannelId")
    if isinstance(author, dict):
        author = author.get("value")
    return {
        "_provider": "youtube_data_v3_comment",
        "id": str(cid),
        "video_id": str(vid or ""),
        "_snippet_flat": {
            "textOriginal": sn.get("textOriginal") or sn.get("textDisplay"),
            "authorChannelId": author,
            "publishedAt": sn.get("publishedAt"),
        },
    }


@dataclass
class YouTubeDataBinding:
    """
    Requires OAuth2 bearer access with YouTube Data API scope (caller supplies token).

    If ``uploads_playlist_id`` is omitted it is resolved once via ``channels.list``.
    Listing uses ``playlistItems.list`` on the uploads playlist.
    """

    channel_id: str
    token_source: AccessTokenSource
    uploads_playlist_id: str | None = None
    transport: GraphHttpTransport | None = None
    _resolved_playlist: str | None = field(default=None, repr=False)
    call_count: int = 0

    def __post_init__(self) -> None:
        require_social_live()

    @property
    def binding_id(self) -> str:
        return f"youtube_data_v3:{self.channel_id}"

    def _transport(self) -> GraphHttpTransport:
        return self.transport or GraphHttpTransport()

    def _bearer_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token_source()}"}

    def _playlist_id(self) -> str:
        if self.uploads_playlist_id:
            return self.uploads_playlist_id
        if self._resolved_playlist:
            return self._resolved_playlist
        tr = self._transport()
        url = "https://www.googleapis.com/youtube/v3/channels"
        data = tr.request_json(
            "GET",
            url,
            params={
                "part": "contentDetails",
                "id": self.channel_id,
            },
            headers=self._bearer_headers(),
        )
        items = data.get("items") or []
        if not items:
            from apipools.errors import NormalizationError

            raise NormalizationError(
                message="YouTube channels.list returned no items for channel.",
                operation="list",
                resource="post",
                detail=f"channel_id={self.channel_id}",
            )
        details = (items[0].get("contentDetails") or {}).get("relatedPlaylists") or {}
        uploads = details.get("uploads")
        if not uploads:
            from apipools.errors import NormalizationError

            raise NormalizationError(
                message="Channel uploads playlist id missing.",
                operation="list",
                resource="post",
                detail="relatedPlaylists.uploads",
            )
        self._resolved_playlist = str(uploads)
        return str(uploads)

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
                level=CapabilityLevel.PARTIAL,
                supported_fields=frozenset({"id", "post_id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
        )

    def fetch_post(self, provider_post_id: str) -> dict:
        self.call_count += 1
        tr = self._transport()
        data = tr.request_json(
            "GET",
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet",
                "id": provider_post_id,
            },
            headers=self._bearer_headers(),
        )
        items = data.get("items") or []
        if not items:
            from apipools.errors import NormalizationError

            raise NormalizationError(
                message="videos.list returned empty.",
                operation="read",
                resource="post",
                detail=f"id={provider_post_id}",
            )
        snip = (items[0].get("snippet") or {})
        return _video_wire_from_snippet(provider_post_id, snip)

    def fetch_comment(self, provider_comment_id: str) -> dict:
        self.call_count += 1
        tr = self._transport()
        data = tr.request_json(
            "GET",
            "https://www.googleapis.com/youtube/v3/comments",
            params={
                "part": "snippet",
                "id": provider_comment_id,
            },
            headers=self._bearer_headers(),
        )
        threads = data.get("items") or []
        if not threads:
            from apipools.errors import NormalizationError

            raise NormalizationError(
                message="comments.list by id returned empty.",
                operation="read",
                resource="comment",
                detail=f"id={provider_comment_id}",
            )
        w = _comment_wire_from_resource(threads[0])
        if w is None:
            raise NormalizationError(
                message="Could not derive comment resource wire.",
                operation="read",
                resource="comment",
                detail="missing_comment_wire",
            )
        return w

    def list_posts(self, provider_cursor: str | None, limit: int) -> dict:
        self.call_count += 1
        tr = self._transport()
        params: dict[str, object] = {
            "part": "snippet,contentDetails",
            "playlistId": self._playlist_id(),
            "maxResults": max(1, min(limit, 50)),
        }
        if provider_cursor:
            cur = json.loads(provider_cursor)
            if cur.get("page_token"):
                params["pageToken"] = cur["page_token"]

        data = tr.request_json(
            "GET",
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params,
            headers=self._bearer_headers(),
        )

        wires: list[dict] = []
        for row in data.get("items") or []:
            vid = (((row.get("contentDetails") or {}).get("videoId")) or "") or ""
            snip = row.get("snippet") or {}
            if not vid:
                continue
            wires.append(_video_wire_from_snippet(str(vid), snip))

        next_page = data.get("nextPageToken")
        wires = wires[:limit]
        next_max_id = json.dumps({"page_token": next_page}) if next_page else None
        more = bool(next_page)

        return {
            "items": wires,
            "next_max_id": next_max_id,
            "more_available": more,
        }

    def normalize_post(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalPost, str | None]:
        return normalize_youtube_video_post_v1(wire, projection, version)

    def normalize_comment(
        self, wire: dict, projection: set[str], version: str
    ) -> tuple[CanonicalComment, str | None]:
        return normalize_youtube_comment_v1(wire, projection, version)


__all__ = ["YouTubeDataBinding"]
