Implementation map
====================

This page describes how the **Python package** ``apipools`` maps to the conceptual architecture. It complements the contract-first topics in this section (which stay transport- and vendor-agnostic).

Purpose
-------

``apipools`` is a **semantic interoperability** library: canonical types, capability validation, version-aware normalization helpers, semantic pagination, structured interoperability errors, and thin **execution** facades. Vendor-specific adapters, mocks, and demo providers live **outside** the installable package (for this repository, under ``tests/support/``) so applications can ship their own bindings.

Conceptual layers
-----------------

1. **Core semantics** — Canonical resources, capability contracts, normalization schema helpers, pagination semantics, ``assert_supported_projection_version``.
2. **Execution** — Transport-scoped errors (timeouts, rate limits); optional resilience helpers.
3. **Your code** — Protocol implementations (e.g. :class:`apipools.protocols.SocialSemanticBinding`), HTTP clients, credentials.

Python package map
------------------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Module / package
     - Role
   * - ``apipools.canonical``
     - Canonical domain instances and projection-friendly fields.
   * - ``apipools.capabilities``
     - Declarative capability contracts and :class:`~apipools.capabilities.CapabilityRegistry` validation.
   * - ``apipools.protocols``
     - :class:`~apipools.protocols.SocialSemanticBinding` and related ``Protocol`` definitions (contracts only).
   * - ``apipools.pagination``
     - :class:`~apipools.pagination.PaginationEngine`, :class:`~apipools.pagination.CursorPaginationService`, opaque cursors, pluggable storage (memory; optional Redis).
   * - ``apipools.normalization``
     - Schema-driven :class:`~apipools.normalization.normalizer.CapabilityNormalizer` (no vendor wire baked in).
   * - ``apipools.errors`` / ``apipools.execution.errors``
     - Interoperability vs execution failure taxonomy.
   * - ``apipools.versioning``
     - :func:`~apipools.versioning.assert_supported_projection_version` for normalization target pins.
   * - ``apipools.core``
     - :class:`~apipools.core.execution.MultiProviderExecutor`, provider registry, deterministic selection (generic; **no** demo providers in-package).
   * - ``apipools.routing``
     - Convenience re-exports for single-binding execution without orchestration.
   * - ``apipools.resilience``
     - Rate-limit and executor wrapper policies.

Operational entry points
------------------------

- **Library:** ``import apipools`` for stable root re-exports, or import submodules explicitly.
- **Constitution compliance CLI:** ``apipools-compliance`` (implemented as the separate ``compliance_cli`` package in this repo; not part of the public library API).
- **Extras:** ``pip install apipools[redis]`` for :mod:`apipools.pagination.redis_store`.

Reference flow (example)
------------------------

Application intent → :class:`~apipools.capabilities.CapabilityRegistry` validates requested projection → your adapter fetches **wire** dicts and runs **pure** normalizers → canonical instances → pagination services issue opaque cursors.
