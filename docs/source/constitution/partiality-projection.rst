Partiality and projection constitution
========================================

Preamble
--------

This chapter is **constitutional law** for incomplete information. API Pools rejects **silent degradation**: weaker or partial semantic outcomes must be **lawfully visible**. If partiality categories blur, interoperability becomes **non-computable**—callers cannot distinguish “not there” from “cannot know” from “forbidden.”

Foundational truth: standardize meaning **and** make incompatibility **explicit**.

Canonical definitions
-----------------------

These terms are **orthogonal**. None may be inferred solely from another without declared rules.

**Missing**
   A facet belongs to the **requested projection** but no value is present **and** the strategy’s rules classify the absence as **permitted** under the current capability slice (e.g., optional field legitimately absent on this instance). **Missing** is not automatically **unsupported** or **unknown**.

**Unsupported**
   The strategy defines the facet, but this **binding** does not implement it for the relevant operation or projection class. Unsupported is a **compatibility** fact, not a data accident.

**Unknown**
   The binding cannot determine the facet’s value under declared rules **without** inventing meaning—e.g., vendor opacity, ambiguous wire state, or insufficient context **as defined by the strategy**. **Unknown** is **epistemic**, not a synonym for null convenience.

**Unrequested**
   The facet was **not** part of the declared projection or operation intent. Its absence is **out of scope**, not a partiality failure.

**Degraded**
   A **lawful** weaker outcome under explicit policy: partial projection, weaker ordering guarantee, or reduced pagination **integrity**—**only** when strategies permit and **residual** semantics are **declared** (see **Degradation visibility**). Degraded is **not** a silent substitute for full success.

**Unmappable**
   No deterministic mapping exists from provider truth to the requested canonical commitment without **violating invariants** or **inventing** business meaning. Unmappable demands **structured interoperability failure** (or a **lawful** alternative target **explicitly** selected), not guesswork.

**Redacted**
   A value is withheld for **policy** (permissions, legal, safety) with an explicit **redaction** signal—distinct from missing/unknown. Redaction must not be conflated with technical absence.

Why ambiguity destroys interoperability
----------------------------------------

- **Downstream logic** branches on the wrong predicate (compliance, billing, safety).  
- **Metrics** count false negatives/positives.  
- **Automation** retries futilely or masks configuration errors.  
- **Trust** in canonical semantics erodes if “null” means five different things.

Projection integrity
--------------------

**Projection** = declared intent. **Integrity** = the conjunction of:

- every facet in the projection is **lawfully present**, **lawfully marked** (unknown/redacted/optional-missing with correct category), or the operation **fails** with the correct interoperability category; and  
- **no facet outside** the projection is treated as contractually required without widening intent.

Constitutional rules
----------------------

**PP-1 — No silent degradation**
   Returning a weaker semantic outcome **without** declaring degraded/partial semantics—when the caller requested stricter semantics—is **void**. Such violations are **semantic integrity failures**.

**PP-2 — Explicit partiality visibility**
   Categories above must be representable in outputs or failures **as strategy prescribes**. Inference from absent keys alone—without capability context—is **dispreferred** and **must not** be the only mechanism when ambiguity harms safety or audit.

**PP-3 — Lawful projections**
   Widening or narrowing projections follows capability offers and caller intent; adapters **must not** silently widen to hide unsupported facets.

**PP-4 — Completeness floors**
   Where strategies define **minimum completeness** for partial paths, failure to meet the floor is a **partial-compatibility failure**—not a smaller payload.

**PP-5 — Prohibition of semantic invention**
   Defaulting business-critical values (currency, timezone, approval, identity linkage) to “reasonable” values is **guessing** and **banned** unless the strategy **explicitly** authorizes a named defaulting policy.

**PP-6 — Unmappable is not unknown**
   **Unmappable** concerns impossibility of **honest mapping**; **unknown** concerns **epistemic limits**. Collapsing them destroys debugging and contract drift detection.

Projection-constrained outcomes (conceptual)
---------------------------------------------

For any operation, lawful outcomes belong to a **small lattice**:

- **Success** (full contract satisfaction).  
- **Lawful partial/degraded success** (explicit residual semantics).  
- **Structured interoperability failure** (category-discriminated).  

**Silent** partial results pretending to be full success are **excluded**.

Risk analysis
-------------

The dominant failure mode in heterogeneous integration is **“ship a dict, hope for the best.”** This constitution **outlaws** that pattern for **declared** semantic commitments.

Related chapters
----------------

- :doc:`semantic-primitives`  
- :doc:`capability-contracts`  
- :doc:`interoperability-errors`  
- :doc:`normalization`  
