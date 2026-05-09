"""Constitution pressure tests with a second heterogeneous provider."""

import unittest

from apipools.canonical import CanonicalPost, FieldStatus
from apipools.errors import PartialCapabilityError, UnsupportedCapabilityError
from support.mocks import MockInstagramAPI
from support.strategy import SocialAPIStrategy
from support.twitter_mock import MockTwitterAPI


class SecondProviderPressureTests(unittest.TestCase):
    def test_capability_mismatch_fails_before_execution(self) -> None:
        provider = MockTwitterAPI()
        strategy = SocialAPIStrategy(provider=provider)
        before = provider.call_count
        with self.assertRaises(UnsupportedCapabilityError):
            strategy.read_comment(
                "c-1",
                projection={"text", "author_id", "created_at"},
                require_full=True,
            )
        self.assertEqual(before, provider.call_count)

    def test_partial_data_maps_to_explicit_field_status(self) -> None:
        strategy = SocialAPIStrategy(provider=MockTwitterAPI())
        post, gap = strategy.read_post(
            "t-missing-author",
            projection={"text", "author_id", "created_at"},
            require_full=False,
        )
        self.assertEqual(post.author_id.status, FieldStatus.UNKNOWN)
        self.assertIsNotNone(gap)
        self.assertIn("unknown_from_provider", gap)

    def test_cross_provider_same_intent_same_canonical_shape(self) -> None:
        instagram_strategy = SocialAPIStrategy(provider=MockInstagramAPI())
        twitter_strategy = SocialAPIStrategy(provider=MockTwitterAPI())

        projection = {"text", "author_id", "created_at"}
        insta_post, insta_gap = instagram_strategy.read_post(
            "p-1", projection=projection, require_full=True
        )
        twitter_post, twitter_gap = twitter_strategy.read_post(
            "t-1", projection=projection, require_full=False
        )

        self.assertIsInstance(insta_post, CanonicalPost)
        self.assertIsInstance(twitter_post, CanonicalPost)
        self.assertEqual(insta_post.text.status, FieldStatus.VALUE)
        self.assertEqual(twitter_post.text.status, FieldStatus.VALUE)
        self.assertIsNone(insta_gap)
        self.assertIsNotNone(twitter_gap)

    def test_second_provider_determinism(self) -> None:
        strategy = SocialAPIStrategy(provider=MockTwitterAPI())
        projection = {"text", "author_id", "created_at"}
        post_a, gap_a = strategy.read_post("t-1", projection=projection, require_full=False)
        post_b, gap_b = strategy.read_post("t-1", projection=projection, require_full=False)
        self.assertEqual(post_a, post_b)
        self.assertEqual(gap_a, gap_b)

    def test_second_provider_rejects_unsupported_rich_media_when_full_required(self) -> None:
        strategy = SocialAPIStrategy(provider=MockTwitterAPI())
        with self.assertRaises(PartialCapabilityError):
            strategy.read_post(
                "t-1",
                projection={"text", "author_id", "created_at", "rich_media_metadata"},
                require_full=True,
            )

    def test_full_required_rejects_partial_provider_before_execution(self) -> None:
        provider = MockTwitterAPI()
        strategy = SocialAPIStrategy(provider=provider)
        before = provider.call_count
        with self.assertRaises(PartialCapabilityError):
            strategy.read_post(
                "t-1",
                projection={"text", "author_id", "created_at"},
                require_full=True,
            )
        self.assertEqual(before, provider.call_count)

    def test_second_provider_pagination_gap_propagates(self) -> None:
        strategy = SocialAPIStrategy(provider=MockTwitterAPI())
        page = strategy.list_posts(
            projection={"text", "author_id", "created_at", "rich_media_metadata"},
            require_full=False,
            limit=2,
        )
        self.assertIsNotNone(page.gap)
        self.assertIn("unsupported_fields", page.gap)
        self.assertTrue(
            "truncated_by_provider_limit" in page.gap or "unknown_from_provider" in page.gap
        )


if __name__ == "__main__":
    unittest.main()
