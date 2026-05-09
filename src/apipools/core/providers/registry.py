"""Deterministic immutable provider registry."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .base import CoreProvider


@dataclass(frozen=True)
class ProviderRegistry:
    """Immutable deterministic provider map."""

    ordered_provider_ids: tuple[str, ...]
    _providers: Mapping[str, CoreProvider]

    @staticmethod
    def build(providers: tuple[CoreProvider, ...]) -> "ProviderRegistry":
        by_id = {provider.provider_id: provider for provider in providers}
        ordered_ids = tuple(sorted(by_id.keys()))
        ordered_map = MappingProxyType(
            {provider_id: by_id[provider_id] for provider_id in ordered_ids}
        )
        return ProviderRegistry(ordered_provider_ids=ordered_ids, _providers=ordered_map)

    def get(self, provider_id: str) -> CoreProvider:
        return self._providers[provider_id]

    def first_provider_id(self) -> str:
        return self.ordered_provider_ids[0]

    def items(self) -> tuple[tuple[str, CoreProvider], ...]:
        return tuple(
            (provider_id, self._providers[provider_id]) for provider_id in self.ordered_provider_ids
        )
