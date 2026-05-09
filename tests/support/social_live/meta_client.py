"""Shared Meta Graph API GET helper."""

from __future__ import annotations

from typing import Any

from support.social_live.oauth import AccessTokenSource

from .deps import require_social_live
from .http import GraphHttpTransport


class MetaGraphClient:
    """Minimal Graph GET client (Facebook + Instagram use the same host)."""

    def __init__(
        self,
        token_source: AccessTokenSource,
        *,
        graph_version: str = "v21.0",
        transport: GraphHttpTransport | None = None,
    ) -> None:
        require_social_live()
        self._token_source = token_source
        self.graph_version = graph_version
        self._own_transport = transport is None
        self.transport = transport or GraphHttpTransport()

    def close(self) -> None:
        if self._own_transport:
            self.transport.close()

    def __enter__(self) -> MetaGraphClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def get_object(self, object_path: str, **params: Any) -> dict[str, Any]:
        """GET ``/{graph_version}/{object_path}`` with access_token injected."""
        path = object_path.lstrip("/")
        url = f"https://graph.facebook.com/{self.graph_version}/{path}"
        qp: dict[str, Any] = dict(params)
        qp["access_token"] = self._token_source()
        return self.transport.request_json("GET", url, params=qp)


__all__ = ["MetaGraphClient"]
