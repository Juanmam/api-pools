"""Opt-in smoke tests hitting real APIs (credentials via env).

Run when enabled::

    set APIPOOLS_RUN_LIVE=1
    pytest tests/test_social_live_smoke.py -m live
"""

from __future__ import annotations

import os

import pytest

from support.social_live import StaticAccessToken, YouTubeDataBinding

pytestmark = pytest.mark.live


@pytest.mark.skipif(
    os.getenv("APIPOOLS_RUN_LIVE") != "1",
    reason="Set APIPOOLS_RUN_LIVE=1 (see .env.example and quickstart).",
)
@pytest.mark.skipif(
    not os.getenv("APIPOOLS_YOUTUBE_ACCESS_TOKEN"),
    reason="Missing APIPOOLS_YOUTUBE_ACCESS_TOKEN.",
)
@pytest.mark.skipif(
    not os.getenv("APIPOOLS_YOUTUBE_CHANNEL_ID"),
    reason="Missing APIPOOLS_YOUTUBE_CHANNEL_ID.",
)
def test_youtube_list_posts_smoke_one() -> None:
    chan = os.environ["APIPOOLS_YOUTUBE_CHANNEL_ID"]
    token = os.environ["APIPOOLS_YOUTUBE_ACCESS_TOKEN"]
    b = YouTubeDataBinding(channel_id=chan, token_source=StaticAccessToken(token))
    out = b.list_posts(provider_cursor=None, limit=1)
    assert isinstance(out["items"], list)
    assert "more_available" in out
