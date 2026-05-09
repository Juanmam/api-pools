Canonical resources constitution
==================================

Preamble
--------

Canonical resources are the **semantic center** of API Pools: the **stable vocabulary** of entities and relationships within a **bounded strategy**. They answer: *what do we call “the same thing,” and what do we refuse to pretend is the same?*

This chapter defines **philosophy, boundaries, invariants, and evolution constraints**—not concrete resource types or field lists.

Philosophy
----------

**Resource-centric semantics.** Operations attach to **what exists** in the ontology and what **lawful queries** mean for those resources—rather than an unbounded verb list whose payloads drift independently.

**Bounded truth.** Canonical resources are **not** rows in a universal enterprise model spanning unrelated domains. Each strategy owns its ontology; **reuse of names** across strategies is informal and must not force structural merging.

**Interoperability target.** Normalization **targets** canonical instances; capabilities **scope** what can be truthfully populated.

Ontology boundaries
-------------------

An **ontology** declares resource kinds, relationships, cardinalities, and **which traversals** are meaningful. Ontology is **strategy-local**. Expansion requires explicit governance—see constraints below.

Bounded semantic contexts
-------------------------

API Pools treats each **strategy** as a **bounded context** (DDD): a closed ubiquitous language. Social, payment, and messaging strategies **must not** be welded into one mega-schema “for reuse.” Cross-context integration belongs in **application or optional extension layers**, not in core canonical definitions.

Invariants
----------

**Invariant** means: under declared **full** compatibility for a capability slice, instances satisfy strategy rules (examples of **classes**, not specific fields):

- **Referential integrity** under the projection: references resolve or the instance is unlawful for that projection.
- **Lifecycle lawfulness**: states combine consistently with list/read visibility rules.
- **Temporal ordering** where time is domain-relevant: ordering rules are explicit for collection operations.

Invariants may be **relaxed** only when partial compatibility is **declared**—never implicitly.

Resource identity
-----------------

**Canonical identity** is defined by strategy rules for references within canonical space. **Provider-native identifiers** are mapped by adapters and **must not** silently become canonical unless the contract says so.

Lawful resource semantics
-------------------------

Lawfulness is **triangulated**: strategy contract + capability offers + normalization targets. Outputs are **lawful**, **lawfully partial**, or **failures**—not “best-effort” ambiguity.

Projection rules
----------------

Projections are **named or typed intent**. Capability contracts bind which projections a binding can supply. Projections are governed by :doc:`partiality-projection`.

Semantic ownership
------------------

**Strategies own** domain meaning for their resources. **Adapters own** faithful translation and explicit limitation. **Execution owns** how bytes move. **Normalization** maps wire-domain outcomes to canonical targets but **does not own** domain vocabulary.

Why canonical resources are the semantic center
-----------------------------------------------

Without them, “normalization” devolves into formatting; without bounded contexts, “canonical” devolves into a dishonest universal model.

Risks of universal model creep
------------------------------

- Collapsing domains into one ``User``/``Account`` type forces **dishonest** mappings.
- Coupling unrelated release cycles into one evolving mega-schema **amplifies** breaking change blast radius.

Constitutional constraints
--------------------------

**CR-1 — Strategy locality**
   New resource kinds and relationships are introduced **inside** a strategy’s governance process; they do not appear by cross-import from unrelated strategies.

**CR-2 — Explicit evolution**
   Semantic evolution follows :doc:`canonical-versioning`. Breaking meaning requires governed transitions—not silent reinterpretation.

**CR-3 — No covert ontology merges**
   “Compatibility shims” that silently unify heterogeneous domains are **disallowed** in core; explicit anti-corruption boundaries are required at edges.

**CR-4 — Cross-strategy boundaries**
   Core canonical types **must not** depend on types from another strategy’s ontology. Application-level correlation is permitted **outside** core.

Related chapters
----------------

- :doc:`semantic-primitives`  
- :doc:`capability-contracts`  
- :doc:`canonical-versioning`  
