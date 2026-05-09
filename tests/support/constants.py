"""Defaults for tests and docs examples — replace secrets in production."""

DEFAULT_VALIDATION_CURSOR_SECRET = b"apipools-validation-slice-secret"

# Example normalization version pin used by legacy mock normalizers in tests.
SUPPORTED_MOCK_PROJECTION_V1 = frozenset({"v1"})
