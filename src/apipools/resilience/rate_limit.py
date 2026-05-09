"""Strict rate-limit observables and pressure policy inputs."""

from dataclasses import dataclass

from ..execution.errors import RateLimitExceededError

__all__ = ["RateLimitState", "RateLimitExceededError"]


@dataclass(frozen=True)
class RateLimitState:
    """Observed provider pressure state."""

    provider_id: str
    reason: str = "rate_limit_exceeded"
    retry_after_seconds: int | None = None
