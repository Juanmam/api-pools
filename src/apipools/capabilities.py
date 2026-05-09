"""Structured capability contracts for one provider."""

from dataclasses import dataclass
from enum import Enum

from .errors import PartialCapabilityError, UnsupportedCapabilityError


class CapabilityLevel(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class CapabilityContract:
    resource: str
    operation: str
    level: CapabilityLevel
    supported_fields: frozenset[str]
    unsupported_fields: frozenset[str]


@dataclass(frozen=True)
class CapabilityValidationResult:
    accepted: bool
    degraded: bool
    gap: str | None = None


class CapabilityRegistry:
    """Contract registry and pre-execution validator."""

    def __init__(self, contracts: tuple[CapabilityContract, ...]) -> None:
        self._contracts = {(c.resource, c.operation): c for c in contracts}

    def validate(
        self,
        *,
        resource: str,
        operation: str,
        requested_fields: set[str],
        require_full: bool,
    ) -> CapabilityValidationResult:
        contract = self._contracts.get((resource, operation))
        if contract is None or contract.level is CapabilityLevel.UNSUPPORTED:
            raise UnsupportedCapabilityError(
                message="Operation unsupported by provider capability contract.",
                operation=operation,
                resource=resource,
            )

        if require_full and contract.level is CapabilityLevel.PARTIAL:
            raise PartialCapabilityError(
                message="Provider declares only partial capability for this operation.",
                operation=operation,
                resource=resource,
            )

        unsupported = requested_fields - contract.supported_fields
        if not unsupported:
            return CapabilityValidationResult(accepted=True, degraded=False)

        if require_full:
            raise PartialCapabilityError(
                message="Requested projection exceeds declared capability floor.",
                operation=operation,
                resource=resource,
                detail=f"unsupported_fields={sorted(unsupported)}",
            )

        return CapabilityValidationResult(
            accepted=True,
            degraded=True,
            gap=f"unsupported_fields={sorted(unsupported)}",
        )
