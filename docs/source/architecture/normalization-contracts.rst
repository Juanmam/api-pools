Normalization contracts
=========================

Purpose
-------

This document defines **normalization contracts**: the relationship between **provider truth** and **canonical truth**, determinism, versioning, fidelity, partial projections, provenance, and evolution—**without** schemas, codecs, or mapper implementations.

Normalization semantics
-----------------------

**Normalization** is the **semantic translation** from representations grounded in a provider’s world to **canonical resource instances** governed by strategy contracts and canonical versioning.

It is **not** “making JSON pretty.” It is **committing** to specific meanings for fields, identities, and relationships—or refusing when commitment is impossible under declared rules.

Provider truth vs canonical truth
---------------------------------

**Provider truth** is what the vendor’s API asserts: payloads, codes, states, and implicit conventions.

**Canonical truth** is what API Pools commits to **downstream** after normalization: strategy meanings, invariants, and declared projections.

Core stance:

- Provider truth remains **authoritative for vendor-specific facts** that are out of scope for canonicalization.
- Canonical truth is **authoritative for interoperability** within the declared normalization target.

Adapters must not **mask** provider truth when doing so would falsify canonical commitments; they must **translate**, **narrow**, or **fail**.

Deterministic mapping
---------------------

Given the same **inputs** (wire representation, declared API version context, capability slice), normalization must be **deterministic** relative to defined rules:

- Same payload → same canonical outcome **or** same class of failure.
- No hidden randomness, network lookups, or time-dependent defaults **inside** normalization proper.

Determinism enables **testing, auditing, and reproducible incompatibility analysis**.

Version-aware normalization
---------------------------

Normalization is always tied to a **normalization target**: which **canonical version** (and strategy interpretation) the output conforms to.

**Version-aware** means:

- Provider API evolution maps to **explicit** canonical targets—not an implicit “latest.”
- Multiple targets may coexist during migrations with clear compatibility rules.

Without version awareness, silent **semantic drift** replaces breaking changes with breaking meanings.

Semantic fidelity
-----------------

**Fidelity** describes how closely a mapped instance reflects the intended canonical semantics:

- **High fidelity** — fields and invariants match expectations for the projection.
- **Partial fidelity** — some facets omitted or weaker invariants by **declared** partial compatibility.
- **Failed fidelity** — mapping would misrepresent; must error.

Fidelity is not a single scalar; it is **per projection** and **per capability slice**.

Degradation semantics
---------------------

When provider data cannot fully populate a projection:

- **Explicit omission** — absent vs unsupported vs unknown distinctions where strategy defines them.
- **No silent defaulting** that invents business meaning (e.g., assuming currency, timezone, or approval state).

Degradation aligns with **capability contracts** and **interoperability errors**, not ad hoc null handling.

Partial projections
-------------------

**Partial projections** are intentional subsets of canonical richness:

- Declared by caller intent or constrained by provider offers.
- Accompanied by **semantic completeness signals** where strategies require them—not ambiguous sparse structures.

Provenance considerations
-------------------------

**Provenance** captures **where canonical truth came from** without conflating it with canonical fields:

- Provider identity and endpoint family (conceptually—not wire URLs as canonical data).
- Provider record identifiers and versions.
- Retrieval context (batch vs single, approximate timestamps).

Provenance supports **audit, debugging, and later identity-adjacent extensions** without making core canonical resources into lineage databases.

Core principle: provenance **annotates**; it does not **replace** canonical semantics.

Why normalization must remain pure
------------------------------------

**Pure** normalization (no I/O, no side effects) yields:

- **Testability** — table-driven expectations without networks.
- **Composition** — caching and retries belong outside semantic translation.
- **Audit clarity** — failures trace to mapping rules, not transient outages.

If normalization performs I/O, semantic failures become entangled with operational failures—hurting interoperability observability.

Wire isolation
--------------

**Wire representations** (serialized payloads, vendor-specific enums) stay **outside** canonical types:

- Canonical instances should not **be** raw responses.
- Decoding is a separate concern from semantic mapping (still adapter-side, still deterministic).

Isolation prevents **accidental coupling** of downstream logic to vendor JSON layouts.

Risks of semantic drift
-----------------------

Drift occurs when:

- Canonical meaning shifts without version bumps.
- Providers change payloads but mappings silently reinterpret fields.
- Partial support is inferred from **missing keys** without declared capability.

Mitigations: **versioned canonical targets**, **explicit capability narrowing**, **structured incompatibility reporting**.

Version compatibility and schema evolution
------------------------------------------

**Evolution principles** (conceptual):

- **Additive change** preferred within a canonical major where feasible.
- **Breaking semantic change** warrants new canonical major or explicit compatibility shims with documented loss.
- **Normalization declares** which targets it implements.

Cross-version bridges—when they exist—must document **lossiness** (e.g., field narrowing).

Interoperability honesty
------------------------

Normalization contracts exist to make **honesty** the default:

- When uncertain, **fail** or **omit with explicit semantics**—not guess.
- When partial, **declare** partiality via capabilities and result metadata—not imply completeness.

Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Concept
     - Role
   * - Normalization
     - Semantic translation to versioned canonical targets
   * - Determinism
     - Reproducible outcomes or failures
   * - Purity
     - No I/O inside semantic mapping core
   * - Wire isolation
     - Vendor shapes do not leak into canonical definitions
   * - Version awareness
     - Prevents silent drift

Related documents
-----------------

- :doc:`canonical-resource-system`
- :doc:`strategy-contracts`
- :doc:`capability-contracts`
- :doc:`interoperability-error-semantics`
