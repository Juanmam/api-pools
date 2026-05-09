Quickstart
============

Install
-------

.. code-block:: bash

   pip install apipools

Editable install when developing this repository:

.. code-block:: bash

   pip install -e ".[dev]"

Stable imports use the package root (see :doc:`api_reference`) or submodules such as :mod:`apipools.pagination`.

Design in one minute
--------------------

1. Model **canonical** entities and **capabilities** for your bounded context.
2. Implement a **binding** (see :class:`apipools.protocols.SocialSemanticBinding` for a social-shaped example port) with **pure** normalizers from vendor wire → canonical types.
3. Compose **pagination** and **capability validation** in your strategy/orchestration layer (this library provides primitives, not a full hosted runtime).

Capability validation
----------------------

.. code-block:: python

   from apipools import CapabilityContract, CapabilityLevel, CapabilityRegistry

   contracts = (
       CapabilityContract(
           resource="post",
           operation="read",
           level=CapabilityLevel.FULL,
           supported_fields=frozenset({"id", "text"}),
           unsupported_fields=frozenset(),
       ),
   )
   reg = CapabilityRegistry(contracts)
   check = reg.validate(
       resource="post",
       operation="read",
       requested_fields={"id", "text"},
       require_full=True,
   )
   assert check.gap is None

Implementing a binding (sketch)
--------------------------------

The library ships **protocols only**. Your application provides types that implement them.

.. literalinclude:: ../_snippets/example_binding.py
   :language: python

Version pins for normalization use :func:`apipools.assert_supported_projection_version` with the set of projection versions your adapters actually implement.

Semantic pagination (stack)
----------------------------

Use :class:`apipools.PaginationEngine` with :class:`apipools.CursorPaginationService` to enforce opaque client cursors and deterministic ordering for list operations. See :doc:`pagination-operations` for the full pattern.

Multi-provider selection (no orchestration)
--------------------------------------------

``apipools`` exposes :class:`apipools.routing.MultiProviderExecutor`, :class:`apipools.routing.ProviderRegistry`, and :class:`apipools.routing.DeterministicProviderSelector` against :class:`apipools.core.providers.ProviderRequest`. **Concrete** ``CoreProvider`` implementations are **not** included in the library—register your own adapters that declare capabilities and return canonical-shaped payloads.

Constitution compliance report (this repo)
-------------------------------------------

The :program:`apipools-compliance` CLI ships with the repository (``compliance_cli`` package). It runs the test suite and aggregates clause coverage.

.. code-block:: bash

   apipools-compliance --format human

Live API tests in this repository
-----------------------------------

Optional live tests and HTTP helpers for Meta/TikTok/YouTube-style APIs live under ``tests/support/social_live`` **for pytest only**. They require ``pip install -e ".[dev]"`` (``httpx``, ``authlib``). They are **not** part of the published ``apipools`` API.

Further reading
---------------

- :doc:`../architecture/index` — terminology and contracts
- :doc:`pagination-operations` — cursor and page semantics
- :doc:`api_reference` — module-level reference
