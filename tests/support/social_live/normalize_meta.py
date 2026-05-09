"""Pure normalizers for internal Facebook / Instagram Graph wire dicts."""

from __future__ import annotations

from apipools.canonical import CanonicalComment, CanonicalPost, FieldStatus, SemanticField
from apipools.errors import NormalizationError
from apipools.versioning import assert_supported_projection_version

_SUPPORTED_V1 = frozenset({"v1"})


def normalize_facebook_graph_post_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalPost, str | None]:
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="post")
    if wire.get("_provider") != "facebook_graph":
        raise NormalizationError(
            message="Wrong wire kind for Facebook Graph post normalizer.",
            operation="read",
            resource="post",
            detail=f"provider={wire.get('_provider')!r}",
        )
    post_id = str(wire.get("id") or "")
    author_id_raw = wire.get("author_id")
    created_raw = wire.get("created_time")
    message_raw = wire.get("message")

    if not post_id:
        raise NormalizationError(
            message="Facebook post wire missing id.",
            operation="read",
            resource="post",
            detail="missing_id",
        )

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    gap: str | None = None
    post = CanonicalPost(
        id=post_id,
        text=field("text", None if message_raw is None else str(message_raw)),
        author_id=field(
            "author_id", None if author_id_raw is None else str(author_id_raw)
        ),
        created_at=field(
            "created_at", None if created_raw is None else str(created_raw)
        ),
    )
    return post, gap


def normalize_facebook_graph_comment_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalComment, str | None]:
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="comment")
    if wire.get("_provider") != "facebook_graph_comment":
        raise NormalizationError(
            message="Wrong wire kind for Facebook Graph comment normalizer.",
            operation="read",
            resource="comment",
            detail=f"provider={wire.get('_provider')!r}",
        )
    cid = str(wire.get("id") or "")
    post_id = str(wire.get("post_id") or "")
    if not cid:
        raise NormalizationError(
            message="Facebook comment wire missing id.",
            operation="read",
            resource="comment",
            detail="missing_id",
        )
    if not post_id:
        raise NormalizationError(
            message="Facebook comment wire missing parent post id.",
            operation="read",
            resource="comment",
            detail="missing_post_id",
        )

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    msg_raw = wire.get("message")
    gap: str | None = None

    comment = CanonicalComment(
        id=cid,
        post_id=post_id,
        text=field("text", None if msg_raw is None else str(msg_raw)),
        author_id=field(
            "author_id",
            None if wire.get("author_id") is None else str(wire["author_id"]),
        ),
        created_at=field(
            "created_at",
            None if wire.get("created_time") is None else str(wire["created_time"]),
        ),
    )
    return comment, gap


def normalize_instagram_graph_post_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalPost, str | None]:
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="post")
    if wire.get("_provider") != "instagram_graph":
        raise NormalizationError(
            message="Wrong wire kind for Instagram Graph post normalizer.",
            operation="read",
            resource="post",
            detail=f"provider={wire.get('_provider')!r}",
        )
    post_id = str(wire.get("id") or "")
    if not post_id:
        raise NormalizationError(
            message="Instagram media wire missing id.",
            operation="read",
            resource="post",
            detail="missing_id",
        )

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    caption = wire.get("caption")
    gap = (
        "instagram.graph.caption_truncation_policy_not_modeled_in_v1"
        if caption is not None and projection & {"text"}
        else None
    )

    post = CanonicalPost(
        id=post_id,
        text=field("text", None if caption is None else str(caption)),
        author_id=field(
            "author_id",
            None if wire.get("author_id") is None else str(wire["author_id"]),
        ),
        created_at=field(
            "created_at",
            None if wire.get("timestamp") is None else str(wire["timestamp"]),
        ),
    )
    return post, gap


def normalize_instagram_graph_comment_v1(
    wire: dict, projection: set[str], version: str
) -> tuple[CanonicalComment, str | None]:
    assert_supported_projection_version(version, _SUPPORTED_V1, operation="read", resource="comment")
    if wire.get("_provider") != "instagram_graph_comment":
        raise NormalizationError(
            message="Wrong wire kind for Instagram Graph comment normalizer.",
            operation="read",
            resource="comment",
            detail=f"provider={wire.get('_provider')!r}",
        )
    cid = str(wire.get("id") or "")
    media_id = str(wire.get("media_id") or "")
    if not cid or not media_id:
        raise NormalizationError(
            message="Instagram comment wire incomplete.",
            operation="read",
            resource="comment",
            detail="missing_id_or_media",
        )

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    text_raw = wire.get("text")
    author_fallback = wire.get("author_id")
    if author_fallback is None and wire.get("username") is not None:
        author_fallback = wire.get("username")

    gap: str | None = None
    if wire.get("author_id") is None and wire.get("username") is not None:
        gap = "instagram.comment.author_used_username_fallback_for_author_id"

    comment = CanonicalComment(
        id=cid,
        post_id=media_id,
        text=field("text", None if text_raw is None else str(text_raw)),
        author_id=field(
            "author_id",
            None if author_fallback is None else str(author_fallback),
        ),
        created_at=field(
            "created_at",
            None if wire.get("timestamp") is None else str(wire["timestamp"]),
        ),
    )
    return comment, gap


__all__ = [
    "normalize_facebook_graph_comment_v1",
    "normalize_facebook_graph_post_v1",
    "normalize_instagram_graph_comment_v1",
    "normalize_instagram_graph_post_v1",
]
