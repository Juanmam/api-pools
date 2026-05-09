"""Clause-level compliance aggregation and drift detection."""

from dataclasses import dataclass
from enum import Enum

from .engine import TestOutcome
from .registry import CLAUSE_REGISTRY, TEST_CLAUSE_MAP, TestKind


class ClauseStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WEAK = "WEAK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ClauseResult:
    clause_id: str
    description: str
    status: ClauseStatus
    tests: list[str]
    notes: str | None


@dataclass(frozen=True)
class ComplianceReport:
    global_score: float
    clause_results: list[ClauseResult]
    warnings: list[str]


def _score(status: ClauseStatus) -> float:
    return {
        ClauseStatus.PASS: 1.0,
        ClauseStatus.WEAK: 0.5,
        ClauseStatus.UNKNOWN: 0.0,
        ClauseStatus.FAIL: 0.0,
    }[status]


def aggregate_compliance(
    outcomes: dict[str, TestOutcome], previous_snapshot: dict | None = None
) -> ComplianceReport:
    clause_to_tests: dict[str, list[str]] = {clause: [] for clause in CLAUSE_REGISTRY}
    warnings: list[str] = []

    for test_id, mapping in TEST_CLAUSE_MAP.items():
        for clause in mapping.clauses:
            if clause in clause_to_tests:
                clause_to_tests[clause].append(test_id)

    clause_results: list[ClauseResult] = []
    for clause_id in sorted(CLAUSE_REGISTRY):
        mapped_tests = sorted(clause_to_tests[clause_id])
        if not mapped_tests:
            clause_results.append(
                ClauseResult(
                    clause_id=clause_id,
                    description=CLAUSE_REGISTRY[clause_id],
                    status=ClauseStatus.UNKNOWN,
                    tests=[],
                    notes="No mapped tests.",
                )
            )
            warnings.append(f"Clause {clause_id} has no mapped tests.")
            continue

        missing_outcomes = [t for t in mapped_tests if t not in outcomes]
        if missing_outcomes:
            warnings.append(f"Clause {clause_id} has mapped tests not executed: {missing_outcomes}")

        executed = [t for t in mapped_tests if t in outcomes]
        failures = [t for t in executed if not outcomes[t].passed]
        has_positive = any(TEST_CLAUSE_MAP[t].kind is TestKind.POSITIVE for t in mapped_tests)
        has_violation = any(TEST_CLAUSE_MAP[t].kind is TestKind.VIOLATION for t in mapped_tests)

        notes: list[str] = []
        if failures:
            status = ClauseStatus.FAIL
            notes.append(f"Failing tests: {failures}")
        else:
            if has_positive and not has_violation:
                status = ClauseStatus.WEAK
                notes.append("No violation tests mapped.")
            else:
                # PASS for mixed evidence OR violation-only evidence,
                # matching requested semantics.
                status = ClauseStatus.PASS

        clause_results.append(
            ClauseResult(
                clause_id=clause_id,
                description=CLAUSE_REGISTRY[clause_id],
                status=status,
                tests=mapped_tests,
                notes="; ".join(notes) if notes else None,
            )
        )

    if previous_snapshot:
        prev_results = {
            item["clause_id"]: item["status"]
            for item in previous_snapshot.get("clause_results", [])
            if "clause_id" in item and "status" in item
        }
        status_order = {"UNKNOWN": 0, "WEAK": 1, "PASS": 2, "FAIL": -1}
        for clause in clause_results:
            prev = prev_results.get(clause.clause_id)
            if prev is None:
                continue
            if status_order.get(clause.status.value, 0) < status_order.get(prev, 0):
                warnings.append(
                    f"Clause {clause.clause_id} regressed from {prev} to {clause.status.value}."
                )

    total = len(clause_results) or 1
    score = round((sum(_score(c.status) for c in clause_results) / total) * 100, 2)
    return ComplianceReport(global_score=score, clause_results=clause_results, warnings=warnings)
