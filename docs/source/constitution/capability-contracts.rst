Capability contracts constitution
===================================

Preamble
--------

**Capabilities are behavioral contracts**, not marketing labels or opaque feature toggles. They declare what a **provider semantic adapter** can truthfully do—under constraints—relative to a **strategy contract** and **canonical resources**.

Foundational truth remains: interoperability must be **explicit and computable**.

Capabilities vs feature flags
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Feature-flag mindset
     - Capability-contract mindset
   * - Opaque toggles
     - Typed offers attached to strategy vocabulary
   * - “Works on my machine”
     - Declared preconditions and postconditions for slices of behavior
   * - Informal drift
     - Validation gates at bind and request boundaries

Metadata vs contracts
---------------------

**Metadata** informs; **contracts** bind behavior when execution proceeds. Capabilities must be **discriminable and comparable** for compatibility evaluation—**not** unstructured bags of strings.

Behavioral contracts (constitutional elements)
----------------------------------------------

**Typed compatibility**
   Capabilities belong to a structured vocabulary aligned with strategies: resource kinds, operation shapes (retrieve/list/stream/mutate families), projection bands, pagination modes, normalization targets, auth prerequisites.

**Compatibility declarations**
   Each binding publishes **offers**: what combinations are supported and under which constraints (limits, required filters, mutual exclusions).

**Semantic guarantees**
   When an offer matches executed intent, outputs must conform to strategy semantics for that slice—or produce structured interoperability failures, not silent variance.

**Unsupported semantics**
   Constructs defined by the strategy that this binding does **not** implement. Unsupported is **not** the same as transient outage; it must be **visible** in declarations and validation.

**Partial compatibility**
   Intent satisfied only as a **declared subset**, with **explicit gap** reporting—never silent truncation.

**Degradation semantics**
   Where strategies permit weaker outputs, degradation is **named**, **attributed**, and **bounded by floors**—see :doc:`partiality-projection`.

**Capability validation**
   **Bind-time** and **request-time** evaluation of intent vs offers; optional **post-execution checks** where strategies define observable criteria.

Why explicit incompatibility matters
------------------------------------

Without contract-grade capabilities, systems infer support from **success patterns** and **missing keys**—the root of production dishonesty. Explicit incompatibility enables **automation and governance**: narrowing projections, changing scopes, or selecting different bindings in **optional** higher layers—without core becoming a planner.

Constitutional constraints
--------------------------

**CC-1 — Typing discipline**
   Externalized capability surfaces must remain **semantic and typed**; arbitrary dictionaries are **constitutional debt**.

**CC-2 — Declarative core**
   Core capabilities remain **declarative offers and constraints**—not executable planners. Selection among multiple providers is **non-core**.

**CC-3 — Explicit unsupportedness**
   Unsupported semantics must be representable and discoverable; absence of fields alone cannot prove support.

**CC-4 — Explicit degradation**
   Partial success must carry **residual gap** semantics when strategies require it.

**CC-5 — Compatibility computability**
   Full vs partial vs incompatible outcomes must be **evaluable** from offers and intent—not subjective runtime judgment.

Boundary with strategy contracts
--------------------------------

- **Strategy contracts** define what **may exist** and what is **lawful** in the domain language.
- **Capability contracts** define what **this binding actually offers** of that language.

Future-facing negotiation (non-design)
--------------------------------------

The same contract objects may later inform **selection among offers** or **planning** in optional modules. **Core** defines meaning and validation for **one** binding; multi-provider orchestration remains **non-core** (:doc:`non-goals`).

Related chapters
----------------

- :doc:`semantic-primitives`  
- :doc:`partiality-projection`  
- :doc:`provider-adapters`  
- :doc:`dependency-boundaries`  
