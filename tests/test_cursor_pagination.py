"""Constitutional pagination: opacity, lifecycle, bounded store, replay."""

import base64
import unittest
from unittest.mock import patch

from apipools.errors import ExpiredCursorError, TamperedCursorError
from support.mocks import MockInstagramAPI
from support.strategy import SocialAPIStrategy


class CursorPaginationTests(unittest.TestCase):
    def test_cursor_opacity(self) -> None:
        strategy = SocialAPIStrategy(provider=MockInstagramAPI())
        page = strategy.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
        self.assertIsNotNone(page.next_cursor)
        opaque = page.next_cursor
        self.assertIsInstance(opaque, str)
        self.assertNotIn("provider-page-2", opaque)
        self.assertNotIn("next_max_id", opaque)
        lowered = opaque.lower()
        self.assertFalse(
            any(piece in lowered for piece in ("p-", "instagram", "max_id")),
            "opaque client cursor must not embed obvious provider payloads",
        )

    def test_cursor_tampering_detected(self) -> None:
        strategy = SocialAPIStrategy(provider=MockInstagramAPI())
        page = strategy.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
        self.assertIsNotNone(page.next_cursor)
        cur = page.next_cursor
        padded = cur + "=" * (-len(cur) % 4)
        wire = base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")
        parts = wire.split("|")
        sig = parts[2]
        parts[2] = sig[:-1] + ("0" if sig[-1] != "0" else "1")
        mutated = (
            base64.urlsafe_b64encode("|".join(parts).encode("ascii")).decode("ascii").rstrip("=")
        )
        with self.assertRaises(TamperedCursorError):
            strategy.list_posts(
                projection={"text", "author_id", "created_at"},
                cursor=mutated,
            )

    def test_cursor_expiration_enforced(self) -> None:
        with patch("time.monotonic", return_value=0.0):
            strategy = SocialAPIStrategy(
                provider=MockInstagramAPI(),
                cursor_ttl_seconds=30.0,
                cursor_max_store_entries=128,
            )
            page = strategy.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
            cur = page.next_cursor
        self.assertIsNotNone(cur)
        with patch("time.monotonic", return_value=9999.0):
            with self.assertRaises(ExpiredCursorError):
                strategy.list_posts(
                    projection={"text", "author_id", "created_at"},
                    cursor=cur,
                )

    def test_cursor_replay_determinism(self) -> None:
        strategy = SocialAPIStrategy(provider=MockInstagramAPI())
        first = strategy.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
        cur = first.next_cursor
        self.assertIsNotNone(cur)
        again = strategy.list_posts(
            projection={"text", "author_id", "created_at"},
            cursor=cur,
            limit=2,
        )
        repeat = strategy.list_posts(
            projection={"text", "author_id", "created_at"},
            cursor=cur,
            limit=2,
        )
        self.assertEqual(again.items, repeat.items)
        self.assertEqual(again.has_more, repeat.has_more)
        self.assertEqual(again.next_cursor, repeat.next_cursor)

    def test_cursor_cross_instance_validity(self) -> None:
        p = MockInstagramAPI()
        one = SocialAPIStrategy(provider=p)
        page = one.list_posts(projection={"text", "author_id", "created_at"}, limit=2)
        cur = page.next_cursor
        self.assertIsNotNone(cur)
        two = SocialAPIStrategy(provider=p)
        with self.assertRaises(ExpiredCursorError):
            two.list_posts(
                projection={"text", "author_id", "created_at"},
                cursor=cur,
            )

    def test_cursor_store_bounded(self) -> None:
        strategy = SocialAPIStrategy(
            provider=MockInstagramAPI(),
            cursor_ttl_seconds=3600.0,
            cursor_max_store_entries=3,
        )
        opaques: list[str] = []
        for i in range(4):
            oc = strategy._pagination.issue(
                operation="list",
                resource="post",
                provider_cursor=f"synthetic-pc-{i}",
            )
            assert oc is not None
            opaques.append(oc)
        with self.assertRaises(ExpiredCursorError):
            strategy._pagination.resolve(opaques[0], operation="list", resource="post")


if __name__ == "__main__":
    unittest.main()
