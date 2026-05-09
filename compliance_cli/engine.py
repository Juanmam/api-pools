"""Python-native test execution adapter for compliance evidence."""

import io
import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestOutcome:
    test_id: str
    passed: bool
    error_type: str | None
    elapsed_ms: int
    message: str | None = None


class _TimingResult(unittest.TextTestResult):
    """Custom result that captures pass/fail + elapsed timing."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self._start_times: dict[str, float] = {}
        self.outcomes: dict[str, TestOutcome] = {}

    def startTest(self, test) -> None:  # noqa: N802 (unittest API)
        test_id = test.id()
        self._start_times[test_id] = time.perf_counter()
        super().startTest(test)

    def _elapsed_ms(self, test_id: str) -> int:
        start = self._start_times.pop(test_id, None)
        if start is None:
            return 0
        return int((time.perf_counter() - start) * 1000)

    def addSuccess(self, test) -> None:  # noqa: N802 (unittest API)
        test_id = test.id()
        self.outcomes[test_id] = TestOutcome(
            test_id=test_id,
            passed=True,
            error_type=None,
            elapsed_ms=self._elapsed_ms(test_id),
        )
        super().addSuccess(test)

    def addFailure(self, test, err) -> None:  # noqa: N802 (unittest API)
        exc_type, exc, _ = err
        test_id = test.id()
        self.outcomes[test_id] = TestOutcome(
            test_id=test_id,
            passed=False,
            error_type=getattr(exc_type, "__name__", "Failure"),
            elapsed_ms=self._elapsed_ms(test_id),
            message=str(exc),
        )
        super().addFailure(test, err)

    def addError(self, test, err) -> None:  # noqa: N802 (unittest API)
        exc_type, exc, _ = err
        test_id = test.id()
        self.outcomes[test_id] = TestOutcome(
            test_id=test_id,
            passed=False,
            error_type=getattr(exc_type, "__name__", "Error"),
            elapsed_ms=self._elapsed_ms(test_id),
            message=str(exc),
        )
        super().addError(test, err)


class _TimingRunner(unittest.TextTestRunner):
    resultclass = _TimingResult


def run_discovered_tests(project_root: Path | None = None) -> dict[str, TestOutcome]:
    """Execute all `tests/test_*.py` with unittest discovery."""
    root = project_root or Path(__file__).resolve().parents[1]
    tests_dir = root / "tests"

    try:
        import apipools  # noqa: F401
    except ImportError:
        src_dir = root / "src"
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir), pattern="test_*.py")
    runner = _TimingRunner(stream=io.StringIO(), verbosity=0)
    result: _TimingResult = runner.run(suite)  # type: ignore[assignment]
    return dict(sorted(result.outcomes.items(), key=lambda item: item[0]))
