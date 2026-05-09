"""Redis/Valkey-backed opaque cursor storage (optional ``apipools[redis]`` extra)."""

from __future__ import annotations

import json
from typing import Any

from ..errors import ExpiredCursorError
from .token import CursorToken


def _serialize(token: CursorToken) -> str:
    meta = [[k, v] for k, v in sorted(token.metadata)]
    payload = {
        "provider_id": token.provider_id,
        "operation": token.operation,
        "resource": token.resource,
        "provider_cursor": token.provider_cursor,
        "issued_at_ns": token.issued_at_ns,
        "metadata": meta,
    }
    return json.dumps(payload, separators=(",", ":"))


def _deserialize(raw: Any) -> CursorToken:
    obj = raw if isinstance(raw, dict) else json.loads(raw)
    meta_pairs = tuple((str(a), str(b)) for a, b in obj.get("metadata", []))
    return CursorToken(
        provider_id=str(obj["provider_id"]),
        operation=str(obj["operation"]),
        resource=str(obj["resource"]),
        provider_cursor=str(obj["provider_cursor"]),
        issued_at_ns=int(obj["issued_at_ns"]),
        metadata=meta_pairs,
    )


class RedisCursorStore:
    """
    Cursor backing using TTL keys on a Redis-compatible client (``setex`` / ``get``).

    Install ``apipools[redis]`` when you want the official ``redis`` PyPI client alongside
    ops playbooks; duck-typed mocks work without that dependency.
    """

    def __init__(
        self,
        client: Any,
        *,
        key_prefix: str = "apipools:cursor:",
        ttl_seconds: float,
    ) -> None:
        self._redis = client
        self._prefix = key_prefix
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = int(ttl_seconds)

    def put(self, key: str, token: CursorToken) -> None:
        redis_key = f"{self._prefix}{key}"
        self._redis.setex(redis_key, self._ttl, _serialize(token))

    def get(self, key: str, *, operation: str, resource: str) -> CursorToken:
        redis_key = f"{self._prefix}{key}"
        raw = self._redis.get(redis_key)
        if raw is None:
            raise ExpiredCursorError(
                message="Cursor is unknown or expired in Redis store.",
                operation=operation,
                resource=resource,
                detail="redis_miss_or_expired",
            )
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return _deserialize(raw)


__all__ = ["RedisCursorStore"]
