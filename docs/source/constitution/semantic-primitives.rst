Semantic primitives constitution
==================================

Preamble
--------

**Foundational truth:** API Pools standardizes what “the same thing” means across vendors while making incompatibility **explicit and computable**. Semantic primitives are the **smallest units of shared meaning** that make that truth enforceable. If primitives are vague, every higher layer—resources, capabilities, pagination, normalization—becomes an exercise in opinionated defaults and silent drift.

Scope
-----

This chapter defines **categories of meaning** and **constitutional rules**. It does **not** define concrete field schemas, wire formats, or type systems.

Primitive families
------------------

**Identity semantics**
   Rules for how a **canonical** resource instance is denoted and distinguished **within canonical space**: stability properties, structure vs opacity, and lawful reference under declared projections. **Provider-native keys** and transport handles are not canonical identity; adapters **map** them. Core defines what identity **means** for interoperability, not how vendors name rows.

**Canonical references**
   First-class relations between resources in the ontology: edges with declared cardinality, ownership or association, and **navigability** (which traversals are contractually meaningful). A reference is not a URL unless a strategy **explicitly** elevates a URL-shaped identifier to canonical status (generally discouraged).

**Projection semantics**
   The **intended** subset of a resource’s semantics for an operation: which facets are in scope. Projection is **declared intent**, not an accident of sparse payloads.

**Partiality semantics**
   Lawful distinctions among states of incompleteness—see :doc:`partiality-projection`. This primitive family is **constitutionally required**; conflating categories is a defect.

**Provenance semantics**
   **Annotations** describing origin and retrieval context (binding, provider revision class, modality, approximate timestamps) **without** substituting for domain fields or repairing semantic gaps.

**Canonical relationships**
   Ontological graph structure governing lawful queries (e.g., parent/child collection scoping for traversal).

**Semantic integrity**
   Conditions under which an instance **validly** represents a resource for a given projection and capability slice—referential coherence, lifecycle lawfulness, and strategy invariants **as declared**.

**Lifecycle visibility**
   Which states exist and how list/read surfaces include or exclude them—**strategy-defined**. Transport must not define lifecycle.

**Semantic consistency expectations**
   Strategy-local promises where modeled: ordering families for lists, acceptable staleness language, read-after-write windows. **Not** implicit distributed guarantees unless named.

Why primitives are foundational
--------------------------------

Primitives appear in **every** constitutional chapter:

- **Canonical resources** instantiate identity and relationships.
- **Capability contracts** express offers in terms of projections and compatibility modes built from primitive distinctions.
- **Pagination** composes ordering and continuation primitives.
- **Normalization** must preserve primitive distinctions; it may not collapse “unsupported” into “null.”
- **Interoperability errors** name **which primitive obligation** failed.

Inconsistent primitives produce **non-computable interoperability**: callers cannot decide whether to narrow intent, change bindings, or treat outcomes as retryable.

Existential risk of inconsistent meaning
-----------------------------------------

When “missing,” “unsupported,” and “unknown” are interchangeable, integrations infer behavior from **absence patterns**—the most unstable signal across vendors. When identity conflates unrelated notions, downstream systems build **false joins**. When provenance is omitted, audit and debugging collapse into speculation.

How primitives constrain the framework
-----------------------------------------

Primitives act as **semantic conservation laws**: adapters may translate, narrow, or fail—but they may not ** silently rewrite** primitive categories to satisfy ergonomics.

Constitutional rules
----------------------

**SP-1 — Semantic determinism**
   For a declared normalization target, capability slice, and wire context class, semantic translation outcomes must be **deterministic**: either a lawful canonical outcome or a **determinate class** of structured interoperability failure. Accidental randomness, implicit time-based defaults **inside** semantic translation, or hidden nondeterminism are **violations** unless a strategy explicitly defines a stochastic domain (rare; must be named).

**SP-2 — Identity integrity**
   Canonical identifiers and references must not be **fabricated** or **conflated** to hide incompatibility. Cross-provider “sameness” is **not** a core primitive.

**SP-3 — Semantic visibility**
   Material distinctions (especially partiality) must be **observable**—in structured results or structured failures—not recoverable only by convention or documentation archaeology.

**SP-4 — Canonical meaning preservation**
   Meaning moves only through **governed evolution** (:doc:`canonical-versioning`) and explicit contracts—not through adapter convenience.

Related chapters
----------------

- :doc:`partiality-projection`  
- :doc:`canonical-resources`  
- :doc:`interoperability-errors`  
