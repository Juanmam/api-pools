"""OAuth + HTTP social bindings for tests only (requires ``pip install -e '.[dev]'``)."""

from __future__ import annotations

from typing import Any

__all__ = [
    "AccessTokenSource",
    "FacebookGraphBinding",
    "GraphHttpTransport",
    "InstagramGraphBinding",
    "MetaGraphClient",
    "StaticAccessToken",
    "TikTokOpenBinding",
    "YouTubeDataBinding",
    "exchange_meta_code_for_token",
    "exchange_meta_long_lived_token",
    "google_token_refresh",
    "meta_authorize_url",
]


def __getattr__(name: str) -> Any:
    if name == "GraphHttpTransport":
        from .http import GraphHttpTransport

        return GraphHttpTransport
    if name == "AccessTokenSource":
        from .oauth import AccessTokenSource

        return AccessTokenSource
    if name == "StaticAccessToken":
        from .oauth import StaticAccessToken

        return StaticAccessToken
    if name == "meta_authorize_url":
        from .oauth import meta_authorize_url

        return meta_authorize_url
    if name == "exchange_meta_code_for_token":
        from .oauth import exchange_meta_code_for_token

        return exchange_meta_code_for_token
    if name == "exchange_meta_long_lived_token":
        from .oauth import exchange_meta_long_lived_token

        return exchange_meta_long_lived_token
    if name == "google_token_refresh":
        from .oauth import google_token_refresh

        return google_token_refresh
    if name == "MetaGraphClient":
        from .meta_client import MetaGraphClient

        return MetaGraphClient
    if name == "FacebookGraphBinding":
        from .meta_facebook import FacebookGraphBinding

        return FacebookGraphBinding
    if name == "InstagramGraphBinding":
        from .meta_instagram import InstagramGraphBinding

        return InstagramGraphBinding
    if name == "YouTubeDataBinding":
        from .youtube import YouTubeDataBinding

        return YouTubeDataBinding
    if name == "TikTokOpenBinding":
        from .tiktok import TikTokOpenBinding

        return TikTokOpenBinding

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
