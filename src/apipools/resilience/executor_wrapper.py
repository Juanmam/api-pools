"""Execution wrapper that enforces strict no-retry/no-fallback pressure behavior."""

from dataclasses import dataclass

from ..core.execution import ExecutionResult, MultiProviderExecutor
from ..core.providers.base import ProviderRequest
from .policy import RateLimitPolicy
from .rate_limit import RateLimitExceededError, RateLimitState


@dataclass
class StrictRateLimitExecutorWrapper:
    """Wrap executor and guarantee explicit failure under pressure."""

    executor: MultiProviderExecutor
    policy: RateLimitPolicy

    def execute(self, request: ProviderRequest) -> ExecutionResult:
        # Selection occurs once and is never mutated on pressure errors.
        selection = self.executor.selector.select(request)
        try:
            return self.executor.execute(request)
        except RateLimitExceededError as exc:
            state = RateLimitState(provider_id=selection.provider_id, reason="rate_limit_exceeded")
            # Always raises; no retry, no queue, no provider switch.
            self.policy.enforce(state, request)
            raise exc
