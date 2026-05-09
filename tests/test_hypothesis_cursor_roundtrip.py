"""Property checks for opaque cursor determinism and store round-trips."""

import time

from hypothesis import given, settings
from hypothesis import strategies as st

from apipools.pagination import CursorEncoder, CursorSigner, CursorToken
from apipools.pagination.store import MemoryCursorStore
from support.constants import DEFAULT_VALIDATION_CURSOR_SECRET

valid_id = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), min_codepoint=32),
    min_size=1,
    max_size=32,
)


@given(
    provider_id=valid_id,
    operation=valid_id,
    resource=valid_id,
    provider_cursor=valid_id,
)
@settings(deadline=None, max_examples=25)
def test_cursor_encode_decode_roundtrip(
    provider_id: str, operation: str, resource: str, provider_cursor: str
) -> None:
    signer = CursorSigner(DEFAULT_VALIDATION_CURSOR_SECRET)
    store = MemoryCursorStore(max_entries=64, ttl_seconds=3600.0)
    enc = CursorEncoder(signer, store, DEFAULT_VALIDATION_CURSOR_SECRET, max_encoder_state_keys=64)
    token = CursorToken(
        provider_id=provider_id,
        operation=operation,
        resource=resource,
        provider_cursor=provider_cursor,
        issued_at_ns=time.time_ns(),
    )
    opaque = enc.encode(token)
    dec = enc.decode(opaque, operation=operation, resource=resource)
    assert dec == token
