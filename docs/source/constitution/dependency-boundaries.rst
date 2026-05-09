Dependency and boundary constitution
======================================

Preamble
--------

**Dependency direction** encodes **semantic authority**. Reversed edges import hidden orchestration, wire coupling, and universal models into the core. This chapter defines **allowed** and **forbidden** dependencies to preserve long-term maintainability and interoperability honesty.

Layers (conceptual)
-------------------

.. code-block:: text

   [ Application / optional orchestration* ]

              │ uses

   [ Core semantics: resources, strategies, capabilities,
     normalization contracts, pagination semantics,
     interoperability errors, versioning policy ]

              │ uses

   [ Execution: transport, auth, runtime policies ]

   * Optional modules must not be depended upon by core.

Constitutional rules (representative)
--------------------------------------

**D-1 — Core MUST NOT depend on orchestration**
   No imports or conceptual reliance on planners, execution graphs, multi-provider coordinators.

**D-2 — Core MUST NOT depend on federation or identity-graph engines**
   Cross-provider reconciliation is **non-core**.

**D-3 — Canonical models MUST NOT depend on providers**
   No provider SDK types, vendor-generated stubs, or transport types in canonical definitions.

**D-4 — Normalization MUST remain transport-independent**
   No sockets, clients, or retry policies inside semantic translation.

**D-5 — Capabilities MUST remain declarative in core**
   Capabilities describe offers/constraints; they **do not** execute plans.

**D-6 — Runtime MUST NOT absorb orchestration intelligence**
   Runtime wires policies and execution; it does **not** decide multi-provider strategies or semantic merges.

**D-7 — Optional modules MUST NOT redefine core types**
   Extensions consume **ports**; core never imports extension concrete modules.

**D-8 — Semantic layers MUST NOT lose error categories**
   Surfacing to callers preserves interoperability discrimination—see :doc:`interoperability-errors`.

Why direction matters
---------------------

Drift begins with “just one helper” that imports a planner “temporarily.” **Law** prevents erosion into a god runtime.

Optional module containment
---------------------------

Optional capabilities **may** ship as separate artifacts that depend on **core contracts only**. They **must** remain **replaceable** and **detachable** without forked core.

Semantic isolation
------------------

**Bounded contexts** remain isolated at the canonical level—**no** shared mega-types across strategies in core.

Related chapters
----------------

- :doc:`provider-adapters`  
- :doc:`non-goals`  
- :doc:`adr-index`  
