Canonical resource system
=========================

Purpose
-------

This document defines the **canonical resource system**: what canonical resources are, why they sit at the semantic center of API Pools, and how they relate to ontology, invariants, identity, relationships, projections, pagination, lifecycle, and bounded contexts.

It remains **conceptual**. It does **not** prescribe concrete schemas, field lists, or serialization formats.

What canonical resources are
----------------------------

**Canonical resources** are the framework’s **stable semantic units of meaning** for a given **strategy-bounded context**. They represent entities and value-bearing constructs—such as posts, users, payments, messages—not as vendor payloads and not as endpoint shapes, but as **shared vocabulary** that downstream logic can rely on when reasoning about “the same thing” across providers.

A canonical resource carries:

- **Semantic identity** within the model (how the resource is referenced and distinguished from others of the same kind).
- **Declared structure** for attributes that are part of the interoperability promise (which may be partial by design).
- **Explicit uncertainty** where vendor truth does not map cleanly (handled via normalization contracts and interoperability errors—not by silent defaults).

Canonical resources are **not** universal rows in a global enterprise model spanning unrelated domains. They are **scoped** by strategy and version.

Why canonical resources are the semantic center
-----------------------------------------------

API Pools exists to answer: *when two vendors expose related real-world phenomena, what do we call “the same thing,” and what do we refuse to pretend is the same?*

Without canonical resources:

- Integration logic disperses into ad hoc dict shapes and one-off mappers.
- Pagination, sorting, and “what counts as a list” diverge per operation.
- Versioning applies unpredictably to methods instead of to **meaning**.

With canonical resources:

- **Normalization has a target**: canonical truth, versioned.
- **Capabilities attach to resource-level access patterns** (what can be listed, filtered, streamed).
- **Errors can be tied to semantic mismatch** (unsupported projection, incompatible page semantics).

The resource layer is therefore the **anchor** for interoperability honesty.

Resource ontology
-----------------

**Ontology**, in this framework, means the **structured set of resource kinds**, their **relationships**, and the **invariants** that hold among them within a strategy.

Conceptual elements include:

- **Resource kinds** — categories of canonical entities (e.g., within a messaging strategy: conversation, message, participant).
- **Relationships** — cardinality and ownership (e.g., messages belong to conversations; participants link users to conversations).
- **Cross-resource references** — how one resource points to another using canonical identity semantics.
- **Derivation boundaries** — which attributes are intrinsic to the resource vs computed or vendor-specific extensions surfaced elsewhere.

Ontology is **strategy-local**. Reusing names across strategies is a documentation and governance concern, not an invitation to merge unrelated domains into one mega-model.

Invariants
----------

**Invariants** are rules that canonical instances are expected to satisfy **when a provider claims full compatibility** for a given capability slice. Examples of invariant *classes* (not specific fields):

- **Referential integrity** — if a child resource references a parent, the reference resolves under declared rules or the instance is rejected as invalid for that projection.
- **Lifecycle consistency** — deleted or archived states interact predictably with listing and retrieval.
- **Temporal ordering** — when “time” is part of canonical semantics, ordering rules are explicit for list and stream operations.

Invariants may be **relaxed** when partial compatibility is declared; that relaxation must be **capability-visible**, not implicit.

Identity semantics
------------------

**Identity** answers: *how do we refer to “this” canonical resource instance?*

Conceptual dimensions:

- **Canonical identifier** — opaque or structured per strategy rules; stable within a provider binding where possible.
- **Identity strength** — whether identifiers are globally stable, stable per tenant, or ephemeral.
- **Equivalence** — when two references denote the same logical entity; cross-provider equivalence is **not** assumed in core unless explicitly modeled as an extension.

API Pools distinguishes **canonical identity** from **provider-native keys**. Adapters are responsible for mapping; core retains rules for what identity means **in canonical space**.

Relationships
-------------

Relationships model **graphs of resources** inside the ontology:

- **Composition vs association** — owns vs links.
- **Cardinality** — one-to-many constraints relevant to lawful queries.
- **Navigability** — which directions of traversal are supported by contracts vs optional expansions.

Relationship semantics drive **which operations are meaningful** (e.g., “messages for conversation X”) and **how pagination scopes** (page through messages within one conversation vs global feeds).

Projections
-----------

A **projection** is a **subset or view** of a canonical resource’s semantics—fields, nested shapes, or computed facets—that a caller requests or that a provider can supply.

Projections matter because:

- Full materialization is often impossible or expensive across vendors.
- Interoperability requires **explicit** partiality: what was omitted vs never supported.

Core principle: projections are **named or typed intent**, not ambiguous sparse dicts. Capability contracts tie supported projections to provider behavior.

Pagination semantics
----------------------

Pagination is modeled as a **resource-access primitive**, not as an afterthought per operation.

Conceptual components:

- **Page as a unit** — what constitutes one page (items, cursors, stability guarantees).
- **Opaque continuation** — providers encode vendor-specific continuation tokens behind canonical pagination envelopes where appropriate.
- **Ordering** — lawful sort semantics for a resource collection within the strategy.

Semantic pagination ensures **list/stream contracts** remain coherent across adapters without each method reinventing offset/limit assumptions unsuitable for half of vendor APIs.

Resource lifecycle concepts
---------------------------

Resources undergo **states** relevant to retrieval and mutation where strategies include writes:

- **Existence** — created, active, archived, deleted (terminology strategy-specific).
- **Visibility** — whether listed endpoints include or exclude certain states.
- **Transitions** — lawful changes and how they surface in canonical operations.

Lifecycle belongs in ontology and strategy contracts; transports do not define lifecycle.

Bounded context considerations
------------------------------

API Pools adopts **bounded contexts** in the DDD sense at the **strategy** level:

- **Social**, **payment**, and **messaging** strategies are separate semantic languages.
- Canonical resources in one strategy **must not** be forced into another’s ontology “for reuse.”

**Risks of universal model creep:**

- A single ``User`` or ``Account`` type spanning every domain collapses distinctions and forces dishonest mappings.
- Coupling unrelated teams and release cycles into one evolving mega-schema.

**Mitigation:** strict strategy boundaries, explicit **anti-corruption** via adapters at edges, and cross-context integration only in **application or extension layers**—not in core canonical definitions.

Resources vs operation-centric design
-------------------------------------

**Operation-centric** design centers on verbs (``list_posts``, ``charge``) without a stable notion of the entities those verbs manipulate. At scale it tends to:

- Duplicate pagination, filtering, and error semantics per endpoint family.
- Hide structural drift when vendors change payloads but names stay the same.

**Resource-centric** design anchors operations to **what exists** in the ontology and **what lawful queries** mean for those resources. Operations become **resource-scoped** (retrieve, list with semantics, stream) rather than an unconstrained service surface.

API Pools prefers resource-centric **canonical modeling** while still allowing ergonomic façades in user-facing APIs **as long as** they reduce to the same contracts.

How providers map into canonical resources
------------------------------------------

**Provider semantic adapters** consume provider truth (wire representations, vendor semantics) and produce **canonical resource instances** subject to:

- Normalization contracts (versioned).
- Capability contracts (what is supported).
- Explicit degradation or errors when mapping cannot satisfy requested projections or invariants.

The canonical layer **never** embeds transport details; it receives **already-interpreted** semantic outcomes from the adapter boundary or rejects with interoperability errors.

Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Topic
     - Role in API Pools
   * - Canonical resources
     - Stable semantic center and interoperability target
   * - Ontology & invariants
     - Lawful structure within a strategy
   * - Identity & relationships
     - Meaning of references and graphs
   * - Projections
     - Explicit partiality
   * - Pagination
     - First-class resource-access semantics
   * - Bounded contexts
     - Defense against universal model creep

Related documents
-----------------

- :doc:`strategy-contracts`
- :doc:`normalization-contracts`
- :doc:`capability-contracts`
- :doc:`interoperability-error-semantics`
