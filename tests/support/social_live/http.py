"""Sync httpx helper with Graph-style error handling and light retries."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlencode

import httpx

from apipools.errors import NormalizationError
from apipools.execution.errors import RateLimitExceededError, TransportTimeoutError


class GraphHttpTransport:
    """GET/POST JSON helper for vendor REST surfaces."""

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        max_retries_on_5xx: int = 2,
    ) -> None:
        self._client = httpx.Client(timeout=timeout)
        self._max_retries = max_retries_on_5xx

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GraphHttpTransport:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json_body: dict[str, Any] | None = None,
        data_form: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._client.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    json=json_body,
                    data=data_form,
                )
            except httpx.TimeoutException as exc:
                raise TransportTimeoutError(
                    message="HTTP request timed out.",
                    operation="transport",
                    resource="http",
                    detail=str(exc),
                ) from exc

            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                secs: int | None = None
                if retry_after is not None and retry_after.isdigit():
                    secs = int(retry_after)
                raise RateLimitExceededError(
                    message="Upstream rate limit.",
                    operation="transport",
                    resource="http",
                    detail=f"status=429; retry_after={secs}",
                )

            if resp.status_code >= 500 and attempt < self._max_retries:
                time.sleep(0.35 * (attempt + 1))
                continue

            if resp.headers.get("content-type", "").startswith("application/json"):
                data = resp.json()
            else:
                data = {}

            if resp.status_code >= 400:
                detail = _graph_error_detail(data) or resp.text[:500]
                raise NormalizationError(
                    message="Upstream rejected request or returned error payload.",
                    operation="transport",
                    resource="http",
                    detail=f"status={resp.status_code}; body={detail}",
                )

            if not isinstance(data, dict):
                raise NormalizationError(
                    message="Upstream returned non-object JSON.",
                    operation="transport",
                    resource="http",
                    detail=f"type={type(data).__name__}",
                )
            return data

        raise RuntimeError("Unreachable retry loop exhaustion")


def build_url(base: str, path: str, params: dict[str, Any]) -> str:
    """Join base + path and append query string."""
    path = path.lstrip("/")
    base = base.rstrip("/") + "/"
    q = urlencode({k: str(v) for k, v in params.items() if v is not None})
    return f"{base}{path}?{q}" if q else f"{base}{path}"


def _graph_error_detail(payload: dict[str, Any]) -> str | None:
    err = payload.get("error")
    if isinstance(err, dict):
        parts = [str(err.get("message", ""))]
        if "code" in err:
            parts.append(f"code={err['code']}")
        if "type" in err:
            parts.append(f"type={err['type']}")
        return "; ".join(p for p in parts if p)
    return None
