"""Pure normalizers for TikTok Open API v2 shaped wire dicts (video-as-post)."""

from __future__ import annotations

from apipools.canonical import CanonicalPost, FieldStatus, SemanticField
from apipools.errors import NormalizationError
from apipools.versioning import assert_supported_projection_version

_SUPPORTED_V1 = frozenset({"v1"})


def normalize_tiktok_video_post_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalPost, str | None]:
    """Map a TikTok ``video``-as-post projection (canonical v1)."""
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="post")
    if wire.get("_provider") != "tiktok_open_v2_video":
        raise NormalizationError(
            message="Wrong wire kind for TikTok video post normalizer.",
            operation="read",
            resource="post",
            detail=f"provider={wire.get('_provider')!r}",
        )
    vid = str(wire.get("id") or "")
    if not vid:
        raise NormalizationError(
            message="TikTok wire missing video id.",
            operation="read",
            resource="post",
            detail="missing_id",
        )

    title = wire.get("title") or ""
    desc = wire.get("video_description") or ""
    combined = (
        str(title).strip() + ("\n\n" + str(desc).strip() if str(desc).strip() else "")
    ).strip()

    gap_parts = [
        "tiktok.video_as_post.mapping; text merges title + video_description",
        "tiktok.only_public_videos_for_authorized_user_via_video.list",
        "tiktok.author_is_open_id_projection_not_channel_handle",
    ]

    max_len = 2800
    if len(combined) > max_len:
        gap_parts.append(f"text_truncated={len(combined)}->{max_len}")
        combined = combined[:max_len]

    creator_open_id = wire.get("creator_open_id")
    create_time = wire.get("create_time")

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
            "author_id",
            None if creator_open_id is None else str(creator_open_id),
        ),
        created_at=field(
            "created_at", None if create_time is None else str(create_time)
        ),
    )
    return post, "; ".join(gap_parts)


__all__ = ["normalize_tiktok_video_post_v1"]
