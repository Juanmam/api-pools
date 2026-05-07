Strategy contracts
==================

Purpose
-------

This document defines **strategy contracts**: bounded semantic contexts in which canonical resources live, what lawful behavior means, and how strategies differ from transport-oriented or provider-centric “service APIs.”

It remains **conceptual**—no concrete operation signatures, protocol definitions, or class hierarchies.

What a strategy contract is
---------------------------

A **strategy contract** is the **semantic constitution** for a domain family of heterogeneous APIs (e.g., social surfaces, payments, messaging). It specifies:

- **Which canonical resource kinds exist** in this strategy and how they relate (ontology).
- **What operations are meaningful** at the resource boundary: lawful reads, writes, streams, and queries **expressed in domain terms**, not HTTP verbs.
- **Semantic guarantees and non-guarantees**: what callers may assume when a provider declares compatibility, and what remains vendor-specific.
- **Interoperability obligations** for adapters: fidelity expectations, explicit limits, and how gaps surface (via capabilities and errors).

A strategy contract is **not** a catalog of REST endpoints and **not** a wrapper around a particular SDK.

Bounded semantic contexts
-------------------------

Each strategy is a **bounded context**: a closed vocabulary with its own ubiquitous language.

**Why boundaries matter:**

- Prevents **semantic leakage**—payment “authorization” language polluting messaging models.
- Keeps **evolution tractable**—schemas and capabilities evolve within a strategy without dragging unrelated domains.
- Makes **compatibility** computable within the strategy’s rules.

Cross-strategy composition belongs **outside** core strategy definitions—in applications or optional modules—not inside a unified mega-strategy.

Semantic guarantees
-------------------

**Guarantees** are promises about canonical behavior **when** declared capabilities are satisfied. Classes of guarantees include:

- **Structural** — certain projections and relationships are available as claimed.
- **Ordering** — list/stream operations honor declared ordering semantics where applicable.
- **Consistency** — read-after-write expectations within stated bounds (strategy-specific; not a distributed systems manifesto unless explicitly modeled).

**Non-guarantees** must be equally explicit: strategies document what adapters **need not** unify (e.g., vendor-specific moderation states) except through extensions or optional facets.

Resource-scoped operations
--------------------------

Operations are **anchored to resources** and collections:

- Retrieve a resource by canonical identity.
- List or stream resources under collection semantics (feeds, threads, ledgers).
- Mutations that transition lifecycle states where in scope.

This avoids an unbounded flat namespace of verbs and encourages **shared pagination, projection, and error semantics** per resource family.

Lawful behavior
---------------

**Lawful behavior** means: given declared capabilities, adapter outputs conform to strategy invariants and normalization targets—or fail with explicit interoperability errors.

Lawfulness applies to:

- **Outputs** — canonical instances respect ontology and requested projections within capability.
- **Operation semantics** — idempotency expectations, pagination continuity, and error conditions are strategy-defined.

Unlawful outputs are not “best effort truth”; they are **failures** or **explicit partial results** per contract rules.

Provider obligations
--------------------

Under a strategy contract, a **provider semantic adapter** obligates itself to:

- **Declare** what it supports via capability contracts (resources, operations, projections, pagination modes, canonical versions).
- **Normalize** provider truth to declared canonical targets without silent semantic substitution.
- **Surface** incompatibility when requests exceed declared capability or cannot be mapped deterministically.

Obligations are **semantic**, not “always success.” A healthy adapter fails clearly.

Domain-specific semantics
-------------------------

Strategies embrace **real domain differences**:

- Payments expose charges, refunds, disputes; messaging exposes threads and delivery states.
- **Domain language belongs in the strategy**, not diluted to generic records.

This is why strategies are **semantic contracts**, not interchangeable transports.

Strategies as semantic contracts, not service wrappers
--------------------------------------------------------

**Service wrapper** thinking maps one vendor’s API shape to callers. **Strategy contract** thinking maps **many vendors** to a **shared domain semantics** with explicit variance.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Wrapper mindset
     - Strategy contract mindset
   * - Endpoint parity
     - Resource and operation lawfulness
   * - Pass-through errors
     - Interoperability error taxonomy
   * - Implicit “best effort”
     - Declared capability + explicit gaps

Relationship to canonical resources
-----------------------------------

**Canonical resources** are the **nouns**; **strategy contracts** are the **grammar and jurisprudence**: what those nouns mean, how they combine, and what is illegal.

- Resources without strategies drift into schema soup.
- Strategies without canonical anchors become hollow process diagrams.

The **minimum coherent core** requires both, plus **provider semantic adapters** as the bridge from foreign APIs.

Transport-agnostic strategies
-----------------------------

Strategy contracts **must not** depend on HTTP vs gRPC vs queues. Transport belongs to the **execution domain**:

- Strategies define **what** is requested and **what** canonical outcomes mean.
- Execution defines **how** bytes move and credentials attach.

Coupling strategy to transport invites **accidental retrofitting** of vendor networking models into domain semantics.

Deep inheritance danger
-----------------------

Modeling strategies as **deep class hierarchies** (e.g., ``BaseStrategy → SocialStrategy → VideoStrategy → ShortVideoStrategy``) tends to:

- Encode **orthogonal concerns** (pagination, auth modes) as layered overrides.
- Create **fragile diamond** situations when capabilities do not compose along the same axes.

**Preferred stance:**

- **Shallow** taxonomies where inheritance is rare and meaningful.
- **Composition** of capability bundles, policy objects, and adapter traits **without** implying a single inheritance tree mirrors reality.

Composition vs inheritance
--------------------------

- **Composition** groups capabilities, constraints, and behavioral profiles **without** implying subtype substitution across unrelated vendors.
- **Inheritance** should be reserved for **true semantic specialization** with stable rules—not for sharing HTTP helpers.

Semantic boundaries and interoperability constraints
----------------------------------------------------

Interoperability is **bounded**: strategies define **where** heterogeneity ends and explicit variance begins. Constraints include:

- **No silent expansion** of canonical meaning to absorb vendor quirks.
- **Explicit extensions** for vendor-only facets when needed.
- **Version discipline** on canonical resources referenced by the strategy.

Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Concept
     - Definition
   * - Strategy contract
     - Bounded semantic constitution for a domain family
   * - Bounded context
     - Closed ontology and language per strategy
   * - Lawful behavior
     - Conformance or explicit failure under declared capability
   * - Provider obligations
     - Declare, map honestly, fail explicitly

Related documents
-----------------

- :doc:`canonical-resource-system`
- :doc:`capability-contracts`
- :doc:`normalization-contracts`
- :doc:`interoperability-error-semantics`
