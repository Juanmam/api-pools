"""Bounded cursor store with explicit TTL and FIFO eviction."""

import time
from collections import OrderedDict
from dataclasses import dataclass

from ..errors import ExpiredCursorError
from .token import CursorToken


@dataclass
class _Entry:
    token: CursorToken
    expires_at_monotonic: float


class MemoryCursorStore:
    """In-process FIFO-bounded TTL store for issued cursor keys."""

    __slots__ = ("_max_entries", "_ttl_seconds", "_data")

    def __init__(self, *, max_entries: int, ttl_seconds: float) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._data: OrderedDict[str, _Entry] = OrderedDict()

    def put(self, key: str, token: CursorToken) -> None:
        now = time.monotonic()
        self._evict_expired(now)
        while len(self._data) >= self._max_entries:
            self._data.popitem(last=False)
        self._data[key] = _Entry(token=token, expires_at_monotonic=now + self._ttl_seconds)

    def get(self, key: str, *, operation: str, resource: str) -> CursorToken:
        now = time.monotonic()
        self._evict_expired(now)
        entry = self._data.get(key)
        if entry is None:
            raise ExpiredCursorError(
                message="Cursor is unknown or was evicted from the bounded store.",
                operation=operation,
                resource=resource,
                detail="store_miss_or_evicted",
            )
        if now > entry.expires_at_monotonic:
            del self._data[key]
            raise ExpiredCursorError(
                message="Cursor TTL expired.",
                operation=entry.token.operation,
                resource=entry.token.resource,
                detail="explicit_ttl_expired",
            )
        return entry.token

    def __len__(self) -> int:
        return len(self._data)

    def clear(self) -> None:
        self._data.clear()

    def _evict_expired(self, now: float) -> None:
        expired_keys = [k for k, e in self._data.items() if now > e.expires_at_monotonic]
        for k in expired_keys:
            del self._data[k]


# Validation-era name; prefer ``MemoryCursorStore`` in new code.
CursorStore = MemoryCursorStore
