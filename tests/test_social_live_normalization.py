"""Fixture-driven tests for ``tests/support/social_live`` pure normalizers (no network)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apipools.canonical import FieldStatus
from apipools.errors import UnsupportedCapabilityError
from support.social_live.normalize_meta import (
    normalize_facebook_graph_comment_v1,
    normalize_facebook_graph_post_v1,
    normalize_instagram_graph_comment_v1,
    normalize_instagram_graph_post_v1,
)
from support.social_live.normalize_tiktok import normalize_tiktok_video_post_v1
from support.social_live.normalize_youtube import (
    normalize_youtube_comment_v1,
    normalize_youtube_video_post_v1,
)
from support.social_live.oauth import StaticAccessToken
from support.social_live.tiktok import TikTokOpenBinding
from support.strategy import SocialAPIStrategy

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "social"


def _load_json(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_normalize_facebook_post() -> None:
    wire = _load_json("facebook_graph_post.json")
    post, gap = normalize_facebook_graph_post_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert post.id == wire["id"]
    assert gap is None
    assert post.text.status is FieldStatus.VALUE
    assert post.text.value == "Hello from fixture"


def test_normalize_facebook_comment() -> None:
    wire = _load_json("facebook_graph_comment.json")
    c, gap = normalize_facebook_graph_comment_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert c.post_id == "fb_post_1"
    assert gap is None


def test_normalize_instagram_media() -> None:
    wire = _load_json("instagram_graph_media.json")
    post, gap = normalize_instagram_graph_post_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert post.id == wire["id"]
    assert gap is not None and "instagram" in gap.lower()


def test_normalize_instagram_comment() -> None:
    wire = _load_json("instagram_graph_comment.json")
    c, gap = normalize_instagram_graph_comment_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert c.id == wire["id"]
    assert gap is None


def test_normalize_youtube_video_as_post() -> None:
    wire = _load_json("youtube_video.json")
    post, gap = normalize_youtube_video_post_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert post.id == "abc123XYZ"
    assert gap and "youtube.video_as_post" in gap
    assert "Fixture title" in (post.text.value or "")


def test_normalize_youtube_comment() -> None:
    wire = _load_json("youtube_comment.json")
    c, gap = normalize_youtube_comment_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert c.post_id == "abc123XYZ"
    assert gap and "youtube.comments_list" in gap


def test_normalize_tiktok_video_as_post() -> None:
    wire = _load_json("tiktok_video.json")
    post, gap = normalize_tiktok_video_post_v1(
        wire, {"text", "author_id", "created_at"}, "v1"
    )
    assert post.id == wire["id"]
    assert gap and "tiktok.video_as_post" in gap


def test_tiktok_binding_fetch_comment_not_supported() -> None:
    b = TikTokOpenBinding("fixture_open_id", StaticAccessToken("fixture_token"))
    with pytest.raises(UnsupportedCapabilityError):
        b.fetch_comment("any_id")


def test_strategy_rejects_comment_read_on_tiktok() -> None:
    strat = SocialAPIStrategy(
        provider=TikTokOpenBinding("_oid", StaticAccessToken("tok")),
    )
    with pytest.raises(UnsupportedCapabilityError):
        strat.read_comment("c", projection={"text"}, require_full=False, version="v1")
