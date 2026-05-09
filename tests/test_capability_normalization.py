"""Strict capability normalization validation tests."""

import unittest

from apipools.errors import CapabilityMismatchError
from apipools.normalization import (
    CanonicalField,
    CanonicalSchema,
    CapabilityNormalizer,
    mapping,
)


class CapabilityNormalizationTests(unittest.TestCase):
    def test_equivalent_fields_are_normalized(self) -> None:
        schema = CanonicalSchema(resource="post", fields=(CanonicalField("likes"),))
        provider_a = CapabilityNormalizer(schema=schema, mappings=mapping(("likes", "like_count")))
        provider_b = CapabilityNormalizer(schema=schema, mappings=mapping(("likes", "favorites")))

        out_a = provider_a.normalize({"like_count": 12}, {"likes"})
        out_b = provider_b.normalize({"favorites": 12}, {"likes"})

        self.assertEqual(out_a, {"likes": 12})
        self.assertEqual(out_b, {"likes": 12})

    def test_missing_field_raises_error(self) -> None:
        schema = CanonicalSchema(
            resource="post",
            fields=(CanonicalField("likes"), CanonicalField("comments")),
        )
        normalizer = CapabilityNormalizer(
            schema=schema,
            mappings=mapping(("likes", "like_count")),
        )
        with self.assertRaises(CapabilityMismatchError):
            normalizer.normalize({"like_count": 3}, {"likes", "comments"})

    def test_ambiguous_mapping_rejected(self) -> None:
        schema = CanonicalSchema(resource="post", fields=(CanonicalField("likes"),))
        normalizer = CapabilityNormalizer(
            schema=schema,
            mappings=(
                *mapping(("likes", "like_count")),
                *mapping(("likes", "favorites")),
            ),
        )
        with self.assertRaises(CapabilityMismatchError):
            normalizer.normalize({"like_count": 5, "favorites": 5}, {"likes"})

    def test_no_silent_field_dropping(self) -> None:
        schema = CanonicalSchema(
            resource="post",
            fields=(CanonicalField("likes"), CanonicalField("comments")),
        )
        normalizer = CapabilityNormalizer(
            schema=schema,
            mappings=mapping(("likes", "engagement.likes"), ("comments", "engagement.comments")),
        )
        with self.assertRaises(CapabilityMismatchError):
            normalizer.normalize({"engagement": {"likes": 8}}, {"likes", "comments"})

    def test_nested_field_mapping(self) -> None:
        schema = CanonicalSchema(
            resource="post",
            fields=(CanonicalField("author_name"),),
        )
        provider_a = CapabilityNormalizer(
            schema=schema,
            mappings=mapping(("author_name", "user.name")),
        )
        provider_b = CapabilityNormalizer(
            schema=schema,
            mappings=mapping(("author_name", "creator.username")),
        )

        out_a = provider_a.normalize({"user": {"name": "alice"}}, {"author_name"})
        out_b = provider_b.normalize({"creator": {"username": "alice"}}, {"author_name"})

        self.assertEqual(out_a, {"author_name": "alice"})
        self.assertEqual(out_b, {"author_name": "alice"})

    def test_provider_specific_shape_leak_forbidden(self) -> None:
        schema = CanonicalSchema(
            resource="post",
            fields=(CanonicalField("likes"),),
        )
        normalizer = CapabilityNormalizer(
            schema=schema,
            mappings=mapping(("likes", "like_count")),
        )
        provider_response = {"like_count": 9, "provider_debug": {"internal": True}}
        out = normalizer.normalize(provider_response, {"likes"})

        self.assertEqual(out, {"likes": 9})
        self.assertNotIn("provider_debug", out)


if __name__ == "__main__":
    unittest.main()
