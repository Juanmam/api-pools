"""API Pools — semantic interoperability primitives (stable root exports)."""

from ._version import __version__
from .canonical import (
    CanonicalComment,
    CanonicalPost,
    FieldStatus,
    SemanticField,
)
from .capabilities import CapabilityContract, CapabilityLevel, CapabilityRegistry
from .errors import (
    CapabilityMismatchError,
    CrossProviderInconsistencyError,
    ExpiredCursorError,
    InteroperabilityError,
    InvalidCursorError,
    NormalizationError,
    PaginationInvariantError,
    PartialCapabilityError,
    TamperedCursorError,
    UnsupportedCapabilityError,
    VersionMismatchError,
)
from .execution.errors import (
    ExecutionError,
    TransportTimeoutError,
)
from .execution.errors import (
    RateLimitExceededError as TransportRateLimitExceededError,
)
from .pagination import (
    CursorPaginationService,
    CursorToken,
    MemoryCursorStore,
    OpaqueCursorStorage,
    Page,
    PaginationConfig,
    PaginationEngine,
    PaginationFetchResult,
    PaginationState,
)
from .versioning import assert_supported_projection_version

# Protocols: ``apipools.protocols``. Multi-binding execution: ``apipools.routing``.
# Resilience helpers: ``apipools.resilience``.

__all__ = [
    "__version__",
    "CanonicalComment",
    "CanonicalPost",
    "FieldStatus",
    "SemanticField",
    "CapabilityContract",
    "CapabilityLevel",
    "CapabilityRegistry",
    "CapabilityMismatchError",
    "CrossProviderInconsistencyError",
    "ExpiredCursorError",
    "InteroperabilityError",
    "InvalidCursorError",
    "NormalizationError",
    "PaginationInvariantError",
    "PartialCapabilityError",
    "TamperedCursorError",
    "UnsupportedCapabilityError",
    "VersionMismatchError",
    "ExecutionError",
    "TransportTimeoutError",
    "TransportRateLimitExceededError",
    "Page",
    "CursorToken",
    "CursorPaginationService",
    "OpaqueCursorStorage",
    "MemoryCursorStore",
    "PaginationConfig",
    "PaginationEngine",
    "PaginationFetchResult",
    "PaginationState",
    "assert_supported_projection_version",
]
