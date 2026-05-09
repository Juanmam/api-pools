"""Core multi-provider pressure-test contracts."""

from dataclasses import dataclass
from typing import Protocol

from ...capabilities import CapabilityContract


@dataclass(frozen=True)
class ProviderRequest:
    """Deterministic request shape for provider selection/execution."""

    resource: str
    operation: str
    requested_fields: frozenset[str]
    require_full: bool = True
    provider_override: str | None = None
    cursor: str | None = None
    limit: int = 2
    consistency_check: bool = False


class CoreProvider(Protocol):
    provider_id: str
    cursor_kind: str
    execution_count: int

    def capabilities(self) -> tuple[CapabilityContract, ...]:
        """Declared capability contracts."""

    def execute(self, request: ProviderRequest) -> dict:
        """Return canonical-shaped result payload for pressure tests."""
