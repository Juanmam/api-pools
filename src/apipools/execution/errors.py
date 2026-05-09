"""Execution-plane failures (transport, quotas, timeouts) distinct from semantic interoperability."""

from dataclasses import dataclass


@dataclass
class ExecutionError(Exception):
    """Failures while carrying out work that are not canonical semantic mismatches."""

    message: str
    operation: str
    resource: str
    detail: str | None = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        suffix = f" detail={self.detail}" if self.detail else ""
        return (
            f"{self.__class__.__name__}: {self.message} "
            f"(operation={self.operation}, resource={self.resource}){suffix}"
        )


class TransportTimeoutError(ExecutionError):
    """Upstream deadline exceeded during execution."""


class RateLimitExceededError(ExecutionError):
    """Provider signaled rate limiting or temporary exhaustion (retry semantics live in policy)."""


__all__ = ["ExecutionError", "TransportTimeoutError", "RateLimitExceededError"]
