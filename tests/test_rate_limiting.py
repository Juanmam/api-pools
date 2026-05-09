"""Strict rate-limit/backpressure constitutional tests."""

import unittest
from dataclasses import dataclass

from apipools.capabilities import CapabilityContract, CapabilityLevel
from apipools.core.providers import ProviderRegistry, ProviderRequest
from apipools.execution.errors import RateLimitExceededError
from apipools.resilience import RateLimitPolicy, StrictRateLimitExecutorWrapper
from apipools.routing import DeterministicProviderSelector, MultiProviderExecutor
from support.demo_providers import ProviderA


@dataclass
class RateLimitedProvider:
    provider_id: str = "provider_rl"
    cursor_kind: str = "cursor"
    execution_count: int = 0

    @staticmethod
    def capabilities() -> tuple[CapabilityContract, ...]:
        return (
            CapabilityContract(
                resource="post",
                operation="read",
                level=CapabilityLevel.FULL,
                supported_fields=frozenset({"id", "text", "author_id", "created_at"}),
                unsupported_fields=frozenset(),
            ),
        )

    def execute(self, request: ProviderRequest) -> dict:
        self.execution_count += 1
        raise RateLimitExceededError(
            message="Provider rate limit reached.",
            operation=request.operation,
            resource=request.resource,
            detail=f"provider_id={self.provider_id}; retry_after=60",
        )


class RateLimitingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rate_limited = RateLimitedProvider()
        self.provider_a = ProviderA()
        self.registry = ProviderRegistry.build((self.rate_limited, self.provider_a))
        self.selector = DeterministicProviderSelector(
            self.registry, default_provider_id="provider_rl"
        )
        self.executor = MultiProviderExecutor(self.registry, self.selector)
        self.wrapper = StrictRateLimitExecutorWrapper(
            executor=self.executor,
            policy=RateLimitPolicy(mode="STRICT"),
        )
        self.request = ProviderRequest(
            resource="post",
            operation="read",
            requested_fields=frozenset({"id", "text", "author_id", "created_at"}),
            require_full=True,
        )

    def test_rate_limit_exceeded_raises_error(self) -> None:
        with self.assertRaises(RateLimitExceededError):
            self.wrapper.execute(self.request)

    def test_no_retry_attempted(self) -> None:
        with self.assertRaises(RateLimitExceededError):
            self.wrapper.execute(self.request)
        self.assertEqual(self.rate_limited.execution_count, 1)

    def test_no_fallback_on_rate_limit(self) -> None:
        with self.assertRaises(RateLimitExceededError):
            self.wrapper.execute(self.request)
        self.assertEqual(self.provider_a.execution_count, 0)

    def test_same_request_same_failure(self) -> None:
        with self.assertRaises(RateLimitExceededError) as first:
            self.wrapper.execute(self.request)
        with self.assertRaises(RateLimitExceededError) as second:
            self.wrapper.execute(self.request)
        self.assertEqual(first.exception.message, second.exception.message)
        self.assertEqual(first.exception.operation, second.exception.operation)
        self.assertEqual(first.exception.resource, second.exception.resource)
        self.assertEqual(self.rate_limited.execution_count, 2)

    def test_rate_limit_does_not_mutate_selection(self) -> None:
        before = self.selector.select(self.request)
        with self.assertRaises(RateLimitExceededError):
            self.wrapper.execute(self.request)
        after = self.selector.select(self.request)
        self.assertEqual(before.provider_id, after.provider_id)
        self.assertEqual(before.reason, after.reason)


if __name__ == "__main__":
    unittest.main()
