"""
Non-orchestration routing: deterministic provider selection + strict single-binding execution.

This package is a thin facade over :mod:`apipools.core` — it does **not** plan workloads,
merge heterogeneous feeds, or silently fall back across providers.
"""

from ..core.execution import ExecutionResult, MultiProviderExecutor
from ..core.providers.base import ProviderRequest
from ..core.providers.registry import ProviderRegistry
from ..core.selection.strategy import DeterministicProviderSelector

__all__ = [
    "DeterministicProviderSelector",
    "ExecutionResult",
    "MultiProviderExecutor",
    "ProviderRegistry",
    "ProviderRequest",
]
