"""Strict policy: surface pressure, never retry or fallback."""

from dataclasses import dataclass

from ..core.providers.base import ProviderRequest
from .rate_limit import RateLimitExceededError, RateLimitState


@dataclass(frozen=True)
class RateLimitPolicy:
    """Constitutional policy for pressure behavior."""

    mode: str = "STRICT"

    def enforce(self, state: RateLimitState, request: ProviderRequest) -> None:
        if self.mode != "STRICT":
            raise ValueError("Only STRICT rate-limit policy is supported.")
        raise RateLimitExceededError(
            message="Provider execution blocked by strict pressure policy.",
            operation=request.operation,
            resource=request.resource,
            detail=(
                f"provider_id={state.provider_id}; reason={state.reason}; "
                f"retry_after={state.retry_after_seconds}"
            ),
        )
