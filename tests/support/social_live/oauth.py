"""Token sources and minimal OAuth exchange helpers (Meta / Google token endpoint patterns)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .deps import require_social_live


@runtime_checkable
class AccessTokenSource(Protocol):
    """Returns a valid bearer or query-style access token string for the target API."""

    def __call__(self) -> str: ...


@dataclass(frozen=True)
class StaticAccessToken:
    """Fixed token (long-lived user token, service token, etc.)."""

    token: str

    def __call__(self) -> str:
        return self.token


def exchange_meta_long_lived_token(
    *,
    app_id: str,
    app_secret: str,
    short_lived_user_token: str,
    graph_version: str = "v21.0",
) -> dict[str, Any]:
    """
    Exchange a short-lived user token for a long-lived user token (Meta Graph).

    https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived
    """
    require_social_live()
    from .http import GraphHttpTransport

    url = f"https://graph.facebook.com/{graph_version}/oauth/access_token"
    params: dict[str, Any] = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_user_token,
    }
    with GraphHttpTransport() as t:
        return t.request_json("GET", url, params=params)


def meta_authorize_url(
    *,
    app_id: str,
    redirect_uri: str,
    scopes: tuple[str, ...],
    state: str,
    graph_version: str = "v21.0",
) -> str:
    """Build Facebook Login dialog URL (user must open in browser)."""
    from urllib.parse import urlencode

    base = f"https://www.facebook.com/{graph_version}/dialog/oauth"
    q = urlencode(
        {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": ",".join(scopes),
            "response_type": "code",
        }
    )
    return f"{base}?{q}"


def exchange_meta_code_for_token(
    *,
    app_id: str,
    app_secret: str,
    redirect_uri: str,
    code: str,
    graph_version: str = "v21.0",
) -> dict[str, Any]:
    """Exchange authorization code for short-lived user access token."""
    require_social_live()
    from .http import GraphHttpTransport

    url = f"https://graph.facebook.com/{graph_version}/oauth/access_token"
    params: dict[str, Any] = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "client_secret": app_secret,
        "code": code,
    }
    with GraphHttpTransport() as t:
        return t.request_json("GET", url, params=params)


def google_token_refresh(
    *,
    client_id: str,
    client_secret: str,
    refresh_token: str,
) -> dict[str, Any]:
    """
    Refresh a Google OAuth2 access token (YouTube Data API).

    Caller stores refresh tokens securely; this only performs the HTTPS exchange.
    """
    require_social_live()
    from .http import GraphHttpTransport

    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    with GraphHttpTransport() as t:
        return t.request_json(
            "POST",
            "https://oauth2.googleapis.com/token",
            data_form=body,
        )


__all__ = [
    "AccessTokenSource",
    "StaticAccessToken",
    "exchange_meta_long_lived_token",
    "exchange_meta_code_for_token",
    "meta_authorize_url",
    "google_token_refresh",
]
