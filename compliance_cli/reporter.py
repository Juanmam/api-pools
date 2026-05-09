"""Deterministic report formatting for compliance snapshots."""

import json
from dataclasses import asdict

from .aggregator import ComplianceReport


def to_json(snapshot: ComplianceReport) -> str:
    payload = asdict(snapshot)
    return json.dumps(payload, indent=2, sort_keys=True)


def to_human(snapshot: ComplianceReport) -> str:
    lines: list[str] = [f"Compliance Score: {snapshot.global_score:.2f}%"]
    lines.append("")
    for clause in sorted(snapshot.clause_results, key=lambda c: c.clause_id):
        lines.append(f"{clause.clause_id} {clause.description} -> {clause.status.value}")
        if clause.notes:
            lines.append(f"  notes: {clause.notes}")
        lines.append(f"  tests: {', '.join(clause.tests) if clause.tests else 'none'}")
    lines.append("")
    lines.append("Warnings:")
    if snapshot.warnings:
        for warning in snapshot.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")
    return "\n".join(lines)
