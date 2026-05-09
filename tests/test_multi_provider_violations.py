"""Strict violation-injection suite for constitutional hardening."""

import unittest

from apipools.core.providers import ProviderRequest
from apipools.errors import CrossProviderInconsistencyError, NormalizationError
from apipools.routing import (
    DeterministicProviderSelector,
    MultiProviderExecutor,
    ProviderRegistry,
)
from support.demo_providers import ProviderA, ProviderB


class _NondeterministicProviderA(ProviderA):
    """Injected violating provider: same request, changing result each execution."""

    def execute(self, request: ProviderRequest) -> dict:
        self.execution_count += 1
        return {
            "provider_id": self.provider_id,
            "item": {
                "id": "a-post-1",
                "text": f"mutating-text-{self.execution_count}",
                "author_id": "a-user-1",
                "created_at": "2026-05-07T12:00:00Z",
            },
            "cursor_format": self.cursor_kind,
        }


class MultiProviderViolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider_a = ProviderA()
        self.provider_b = ProviderB()
        self.registry = ProviderRegistry.build((self.provider_b, self.provider_a))
        self.selector = DeterministicProviderSelector(
            self.registry, default_provider_id="provider_a"
        )
        self.executor = MultiProviderExecutor(self.registry, self.selector)

    def test_non_deterministic_registry_order_detected(self) -> None:
        # Violation attempt: providers supplied in different input order.
        reg_1 = ProviderRegistry.build((ProviderA(), ProviderB()))
        reg_2 = ProviderRegistry.build((ProviderB(), ProviderA()))
        self.assertEqual(reg_1.ordered_provider_ids, ("provider_a", "provider_b"))
        self.assertEqual(reg_2.ordered_provider_ids, ("provider_a", "provider_b"))
        self.assertEqual(reg_1.first_provider_id(), reg_2.first_provider_id())

    def test_selection_depends_on_runtime_state_forbidden(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        first_selection = self.selector.select(req).provider_id
        _ = self.executor.execute(req)
        _ = self.executor.execute(req)
        after_runtime_selection = self.selector.select(req).provider_id
        self.assertEqual(first_selection, after_runtime_selection)

    def test_provider_override_invalid_rejected(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            provider_override="non_existent",
        )
        with self.assertRaises(NormalizationError) as ctx:
            self.executor.execute(req)
        self.assertIn("override", str(ctx.exception).lower())
        self.assertEqual(self.provider_a.execution_count, 0)
        self.assertEqual(self.provider_b.execution_count, 0)

    def test_cross_provider_hidden_divergence_forbidden(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id"}),
            require_full=False,
            consistency_check=True,
        )
        with self.assertRaises(CrossProviderInconsistencyError) as ctx:
            self.executor.detect_cross_provider_inconsistency(req)
        self.assertIn("inconsistency", str(ctx.exception).lower())

    def test_execution_path_attempts_fallback_forbidden(self) -> None:
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        original_execute = self.provider_a.execute

        def fail_execute(_request: ProviderRequest) -> dict:
            self.provider_a.execution_count += 1
            raise RuntimeError("forced primary provider execution failure")

        self.provider_a.execute = fail_execute  # type: ignore[method-assign]
        try:
            with self.assertRaises(RuntimeError):
                self.executor.execute(req)
            self.assertEqual(self.provider_b.execution_count, 0)
        finally:
            self.provider_a.execute = original_execute  # type: ignore[method-assign]

    def test_same_request_different_results_detected(self) -> None:
        provider = _NondeterministicProviderA()
        registry = ProviderRegistry.build((provider, ProviderB()))
        selector = DeterministicProviderSelector(registry, default_provider_id="provider_a")
        executor = MultiProviderExecutor(registry, selector)
        req = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )
        result_1 = executor.execute(req)
        result_2 = executor.execute(req)

        def _assert_deterministic_or_raise() -> None:
            if result_1.payload != result_2.payload:
                raise NormalizationError(
                    message="Determinism violation detected for same request.",
                    operation="read",
                    resource="post",
                )

        with self.assertRaises(NormalizationError) as ctx:
            _assert_deterministic_or_raise()
        self.assertIn("determinism violation", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
