"""Strict multi-provider pressure tests for constitutional enforcement."""

import unittest

from apipools.errors import CrossProviderInconsistencyError, PartialCapabilityError
from apipools.routing import (
    DeterministicProviderSelector,
    MultiProviderExecutor,
    ProviderRegistry,
    ProviderRequest,
)
from support.demo_providers import ProviderA, ProviderB


class MultiProviderPressureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider_a = ProviderA()
        self.provider_b = ProviderB()
        self.registry = ProviderRegistry.build((self.provider_b, self.provider_a))
        self.selector = DeterministicProviderSelector(
            self.registry, default_provider_id="provider_a"
        )
        self.executor = MultiProviderExecutor(self.registry, self.selector)

    def test_deterministic_provider_selection(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        first = self.selector.select(req)
        second = self.selector.select(req)
        self.assertEqual(first.provider_id, second.provider_id)
        self.assertEqual(first.reason, second.reason)

    def test_capability_mismatch_does_not_fallback(self) -> None:
        selector = DeterministicProviderSelector(self.registry, default_provider_id="provider_b")
        executor = MultiProviderExecutor(self.registry, selector)
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        before_a = self.provider_a.execution_count
        before_b = self.provider_b.execution_count
        with self.assertRaises(PartialCapabilityError):
            executor.execute(req)
        self.assertEqual(before_b, self.provider_b.execution_count)
        self.assertEqual(before_a, self.provider_a.execution_count)

    def test_no_implicit_provider_switch(self) -> None:
        selector = DeterministicProviderSelector(self.registry, default_provider_id="provider_b")
        executor = MultiProviderExecutor(self.registry, selector)
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        with self.assertRaises(PartialCapabilityError):
            executor.execute(req)
        self.assertEqual(self.provider_a.execution_count, 0)
        self.assertEqual(self.provider_b.execution_count, 0)

    def test_cross_provider_inconsistency_detected(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id"}),
            require_full=False,
            consistency_check=True,
        )
        with self.assertRaises(CrossProviderInconsistencyError):
            self.executor.detect_cross_provider_inconsistency(req)

    def test_explicit_provider_override_respected(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
            provider_override="provider_a",
        )
        result = self.executor.execute(req)
        self.assertEqual(result.provider_id, "provider_a")
        self.assertEqual(result.selection_reason, "explicit_override")
        self.assertEqual(self.provider_a.execution_count, 1)
        self.assertEqual(self.provider_b.execution_count, 0)

    def test_provider_registry_is_deterministic(self) -> None:
        ids = self.registry.ordered_provider_ids
        self.assertEqual(ids, ("provider_a", "provider_b"))
        self.assertEqual(self.registry.first_provider_id(), "provider_a")

    def test_same_request_same_result_across_runs(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        r1 = self.executor.execute(req)
        r2 = self.executor.execute(req)
        self.assertEqual(r1.provider_id, r2.provider_id)
        self.assertEqual(r1.selection_reason, r2.selection_reason)
        self.assertEqual(sorted(r1.payload["item"].keys()), sorted(r2.payload["item"].keys()))


if __name__ == "__main__":
    unittest.main()
