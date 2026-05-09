"""Explicit provider-to-canonical field mappings (no inference)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderFieldMapping:
    """Map one canonical field to one explicit provider path."""

    canonical_field: str
    provider_path: str


MappingTable = tuple[ProviderFieldMapping, ...]
