"""Entry point for constitutional compliance reporting."""

import json
from argparse import ArgumentParser
from pathlib import Path

from .aggregator import aggregate_compliance
from .engine import run_discovered_tests
from .reporter import to_human, to_json


def _load_previous(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = ArgumentParser(description="API Pools constitutional compliance engine")
    parser.add_argument(
        "--format",
        choices=("human", "json"),
        default="human",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional report output file path",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=None,
        help="Optional previous report JSON for drift detection",
    )
    args = parser.parse_args()

    outcomes = run_discovered_tests()
    snapshot = aggregate_compliance(outcomes, previous_snapshot=_load_previous(args.baseline))

    rendered = to_human(snapshot) if args.format == "human" else to_json(snapshot)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
