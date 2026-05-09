"""RedisCursorStore with a minimal in-memory stand-in (no redis daemon)."""

import time
import unittest

from apipools.errors import ExpiredCursorError
from apipools.pagination import CursorEncoder, CursorSigner, CursorToken
from apipools.pagination.redis_store import RedisCursorStore
from apipools.pagination.store import MemoryCursorStore
from support.constants import DEFAULT_VALIDATION_CURSOR_SECRET


class _FakeRedis:
    def __init__(self) -> None:
        self.kv: dict[str, str] = {}

    def setex(self, key: str, _ttl: int, value: str) -> None:
        self.kv[key] = value

    def get(self, key: str) -> str | None:
        return self.kv.get(key)


class RedisCursorStoreTests(unittest.TestCase):
    def test_put_get_roundtrip(self) -> None:
        fake = _FakeRedis()
        store = RedisCursorStore(fake, ttl_seconds=3600.0)
        token = CursorToken(
            provider_id="binding-1",
            operation="list",
            resource="post",
            provider_cursor="pc-9",
            issued_at_ns=time.time_ns(),
        )
        store.put("k1", token)
        out = store.get("k1", operation="list", resource="post")
        self.assertEqual(out.provider_cursor, "pc-9")

    def test_miss_raises_expired_semantics(self) -> None:
        store = RedisCursorStore(_FakeRedis(), ttl_seconds=60.0)
        with self.assertRaises(ExpiredCursorError):
            store.get("missing", operation="list", resource="post")

    def test_encoder_uses_redis_store(self) -> None:
        signer = CursorSigner(DEFAULT_VALIDATION_CURSOR_SECRET)
        storage = RedisCursorStore(_FakeRedis(), ttl_seconds=3600.0)
        enc = CursorEncoder(
            signer,
            storage,
            DEFAULT_VALIDATION_CURSOR_SECRET,
            max_encoder_state_keys=32,
        )
        token = CursorToken(
            provider_id="b",
            operation="list",
            resource="post",
            provider_cursor="x",
            issued_at_ns=1,
        )
        opaque = enc.encode(token)
        out = enc.decode(opaque, operation="list", resource="post")
        self.assertEqual(out.provider_cursor, "x")

    def test_memory_cursor_store_still_default(self) -> None:
        ms = MemoryCursorStore(max_entries=4, ttl_seconds=10.0)
        self.assertEqual(len(ms), 0)
