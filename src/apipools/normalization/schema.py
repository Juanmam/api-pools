"""Canonical schema declarations for strict capability normalization."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalField:
    """Canonical field definition."""

    name: str


@dataclass(frozen=True)
class CanonicalSchema:
    """Canonical schema for one semantic resource."""

    resource: str
    fields: tuple[CanonicalField, ...]

    def has_field(self, field_name: str) -> bool:
        return any(field.name == field_name for field in self.fields)
