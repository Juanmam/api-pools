"""Immutable constitution clause and test-mapping registries."""

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


class TestKind(str, Enum):
    """Evidence class for mapped tests."""

    POSITIVE = "positive"
    VIOLATION = "violation"


@dataclass(frozen=True)
class TestMapping:
    clauses: tuple[str, ...]
    kind: TestKind


CLAUSE_REGISTRY = MappingProxyType(
    {
        "D-1": "Provider decision must be reproducible",
        "SP-1": "Semantic determinism",
        "SP-3": "Semantic visibility",
        "PP-1": "No silent degradation",
        "PP-2": "Explicit partiality visibility",
        "PP-5": "No semantic invention",
        "CC-1": "Provider selection must be explicit or deterministic",
        "CC-2": "Capability normalization must preserve semantic equivalence only",
        "CC-3": "Unsupported semantics must be explicit",
        "CC-5": "Compatibility must be computable",
        "N-1": "Normalization purity",
        "N-3": "Normalization determinism",
        "N-4": "Version-aware normalization targets",
        "IE-1": "Explicit semantic incompatibility categories",
        "IE-2": "Degradation visibility",
        "IE-3": "Cross-provider inconsistencies must be explicit",
        "PG-1": "Cursor opacity: client-visible cursors must not leak provider cursors",
        "PG-2": "Cursor integrity: signed envelope and explicit failures on tampering",
        "PG-3": "Cursor determinism: encoding is pure for a given token and secret",
        "PG-4": "Cursor lifecycle explicitness: TTL, bounded storage, and eviction are explicit",
        "D-5": "Capabilities remain declarative in core",
        "D-6": "Runtime/strategy must not absorb orchestration intelligence",
        "D-8": "Semantic error categories must be preserved",
    }
)


TEST_CLAUSE_MAP = MappingProxyType(
    {
        # validation slice
        "test_validation_slice.ValidationSliceTests.test_successful_post_retrieval_full_mapping": TestMapping(
            clauses=("SP-3", "N-4"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_partial_comment_mapping_is_explicit": TestMapping(
            clauses=("PP-2", "IE-2", "CC-5"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_capability_rejection_happens_before_execution": TestMapping(
            clauses=("CC-5", "CC-3"),
            kind=TestKind.VIOLATION,
        ),
        "test_validation_slice.ValidationSliceTests.test_pagination_uses_opaque_cursor": TestMapping(
            clauses=("PG-1", "PG-2"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_no_silent_degradation": TestMapping(
            clauses=("PP-1", "IE-2"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_normalization_is_deterministic": TestMapping(
            clauses=("SP-1", "N-3", "N-1"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_version_mismatch_is_explicit": TestMapping(
            clauses=("N-4", "IE-1", "D-8"),
            kind=TestKind.VIOLATION,
        ),
        "test_validation_slice.ValidationSliceTests.test_missing_text_is_explicit_not_fabricated": TestMapping(
            clauses=("PP-5", "PP-2"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_gap_propagates_for_read_post_when_degraded_allowed": TestMapping(
            clauses=("IE-2", "PP-2"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_gap_propagates_for_list_posts_when_degraded_allowed": TestMapping(
            clauses=("IE-2", "PG-2"),
            kind=TestKind.POSITIVE,
        ),
        "test_validation_slice.ValidationSliceTests.test_invalid_cursor_raises_semantic_error": TestMapping(
            clauses=("PG-4", "IE-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_validation_slice.ValidationSliceTests.test_tampered_cursor_raises_semantic_error": TestMapping(
            clauses=("PG-1", "PG-2"),
            kind=TestKind.VIOLATION,
        ),
        # second provider pressure
        "test_second_provider_pressure.SecondProviderPressureTests.test_capability_mismatch_fails_before_execution": TestMapping(
            clauses=("CC-3", "CC-5"),
            kind=TestKind.VIOLATION,
        ),
        "test_second_provider_pressure.SecondProviderPressureTests.test_partial_data_maps_to_explicit_field_status": TestMapping(
            clauses=("PP-2", "IE-2"),
            kind=TestKind.POSITIVE,
        ),
        "test_second_provider_pressure.SecondProviderPressureTests.test_cross_provider_same_intent_same_canonical_shape": TestMapping(
            clauses=("SP-3", "D-6", "D-5"),
            kind=TestKind.POSITIVE,
        ),
        "test_second_provider_pressure.SecondProviderPressureTests.test_second_provider_determinism": TestMapping(
            clauses=("SP-1", "N-3"),
            kind=TestKind.POSITIVE,
        ),
        "test_second_provider_pressure.SecondProviderPressureTests.test_second_provider_rejects_unsupported_rich_media_when_full_required": TestMapping(
            clauses=("CC-5", "PP-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_second_provider_pressure.SecondProviderPressureTests.test_full_required_rejects_partial_provider_before_execution": TestMapping(
            clauses=("CC-5",),
            kind=TestKind.VIOLATION,
        ),
        "test_second_provider_pressure.SecondProviderPressureTests.test_second_provider_pagination_gap_propagates": TestMapping(
            clauses=("PG-2", "IE-2", "PP-2"),
            kind=TestKind.POSITIVE,
        ),
        # multi-provider pressure
        "test_multi_provider_pressure.MultiProviderPressureTests.test_deterministic_provider_selection": TestMapping(
            clauses=("SP-1", "D-1", "CC-1"),
            kind=TestKind.POSITIVE,
        ),
        "test_multi_provider_pressure.MultiProviderPressureTests.test_capability_mismatch_does_not_fallback": TestMapping(
            clauses=("CC-3", "CC-5"),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_pressure.MultiProviderPressureTests.test_no_implicit_provider_switch": TestMapping(
            clauses=("CC-5", "D-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_pressure.MultiProviderPressureTests.test_cross_provider_inconsistency_detected": TestMapping(
            clauses=("IE-3", "PP-1", "IE-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_pressure.MultiProviderPressureTests.test_explicit_provider_override_respected": TestMapping(
            clauses=("CC-1", "D-1"),
            kind=TestKind.POSITIVE,
        ),
        "test_multi_provider_pressure.MultiProviderPressureTests.test_provider_registry_is_deterministic": TestMapping(
            clauses=("D-1", "SP-1"),
            kind=TestKind.POSITIVE,
        ),
        "test_multi_provider_pressure.MultiProviderPressureTests.test_same_request_same_result_across_runs": TestMapping(
            clauses=("SP-1", "D-1"),
            kind=TestKind.POSITIVE,
        ),
        # multi-provider violation injection
        "test_multi_provider_violations.MultiProviderViolationTests.test_non_deterministic_registry_order_detected": TestMapping(
            clauses=("D-1",),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_violations.MultiProviderViolationTests.test_selection_depends_on_runtime_state_forbidden": TestMapping(
            clauses=("SP-1", "CC-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_violations.MultiProviderViolationTests.test_provider_override_invalid_rejected": TestMapping(
            clauses=("CC-1", "IE-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_violations.MultiProviderViolationTests.test_cross_provider_hidden_divergence_forbidden": TestMapping(
            clauses=("IE-3", "PP-1"),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_violations.MultiProviderViolationTests.test_execution_path_attempts_fallback_forbidden": TestMapping(
            clauses=("CC-5",),
            kind=TestKind.VIOLATION,
        ),
        "test_multi_provider_violations.MultiProviderViolationTests.test_same_request_different_results_detected": TestMapping(
            clauses=("SP-1", "D-1"),
            kind=TestKind.VIOLATION,
        ),
        # capability normalization constitution
        "test_capability_normalization.CapabilityNormalizationTests.test_equivalent_fields_are_normalized": TestMapping(
            clauses=("CC-2",),
            kind=TestKind.POSITIVE,
        ),
        "test_capability_normalization.CapabilityNormalizationTests.test_missing_field_raises_error": TestMapping(
            clauses=("CC-3",),
            kind=TestKind.VIOLATION,
        ),
        "test_capability_normalization.CapabilityNormalizationTests.test_ambiguous_mapping_rejected": TestMapping(
            clauses=("CC-3",),
            kind=TestKind.VIOLATION,
        ),
        "test_capability_normalization.CapabilityNormalizationTests.test_no_silent_field_dropping": TestMapping(
            clauses=("PP-1",),
            kind=TestKind.VIOLATION,
        ),
        "test_capability_normalization.CapabilityNormalizationTests.test_nested_field_mapping": TestMapping(
            clauses=("CC-2",),
            kind=TestKind.POSITIVE,
        ),
        "test_capability_normalization.CapabilityNormalizationTests.test_provider_specific_shape_leak_forbidden": TestMapping(
            clauses=("IE-2", "CC-2"),
            kind=TestKind.VIOLATION,
        ),
        # strict rate limiting and backpressure
        "test_rate_limiting.RateLimitingTests.test_rate_limit_exceeded_raises_error": TestMapping(
            clauses=("IE-1",),
            kind=TestKind.VIOLATION,
        ),
        "test_rate_limiting.RateLimitingTests.test_no_retry_attempted": TestMapping(
            clauses=("SP-1",),
            kind=TestKind.VIOLATION,
        ),
        "test_rate_limiting.RateLimitingTests.test_no_fallback_on_rate_limit": TestMapping(
            clauses=("CC-5",),
            kind=TestKind.VIOLATION,
        ),
        "test_rate_limiting.RateLimitingTests.test_same_request_same_failure": TestMapping(
            clauses=("D-1",),
            kind=TestKind.VIOLATION,
        ),
        # cursor constitution
        "test_cursor_pagination.CursorPaginationTests.test_cursor_opacity": TestMapping(
            clauses=("PG-1",),
            kind=TestKind.POSITIVE,
        ),
        "test_cursor_pagination.CursorPaginationTests.test_cursor_tampering_detected": TestMapping(
            clauses=("PG-1", "PG-2"),
            kind=TestKind.VIOLATION,
        ),
        "test_cursor_pagination.CursorPaginationTests.test_cursor_expiration_enforced": TestMapping(
            clauses=("PG-4",),
            kind=TestKind.VIOLATION,
        ),
        "test_cursor_pagination.CursorPaginationTests.test_cursor_replay_determinism": TestMapping(
            clauses=("PG-3",),
            kind=TestKind.POSITIVE,
        ),
        "test_cursor_pagination.CursorPaginationTests.test_cursor_cross_instance_validity": TestMapping(
            clauses=("PG-3",),
            kind=TestKind.POSITIVE,
        ),
        "test_cursor_pagination.CursorPaginationTests.test_cursor_store_bounded": TestMapping(
            clauses=("PG-4",),
            kind=TestKind.VIOLATION,
        ),
        "test_cursor_violations.CursorViolationTests.test_forged_cursor_rejected": TestMapping(
            clauses=("PG-2",),
            kind=TestKind.VIOLATION,
        ),
        "test_cursor_violations.CursorViolationTests.test_cursor_reuse_after_expiration_forbidden": TestMapping(
            clauses=("PG-4",),
            kind=TestKind.VIOLATION,
        ),
        "test_cursor_violations.CursorViolationTests.test_cursor_modification_breaks_integrity": TestMapping(
            clauses=("PG-2",),
            kind=TestKind.VIOLATION,
        ),
        "test_cursor_violations.CursorViolationTests.test_non_deterministic_cursor_generation_forbidden": TestMapping(
            clauses=("PG-3",),
            kind=TestKind.VIOLATION,
        ),
    }
)
