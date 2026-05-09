"""Deterministic provider selection strategy (no fallback)."""

from dataclasses import dataclass

from ...errors import NormalizationError
from ..providers.base import ProviderRequest
from ..providers.registry import ProviderRegistry


@dataclass(frozen=True)
class ProviderSelectionResult:
    provider_id: str
    reason: str


class DeterministicProviderSelector:
    """Reproducible provider selection from request + config + registry."""

    def __init__(
        self, registry: ProviderRegistry, *, default_provider_id: str | None = None
    ) -> None:
        self.registry = registry
        self.default_provider_id = default_provider_id

    def select(self, request: ProviderRequest) -> ProviderSelectionResult:
        if request.provider_override is not None:
            if request.provider_override not in self.registry.ordered_provider_ids:
                raise NormalizationError(
                    message="Explicit provider override does not exist in registry.",
                    operation=request.operation,
                    resource=request.resource,
                    detail=f"provider_override={request.provider_override}",
                )
            return ProviderSelectionResult(
                provider_id=request.provider_override,
                reason="explicit_override",
            )

        if self.default_provider_id is not None:
            if self.default_provider_id not in self.registry.ordered_provider_ids:
                raise NormalizationError(
                    message="Configured default provider not present in registry.",
                    operation=request.operation,
                    resource=request.resource,
                    detail=f"default_provider_id={self.default_provider_id}",
                )
            return ProviderSelectionResult(
                provider_id=self.default_provider_id,
                reason="configured_default",
            )

        return ProviderSelectionResult(
            provider_id=self.registry.first_provider_id(),
            reason="deterministic_registry_order",
        )
