"""Deterministic Instagram-shaped normalizers for mock-backed tests."""

from __future__ import annotations

from apipools.canonical import CanonicalComment, CanonicalPost, FieldStatus, SemanticField
from apipools.errors import NormalizationError
from apipools.versioning import assert_supported_projection_version

from .constants import SUPPORTED_MOCK_PROJECTION_V1


def _assert_version(version: str, operation: str, resource: str) -> None:
    assert_supported_projection_version(
        version, SUPPORTED_MOCK_PROJECTION_V1, operation=operation, resource=resource
    )


def normalize_post_v1(wire: dict, projection: set[str], version: str) -> tuple[CanonicalPost, str | None]:
    _assert_version(version, "read", "post")
    try:
        post_id = wire["pk"]
        owner_id = wire["owner"]["id"]
        created_at = wire["taken_at_iso"]
    except KeyError as exc:
        raise NormalizationError(
            message="Unmappable provider payload for post.",
            operation="read",
            resource="post",
            detail=f"missing_key={exc}",
        ) from exc

    def field(name: str, value: str | None) -> SemanticField[str]:
        if name not in projection:
            return SemanticField(status=FieldStatus.UNREQUESTED)
        if value is None:
            return SemanticField(status=FieldStatus.MISSING)
        return SemanticField(status=FieldStatus.VALUE, value=value)

    post = CanonicalPost(
        id=post_id,
        text=field("text", wire.get("caption")),
        author_id=field("author_id", owner_id),
        created_at=field("created_at", created_at),
    )
    return post, None


def normalize_comment_v1(wire: dict, projection: set[str], version: str) -> tuple[CanonicalComment, str | None]:
    _assert_version(version, "read", "comment")
    try:
        comment_id = wire["pk"]
        post_id = wire["media_pk"]
        owner_id = wire["owner"]["id"]
        created_at = wire["taken_at_iso"]
    except KeyError as exc:
        raise NormalizationError(
            message="Unmappable provider payload for comment.",
            operation="read",
            resource="comment",
            detail=f"missing_key={exc}",
        ) from exc

    if not post_id:
        raise NormalizationError(
            message="Comment relationship invariant violated.",
            operation="read",
            resource="comment",
            detail="comment must belong to a post",
        )

    gap: str | None = None
    if "text" in projection:
        text_field = SemanticField[str](status=FieldStatus.UNSUPPORTED)
        gap = "comment.text unsupported by provider capability"
    else:
        text_field = SemanticField[str](status=FieldStatus.UNREQUESTED)

    comment = CanonicalComment(
        id=comment_id,
        post_id=post_id,
        text=text_field,
        author_id=(
            SemanticField(status=FieldStatus.VALUE, value=owner_id)
            if "author_id" in projection
            else SemanticField(status=FieldStatus.UNREQUESTED)
        ),
        created_at=(
            SemanticField(status=FieldStatus.VALUE, value=created_at)
            if "created_at" in projection
            else SemanticField(status=FieldStatus.UNREQUESTED)
        ),
    )
    return comment, gap
