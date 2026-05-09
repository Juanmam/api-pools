"""Violation injection against constitutional cursor semantics."""

import base64
import secrets
import unittest
from unittest.mock import patch

from apipools.errors import ExpiredCursorError, InvalidCursorError, TamperedCursorError
from apipools.pagination.encoder import CursorEncoder, store_key
from apipools.pagination.signer import CursorSigner
from apipools.pagination.store import MemoryCursorStore
from apipools.pagination.token import CursorToken
from support.constants import DEFAULT_VALIDATION_CURSOR_SECRET
from support.mocks import MockInstagramAPI
from support.strategy import SocialAPIStrategy


class RandomWireEncoder(CursorEncoder):
    """Test double: nondeterministic wire breaks PG-3 (second issue must fail)."""

    def __init__(self, signer: CursorSigner, store: MemoryCursorStore, secret: bytes) -> None:
        super().__init__(signer, store, secret, max_encoder_state_keys=32)

    def encode(self, token: CursorToken) -> str:  # type: ignore[override]
        key = store_key(self._secret, token)
        self._store.put(key, token)
        envelope = f"v1|{key}".encode("ascii")
        sig = self._signer.sign(envelope)
        nonce = secrets.token_hex(4)
        wire = f"v1|{key}|{sig}|{nonce}".encode("ascii")
        opaque = base64.urlsafe_b64encode(wire).decode("ascii").rstrip("=")
        prior = self._determinism_by_key.get(key)
        if prior is not None and prior != opaque:
            raise InvalidCursorError(
                message="Determinism violation detected: same logical cursor encodes differently.",
                operation=token.operation,
                resource=token.resource,
                detail="nondeterministic_cursor_encoding",
            )
        self._determinism_by_key[key] = opaque
        return opaque


class CursorViolationTests(unittest.TestCase):
    def test_forged_cursor_rejected(self) -> None:
        key = "cc" * 32
        sig = "dd" * 32
        bogus = (
            base64.urlsafe_b64encode(f"v1|{key}|{sig}".encode("ascii")).decode("ascii").rstrip("=")
        )
        strategy = SocialAPIStrategy(provider=MockInstagramAPI())
        with self.assertRaises(TamperedCursorError):
            strategy.list_posts(projection={"text", "author_id", "created_at"}, cursor=bogus)

    def test_cursor_reuse_after_expiration_forbidden(self) -> None:
        with patch("time.monotonic", return_value=0.0):
            strategy = SocialAPIStrategy(
                MockInstagramAPI(),
                cursor_ttl_seconds=60.0,
                cursor_max_store_entries=64,
            )
            page = strategy.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
            cur = page.next_cursor
        self.assertIsNotNone(cur)
        with patch("time.monotonic", return_value=9999.0):
            with self.assertRaises(ExpiredCursorError):
                strategy.list_posts(projection={"text", "author_id", "created_at"}, cursor=cur)

    def test_cursor_modification_breaks_integrity(self) -> None:
        strategy = SocialAPIStrategy(MockInstagramAPI())
        page = strategy.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
        cur = page.next_cursor
        self.assertIsNotNone(cur)
        padded = cur + "=" * (-len(cur) % 4)
        wire = base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")
        parts = wire.split("|")
        key = parts[1]
        parts[1] = key[:-4] + ("dead" if key[-4:] != "dead" else "beef")
        broken = (
            base64.urlsafe_b64encode("|".join(parts).encode("ascii")).decode("ascii").rstrip("=")
        )
        with self.assertRaises((TamperedCursorError, ExpiredCursorError, InvalidCursorError)):
            strategy.list_posts(projection={"text", "author_id", "created_at"}, cursor=broken)

    def test_non_deterministic_cursor_generation_forbidden(self) -> None:
        store = MemoryCursorStore(max_entries=32, ttl_seconds=60.0)
        signer = CursorSigner(DEFAULT_VALIDATION_CURSOR_SECRET)
        enc = RandomWireEncoder(signer, store, DEFAULT_VALIDATION_CURSOR_SECRET)
        token = CursorToken(
            provider_id="mock_instagram",
            operation="list",
            resource="post",
            provider_cursor="pc-1",
            issued_at_ns=42,
        )
        enc.encode(token)
        with self.assertRaises(InvalidCursorError) as ctx:
            enc.encode(token)
        self.assertIn("Determinism", ctx.exception.message)


if __name__ == "__main__":
    unittest.main()
