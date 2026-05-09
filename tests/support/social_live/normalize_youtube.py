"""Pure normalizers for YouTube Data API v3 shaped wire dicts."""

from __future__ import annotations

from apipools.canonical import CanonicalComment, CanonicalPost, FieldStatus, SemanticField
from apipools.errors import NormalizationError
from apipools.versioning import assert_supported_projection_version

_SUPPORTED_V1 = frozenset({"v1"})


def normalize_youtube_video_post_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalPost, str | None]:
    """Map a YouTube ``video``-as-post projection (canonical v1).

    ``text`` combines title + description with an explicit truncation gap when lengthy.
    """
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="post")
    if wire.get("_provider") != "youtube_data_v3_video":
        raise NormalizationError(
            message="Wrong wire kind for YouTube video post normalizer.",
            operation="read",
            resource="post",
            detail=f"provider={wire.get('_provider')!r}",
        )
    vid = str(wire.get("id") or "")
    if not vid:
        raise NormalizationError(
            message="YouTube wire missing video id.",
            operation="read",
            resource="post",
            detail="missing_id",
        )

    title = wire.get("title") or ""
    desc = wire.get("description") or ""
    combined = (
        str(title).strip() + ("\n\n" + str(desc).strip() if str(desc).strip() else "")
    ).strip()

    base_gap = "youtube.video_as_post.mapping; text merges title + description"
    max_text = 2800
    gap: str | None
    if len(combined) > max_text:
        gap = (
            base_gap
            + "; text_truncated="
            + str(len(combined))
            + "->"
            + str(max_text)
        )
        combined = combined[:max_text]
    else:
        gap = base_gap

    channel_id = wire.get("channel_id")
    published_at = wire.get("published_at")

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    post = CanonicalPost(
        id=vid,
        text=field("text", combined if combined else None),
        author_id=field(
            "author_id", None if channel_id is None else str(channel_id)
        ),
        created_at=field(
            "created_at", None if published_at is None else str(published_at)
        ),
    )
    return post, gap


def normalize_youtube_comment_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalComment, str | None]:
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="comment")
    if wire.get("_provider") != "youtube_data_v3_comment":
        raise NormalizationError(
            message="Wrong wire kind for YouTube comment normalizer.",
            operation="read",
            resource="comment",
            detail=f"provider={wire.get('_provider')!r}",
        )

    cid = str(wire.get("id") or "")
    vid = str(wire.get("video_id") or "")
    if not cid:
        raise NormalizationError(
            message="YouTube comment wire missing id.",
            operation="read",
            resource="comment",
            detail="missing_id",
        )
    if not vid:
        raise NormalizationError(
            message="YouTube comment missing video linkage.",
            operation="read",
            resource="comment",
            detail="missing_video_id",
        )

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    snippet = wire.get("_snippet_flat") if isinstance(wire.get("_snippet_flat"), dict) else {}
    gap = (
        "youtube.comments_list.flat_snippet_projection"
        if snippet
        else "youtube.comments_list.minimal_projection"
    )

    text_raw = snippet.get("textOriginal") if snippet else wire.get("text_original")
    author = snippet.get("authorChannelId") if snippet else wire.get("author_channel_id")
    ts = snippet.get("publishedAt") if snippet else wire.get("published_at")

    comment = CanonicalComment(
        id=cid,
        post_id=vid,
        text=field("text", None if text_raw is None else str(text_raw)),
        author_id=field("author_id", None if author is None else str(author)),
        created_at=field("created_at", None if ts is None else str(ts)),
    )
    return comment, gap


__all__ = ["normalize_youtube_comment_v1", "normalize_youtube_video_post_v1"]
