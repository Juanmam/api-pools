Pagination operations
=====================

Defaults
--------

* **MemoryCursorStore** — in-process FIFO TTL map. Safe for single-worker tests and prototypes; evictions surface as :class:`apipools.errors.ExpiredCursorError`.
* **RedisCursorStore** — external TTL via a Redis-compatible client (``setex`` / ``get``). Share one client pool per deployment; keys are prefixed (default ``apipools:cursor:``).

Signing
-------

Cursors are opaque base64url blobs. The envelope is HMAC-protected; provider-native cursors are never returned verbatim to callers.

Injecting storage
-----------------

``CursorPaginationService`` accepts ``storage=`` to plug in any implementation of :class:`apipools.pagination.protocols.OpaqueCursorStorage`.

Rotation
--------

Rotate the HMAC secret on a defined cadence. Old cursors fail closed (tamper / unknown semantics) once the signing key changes; plan client-visible messaging for “restart listing from the first page.”

Horizontal scale
----------------

For multiple app instances, prefer **RedisCursorStore** (or another shared store) so encoded keys resolve regardless of which replica issued the cursor.
