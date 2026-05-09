"""Facade: issue and resolve opaque pagination cursors."""

from __future__ import annotations

import time

from ..errors import InvalidCursorError
from .encoder import CursorEncoder
from .protocols import OpaqueCursorStorage
from .signer import CursorSigner
from .store import MemoryCursorStore
from .token import CursorToken


class CursorPaginationService:
    """Constitutional cursor pipeline: encode → store; decode → verify → store lookup."""

    def __init__(
        self,
        secret: bytes,
        *,
        binding_id: str,
        ttl_seconds: float,
        max_store_entries: int,
        storage: OpaqueCursorStorage | None = None,
    ) -> None:
        self._binding_id = binding_id
        self._store: OpaqueCursorStorage = storage or MemoryCursorStore(
            max_entries=max_store_entries, ttl_seconds=ttl_seconds
        )
        self._signer = CursorSigner(secret)
        self._encoder = CursorEncoder(
            self._signer,
            self._store,
            secret,
            max_encoder_state_keys=max_store_entries,
        )

    def issue(self, *, operation: str, resource: str, provider_cursor: str | None) -> str | None:
        if provider_cursor is None:
            return None
        token = CursorToken(
            provider_id=self._binding_id,
            operation=operation,
            resource=resource,
            provider_cursor=provider_cursor,
            issued_at_ns=time.time_ns(),
        )
        return self._encoder.encode(token)

    def resolve(
        self,
        client_cursor: str | None,
        *,
        operation: str,
        resource: str,
    ) -> str | None:
        if client_cursor is None:
            return None
        token = self._encoder.decode(client_cursor, operation=operation, resource=resource)
        if token.operation != operation or token.resource != resource:
            raise InvalidCursorError(
                message="Cursor scope mismatch.",
                operation=operation,
                resource=resource,
                detail="operation_or_resource_mismatch",
            )
        if token.provider_id != self._binding_id:
            raise InvalidCursorError(
                message="Cursor binding mismatch.",
                operation=operation,
                resource=resource,
                detail="provider_binding_mismatch",
            )
        return token.provider_cursor

    @property
    def store(self) -> OpaqueCursorStorage:
        return self._store

    @property
    def encoder(self) -> CursorEncoder:
        return self._encoder
