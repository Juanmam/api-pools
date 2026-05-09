"""Normalization package: capability-driven schema normalization."""

from .mapper import ProviderFieldMapping
from .normalizer import CapabilityNormalizer, mapping
from .schema import CanonicalField, CanonicalSchema

__all__ = [
    "CanonicalField",
    "CanonicalSchema",
    "ProviderFieldMapping",
    "CapabilityNormalizer",
    "mapping",
]
