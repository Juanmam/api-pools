"""Deterministic opaque cursor encoding with HMAC envelope integrity."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
from collections import OrderedDict
from typing import TYPE_CHECKING

from ..errors import InvalidCursorError, TamperedCursorError
from .signer import CursorSigner
from .token import CursorToken

if TYPE_CHECKING:
    from .protocols import OpaqueCursorStorage


def canonical_token_bytes(token: CursorToken) -> bytes:
    meta = "|".join(f"{k}={v}" for k, v in sorted(token.metadata))
    lines = [
        f"provider_id={token.provider_id}",
        f"operation={token.operation}",
        f"resource={token.resource}",
        f"provider_cursor={token.provider_cursor}",
        f"issued_at_ns={token.issued_at_ns}",
        f"metadata={meta}",
    ]
    return "\n".join(lines).encode("utf-8")


def store_key(secret: bytes, token: CursorToken) -> str:
    return hmac.new(secret, canonical_token_bytes(token), hashlib.sha256).hexdigest()


class CursorEncoder:
    """
    Encode CursorToken → opaque client string (provider cursor never embedded in plaintext).

    Decoding verifies HMAC envelope then resolves token from bounded storage.
    """

    def __init__(
        self,
        signer: CursorSigner,
        store: OpaqueCursorStorage,
        secret: bytes,
        *,
        max_encoder_state_keys: int,
    ) -> None:
        self._signer = signer
        self._store = store
        self._secret = secret
        if max_encoder_state_keys < 1:
            raise ValueError("max_encoder_state_keys must be >= 1")
        self._max_encoder_state_keys = max_encoder_state_keys
        self._determinism_by_key: OrderedDict[str, str] = OrderedDict()

    def encode(self, token: CursorToken) -> str:
        key = store_key(self._secret, token)
        self._store.put(key, token)
        envelope = f"v1|{key}".encode("ascii")
        sig = self._signer.sign(envelope)
        wire = f"v1|{key}|{sig}".encode("ascii")
        opaque = base64.urlsafe_b64encode(wire).decode("ascii").rstrip("=")
        prior = self._determinism_by_key.get(key)
        if prior is not None and prior != opaque:
            raise InvalidCursorError(
                message="Determinism violation detected: same logical cursor encodes differently.",
                operation=token.operation,
                resource=token.resource,
                detail="nondeterministic_cursor_encoding",
            )
        self._determinism_by_key[key] = opaque
        self._determinism_by_key.move_to_end(key, last=True)
        while len(self._determinism_by_key) > self._max_encoder_state_keys:
            self._determinism_by_key.popitem(last=False)
        return opaque

    def decode(self, opaque: str, *, operation: str, resource: str) -> CursorToken:
        try:
            padded = opaque + "=" * (-len(opaque) % 4)
            raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        except (ValueError, binascii.Error) as exc:
            raise InvalidCursorError(
                message="Cursor is not valid base64url envelope.",
                operation=operation,
                resource=resource,
                detail="invalid_base64",
            ) from exc
        try:
            wire = raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise InvalidCursorError(
                message="Cursor envelope is not valid opaque ASCII wiring.",
                operation=operation,
                resource=resource,
                detail="invalid_ascii_envelope",
            ) from exc
        parts = wire.split("|")
        if len(parts) != 3:
            raise InvalidCursorError(
                message="Cursor envelope has unexpected structure.",
                operation=operation,
                resource=resource,
                detail="bad_part_count",
            )
        version, key, signature = parts
        if version != "v1":
            raise InvalidCursorError(
                message="Unsupported cursor version.",
                operation=operation,
                resource=resource,
                detail=f"version={version}",
            )
        envelope = f"v1|{key}".encode("ascii")
        if not self._signer.verify(envelope, signature):
            raise TamperedCursorError(
                message="Cursor HMAC verification failed.",
                operation=operation,
                resource=resource,
                detail="envelope_integrity",
            )
        return self._store.get(key, operation=operation, resource=resource)
