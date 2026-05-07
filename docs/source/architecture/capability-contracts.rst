Capability contracts
====================

Purpose
-------

This document defines **capability contracts**: what capabilities represent in API Pools, how they differ from informal feature flags, and how typing, constraints, compatibility, and partial support are modeled **without** prescribing orchestration or concrete serialization.

What capabilities represent
---------------------------

**Capabilities** are **declarative behavioral contracts** that describe what a **provider semantic adapter** can do **under stated constraints** relative to a **strategy contract** and **canonical resources**.

Capabilities answer questions such as:

- Which **resource kinds** and **operation shapes** (retrieve, list, stream, mutate) are supported?
- Which **projections** or **facets** of a resource can be populated?
- Which **pagination modes** and **ordering** semantics are available?
- Which **canonical normalization targets** (version bands) are satisfied for those projections?
- What **authentication modes** or **scopes** are prerequisites?

Capabilities are **more than documentation**: they are inputs to **validation**—whether a requested operation is even **legal** for this binding.

Capability typing
-----------------

**Typing** means capabilities are not arbitrary string tags. They belong to a **structured vocabulary** aligned with strategy semantics:

- **Resource-scoped** capabilities (e.g., list posts with a defined ordering family).
- **Operation-scoped** capabilities (e.g., stream vs poll).
- **Constraint parameters** (limits, maximum page sizes, required filters).

Typing enables:

- **Static reasoning** before execution.
- **Composable policies** without “stringly-typed” configuration drift.

Exact type systems are an implementation concern; architecturally, **capabilities must be discriminable and comparable** for compatibility checks.

Capability constraints
----------------------

**Constraints** narrow or parameterize behavior:

- Numeric bounds (page size caps).
- Required inputs (mandatory time window for auditability).
- Mutually exclusive modes (cursor vs offset where both cannot be honest).

Constraints are part of the contract: violating them is a **capability mismatch**, not an adapter bug.

Compatibility semantics
-----------------------

**Compatibility** is the relation between **caller intent** (a requested operation + projection + pagination + canonical version expectations) and **provider offers** (declared capabilities).

Modes include:

- **Full compatibility** — intent satisfied within invariants.
- **Partial compatibility** — strict subset success with explicit **gap** reporting.
- **Incompatibility** — no lawful execution path; must fail without silent downgrade.

Compatibility is **computable**: it reduces to rule evaluation over typed offers and requests, not informal judgement calls at runtime.

Partial compatibility
---------------------

**Partial compatibility** is an explicit outcome: the adapter can honor **part** of the intent **by contract**:

- Reduced projection.
- Narrower pagination guarantees.
- Deferred facets that require different operations.

Partiality **must not** masquerade as full success. Strategies define how **residual gaps** are surfaced (see interoperability errors).

Unsupported semantics
---------------------

**Unsupported** means: the strategy defines a construct, but this provider binding does not offer it. This differs from “error” in the transport sense—it is a **semantic absence** known at declaration or discovered at validation time.

Unsupported semantics must be **first-class** in reporting so callers do not infer support from silence.

Declarative behavioral contracts
--------------------------------

Capabilities behave as **contracts** because they imply **obligations** when execution proceeds:

- If listed as supported, behavior must conform to strategy semantics for that slice.
- If not listed, operations requiring them must be rejected or narrowed **explicitly**.

This is stricter than marketing-style feature lists and richer than boolean flags.

Why capabilities are more than metadata
---------------------------------------

**Metadata** describes; **contracts** bind.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Metadata mindset
     - Contract mindset
   * - Informative tags
     - Preconditions and offers
   * - Optional checks
     - Validation gates
   * - Docs drift
     - Typed, evolvable surface

Capabilities anchor **honest interoperability**: they align declared possibility with **lawful behavior**.

Feature flags vs behavioral contracts
-----------------------------------

**Feature flags** typically toggle code paths opaquely. **Behavioral contracts**:

- Are **scoped** to strategy vocabulary.
- Participate in **compatibility** evaluation.
- Tie to **normalization targets** and **error taxonomy**.

Flags may exist internally; architecturally, externalized capability surfaces should remain **semantic**, not arbitrary toggles.

Capability validation
---------------------

**Validation** occurs at boundaries:

- **Bind time** — assembling a provider with credentials and configuration.
- **Request time** — evaluating caller intent against offers.
- **Post-execution** — verifying outputs satisfy declared slices where checkable (where strategies define observable criteria).

Validation prevents **silent entry** into unsupported semantic territory.

Compatibility guarantees and explicit degradation
-------------------------------------------------

When degradation is allowed by strategy policy:

- It is **named** (partial projection, weaker ordering).
- It is **attributed** (why the gap exists).
- It remains **auditable** in logs and structured results where applicable.

**Silent** degradation—returning incomplete data as if complete—is an interoperability anti-pattern.

Future-facing considerations (without designing orchestration)
-------------------------------------------------------------

Capabilities are intentionally shaped so that **later** they can feed:

- **Negotiation** — selecting among multiple offers (still a separate layer).
- **Planning** — ordering operations under budgets (not core).
- **Routing hints** — prefer paths with required facets (execution policy, not strategy semantics).

These futures **reuse the same contract objects** as inputs; core remains **declarative validation and honesty**, not a planner.

**Boundary rule:** core defines **what capabilities mean** and **how compatibility is evaluated** for a single binding; **multi-provider selection** lives in optional modules.

Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 36 64

   * - Concept
     - Definition
   * - Capability
     - Typed declarative offer + constraints relative to strategy
   * - Compatibility
     - Computable relation between intent and offers
   * - Partial compatibility
     - Explicit subset success with gap semantics
   * - Validation
     - Gatekeeping at bind and request boundaries

Related documents
-----------------

- :doc:`strategy-contracts`
- :doc:`canonical-resource-system`
- :doc:`normalization-contracts`
- :doc:`interoperability-error-semantics`
