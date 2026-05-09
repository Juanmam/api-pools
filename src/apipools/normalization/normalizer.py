"""Strict capability normalizer with explicit-only mappings."""

from dataclasses import dataclass
from typing import Any

from ..errors import CapabilityMismatchError
from .mapper import MappingTable, ProviderFieldMapping
from .schema import CanonicalSchema


@dataclass(frozen=True)
class CapabilityNormalizer:
    """Normalize one provider response against a canonical schema."""

    schema: CanonicalSchema
    mappings: MappingTable

    def normalize(
        self,
        provider_response: dict[str, Any],
        requested_fields: set[str],
    ) -> dict[str, Any]:
        # Reject unknown canonical requests upfront.
        unknown = sorted(field for field in requested_fields if not self.schema.has_field(field))
        if unknown:
            raise CapabilityMismatchError(
                message="Unknown canonical fields requested.",
                operation="normalize",
                resource=self.schema.resource,
                detail=f"unknown_fields={unknown}",
            )

        normalized: dict[str, Any] = {}
        for canonical_field in sorted(requested_fields):
            candidate_mappings = [m for m in self.mappings if m.canonical_field == canonical_field]
            if not candidate_mappings:
                raise CapabilityMismatchError(
                    message="Requested field has no explicit mapping.",
                    operation="normalize",
                    resource=self.schema.resource,
                    detail=f"field={canonical_field}",
                )
            if len(candidate_mappings) > 1:
                raise CapabilityMismatchError(
                    message="Ambiguous explicit mapping for requested field.",
                    operation="normalize",
                    resource=self.schema.resource,
                    detail=f"field={canonical_field}",
                )
            mapping = candidate_mappings[0]
            value = _extract_required(provider_response, mapping.provider_path)
            normalized[canonical_field] = value

        # Canonical output contains only requested canonical fields.
        return normalized


def _extract_required(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    parts = path.split(".")
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            raise CapabilityMismatchError(
                message="Provider payload missing required mapped field.",
                operation="normalize",
                resource="capability",
                detail=f"path={path}",
            )
        current = current[part]
    if current is None:
        raise CapabilityMismatchError(
            message="Provider payload returned null for required field.",
            operation="normalize",
            resource="capability",
            detail=f"path={path}",
        )
    return current


def mapping(*items: tuple[str, str]) -> MappingTable:
    """Helper for explicit mapping declarations in tests or adapters."""
    return tuple(
        ProviderFieldMapping(canonical_field=canonical, provider_path=provider_path)
        for canonical, provider_path in items
    )
