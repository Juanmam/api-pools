"""Version-aware normalization targets (generic contract checks)."""

from __future__ import annotations

from .errors import VersionMismatchError


def assert_supported_projection_version(
    version: str,
    supported: frozenset[str],
    *,
    operation: str,
    resource: str,
) -> None:
    """Raise VersionMismatchError when the caller requests an unsupported normalization projection version."""
    if version not in supported:
        raise VersionMismatchError(
            message="Unsupported canonical version target.",
            operation=operation,
            resource=resource,
            detail=f"requested={version}, supported={sorted(supported)}",
        )


__all__ = [
    "assert_supported_projection_version",
]
