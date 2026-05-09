"""Execution flow for multi-provider pressure tests."""

from dataclasses import dataclass

from ..capabilities import CapabilityRegistry
from ..errors import CrossProviderInconsistencyError
from .providers.base import ProviderRequest
from .providers.registry import ProviderRegistry
from .selection.strategy import DeterministicProviderSelector


@dataclass(frozen=True)
class ExecutionResult:
    provider_id: str
    selection_reason: str
    payload: dict
    gap: str | None = None


class MultiProviderExecutor:
    """Strict no-fallback executor: select -> validate -> execute."""

    def __init__(self, registry: ProviderRegistry, selector: DeterministicProviderSelector) -> None:
        self.registry = registry
        self.selector = selector

    def execute(self, request: ProviderRequest) -> ExecutionResult:
        selection = self.selector.select(request)
        provider = self.registry.get(selection.provider_id)
        validation = CapabilityRegistry(provider.capabilities()).validate(
            resource=request.resource,
            operation=request.operation,
            requested_fields=set(request.requested_fields),
            require_full=request.require_full,
        )
        payload = provider.execute(request)
        return ExecutionResult(
            provider_id=provider.provider_id,
            selection_reason=selection.reason,
            payload=payload,
            gap=validation.gap,
        )

    def detect_cross_provider_inconsistency(self, request: ProviderRequest) -> None:
        """Pressure-test helper to surface structural mismatch explicitly."""
        signatures: dict[str, tuple[str, ...]] = {}
        for provider_id, provider in self.registry.items():
            # Consistency checks are explicit pressure-test actions, not fallback.
            CapabilityRegistry(provider.capabilities()).validate(
                resource=request.resource,
                operation=request.operation,
                requested_fields=set(request.requested_fields),
                require_full=False,
            )
            payload = provider.execute(request)
            if request.operation == "read":
                keys = tuple(sorted(payload.get("item", {}).keys()))
            else:
                items = payload.get("items", [])
                keys = tuple(sorted(items[0].keys())) if items else tuple()
            signatures[provider_id] = keys

        unique_signatures = {sig for sig in signatures.values()}
        if len(unique_signatures) > 1:
            raise CrossProviderInconsistencyError(
                message="Cross-provider structural inconsistency detected.",
                operation=request.operation,
                resource=request.resource,
                detail=str(signatures),
            )
