Architecture
============

This section contains **conceptual architecture documentation** for API Pools. It defines terminology, boundaries, invariants, and semantic contracts **without implementation detail**. It is intended to stabilize the foundation before code structure and providers are introduced.

Project identity
----------------

**API Pools is a semantic interoperability framework for heterogeneous APIs.**

It is **not** an API wrapper framework, a bare transport abstraction, an orchestration engine, an ETL platform, or a federation or query engine—although downstream systems may build those **using** the interoperability substrate API Pools defines.

**Core value proposition:** API Pools standardizes what “the same thing” means across vendors, while making incompatibility **explicit and computable**.

Documents
---------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Document
     - Scope
   * - :doc:`canonical-resource-system`
     - Semantic center: ontology, invariants, projections, pagination as resource semantics, bounded contexts
   * - :doc:`strategy-contracts`
     - Bounded semantic contexts, lawful behavior, transport-agnostic contracts
   * - :doc:`capability-contracts`
     - Behavioral compatibility, constraints, validation, future-facing negotiation inputs
   * - :doc:`normalization-contracts`
     - Provider truth vs canonical truth, version-aware mapping, fidelity and provenance
   * - :doc:`interoperability-error-semantics`
     - First-class failure modes, structured incompatibility, observability

Minimum coherent core
---------------------

The architecture rests on a **core semantic triangle**:

1. **Canonical resources** — stable meaning and ontology inside a strategy-bounded context
2. **Strategy contracts** — lawful domain semantics and resource-scoped operations
3. **Provider semantic adapters** — faithful translation from provider reality to canonical commitments, with explicit limits

**Supporting contracts:** capability contracts, normalization contracts, semantic pagination, canonical versioning, interoperability error semantics.

Boundary summary
----------------

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Domain
     - Role
   * - **Core**
     - Canonical resources, ontology, strategies, capabilities, normalization, pagination semantics, versioning, error semantics
   * - **Execution**
     - Transport, authentication, runtime context, retries, concurrency, serialization—**only** to execute semantic contracts
   * - **Optional / extensional**
     - Orchestration, planners, identity resolution, federation, merge engines—**separate modules**, must not define core types

Architectural constraints (non-exhaustive)
--------------------------------------------

- No hidden orchestration or implicit federation inside core contracts
- No masking of provider truth; gaps must be representable
- No silent semantic degradation; failures are explicit
- Runtime is a composition root and policy surface—not an orchestration brain
- Shallow taxonomies; prefer composition over deep inheritance
- Guard against universal data model creep across unrelated bounded contexts

For full detail, read the linked documents in the toctree below.

.. toctree::
   :maxdepth: 2
   :caption: Architecture topics

   canonical-resource-system
   strategy-contracts
   capability-contracts
   normalization-contracts
   interoperability-error-semantics
