"""Validation tests for the minimal architecture truth slice."""

import base64
import unittest

from apipools.canonical import FieldStatus
from apipools.errors import (
    InvalidCursorError,
    PartialCapabilityError,
    TamperedCursorError,
    VersionMismatchError,
)
from support.mocks import MockInstagramAPI
from support.strategy import SocialAPIStrategy


class ValidationSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = MockInstagramAPI()
        self.strategy = SocialAPIStrategy(provider=self.provider)

    def test_successful_post_retrieval_full_mapping(self) -> None:
        post, gap = self.strategy.read_post(
            "p-1",
            projection={"text", "author_id", "created_at"},
            require_full=True,
        )
        self.assertIsNone(gap)
        self.assertEqual(post.id, "p-1")
        self.assertEqual(post.text.status, FieldStatus.VALUE)
        self.assertEqual(post.author_id.status, FieldStatus.VALUE)
        self.assertEqual(post.created_at.status, FieldStatus.VALUE)

    def test_partial_comment_mapping_is_explicit(self) -> None:
        comment, gap = self.strategy.read_comment(
            "c-1",
            projection={"text", "author_id", "created_at"},
            require_full=False,
        )
        self.assertEqual(comment.id, "c-1")
        self.assertEqual(comment.post_id, "p-1")
        self.assertEqual(comment.text.status, FieldStatus.UNSUPPORTED)
        self.assertIsNotNone(gap)
        self.assertIn("unsupported_fields", gap)

    def test_capability_rejection_happens_before_execution(self) -> None:
        before = self.provider.call_count
        with self.assertRaises(PartialCapabilityError):
            self.strategy.read_comment(
                "c-1",
                projection={"text", "author_id", "created_at"},
                require_full=True,
            )
        after = self.provider.call_count
        self.assertEqual(before, after, "Provider must not be called on pre-validation failure")

    def test_pagination_uses_opaque_cursor(self) -> None:
        page1 = self.strategy.list_posts(
            projection={"text", "author_id", "created_at"},
            limit=2,
        )
        self.assertIsNone(page1.gap)
        self.assertTrue(page1.has_more)
        self.assertIsNotNone(page1.next_cursor)
        # Cursor must not leak provider's raw token.
        self.assertNotEqual(page1.next_cursor, "provider-page-2")
        self.assertNotIn("provider-page-2", page1.next_cursor)

        page2 = self.strategy.list_posts(
            projection={"text", "author_id", "created_at"},
            cursor=page1.next_cursor,
            limit=2,
        )
        self.assertFalse(page2.has_more)
        self.assertIsNone(page2.next_cursor)
        self.assertEqual(page2.items[0].id, "p-3")

    def test_no_silent_degradation(self) -> None:
        comment, gap = self.strategy.read_comment(
            "c-1",
            projection={"text", "author_id"},
            require_full=False,
        )
        self.assertEqual(comment.text.status, FieldStatus.UNSUPPORTED)
        self.assertIsNotNone(gap)
        self.assertNotEqual(comment.text.status, FieldStatus.VALUE)

    def test_normalization_is_deterministic(self) -> None:
        projection = {"text", "author_id", "created_at"}
        post_a, _ = self.strategy.read_post("p-1", projection=projection, require_full=True)
        post_b, _ = self.strategy.read_post("p-1", projection=projection, require_full=True)
        self.assertEqual(post_a, post_b)

    def test_version_mismatch_is_explicit(self) -> None:
        with self.assertRaises(VersionMismatchError):
            self.strategy.read_post(
                "p-1",
                projection={"text", "author_id", "created_at"},
                version="v2",
            )

    def test_missing_text_is_explicit_not_fabricated(self) -> None:
        original = self.provider.fetch_post

        def fetch_without_caption(_: str) -> dict:
            data = original("p-1")
            data.pop("caption", None)
            return data

        self.provider.fetch_post = fetch_without_caption
        post, _ = self.strategy.read_post(
            "p-1",
            projection={"text", "author_id", "created_at"},
        )
        self.assertEqual(post.text.status, FieldStatus.MISSING)

    def test_gap_propagates_for_read_post_when_degraded_allowed(self) -> None:
        post, gap = self.strategy.read_post(
            "p-1",
            projection={"text", "author_id", "created_at", "nonexistent"},
            require_full=False,
        )
        self.assertEqual(post.id, "p-1")
        self.assertIsNotNone(gap)
        self.assertIn("unsupported_fields", gap)

    def test_gap_propagates_for_list_posts_when_degraded_allowed(self) -> None:
        page = self.strategy.list_posts(
            projection={"text", "author_id", "created_at", "nonexistent"},
            require_full=False,
        )
        self.assertIsNotNone(page.gap)
        self.assertIn("unsupported_fields", page.gap)

    def test_invalid_cursor_raises_semantic_error(self) -> None:
        with self.assertRaises(InvalidCursorError):
            self.strategy.list_posts(
                projection={"text", "author_id", "created_at"},
                cursor="not-valid-base64$$$",
            )

    def test_tampered_cursor_raises_semantic_error(self) -> None:
        page = self.strategy.list_posts(
            projection={"text", "author_id", "created_at"},
            limit=2,
        )
        self.assertIsNotNone(page.next_cursor)
        cur = page.next_cursor
        padded = cur + "=" * (-len(cur) % 4)
        wire = base64.urlsafe_b64decode(padded.encode("ascii")).decode("ascii")
        parts = wire.split("|")
        self.assertEqual(len(parts), 3)
        sig = parts[2]
        parts[2] = sig[:-1] + ("0" if sig[-1] != "0" else "1")
        tampered_wire = "|".join(parts)
        tampered = (
            base64.urlsafe_b64encode(tampered_wire.encode("ascii")).decode("ascii").rstrip("=")
        )
        with self.assertRaises(TamperedCursorError):
            self.strategy.list_posts(
                projection={"text", "author_id", "created_at"},
                cursor=tampered,
            )


if __name__ == "__main__":
    unittest.main()
