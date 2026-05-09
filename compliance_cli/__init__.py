"""Constitutional compliance engine package."""

from .aggregator import ClauseResult, ClauseStatus, ComplianceReport, aggregate_compliance
from .engine import TestOutcome, run_discovered_tests
from .registry import CLAUSE_REGISTRY, TEST_CLAUSE_MAP, TestKind, TestMapping
from .reporter import to_human, to_json

__all__ = [
    "ClauseResult",
    "ClauseStatus",
    "ComplianceReport",
    "aggregate_compliance",
    "TestOutcome",
    "run_discovered_tests",
    "CLAUSE_REGISTRY",
    "TEST_CLAUSE_MAP",
    "TestKind",
    "TestMapping",
    "to_human",
    "to_json",
]
