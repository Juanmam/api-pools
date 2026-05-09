Interoperability error constitution
=====================================

Preamble
--------

**Interoperability errors** are **first-class semantic outcomes** when **strategy obligations**, **capability offers**, **normalization targets**, or **partiality floors** cannot be satisfied. They are **not** generic failures and **must not** be conflated with **execution failures**.

Foundational truth: incompatibility must be **explicit and computable**.

Failure partitions
------------------

**Execution failures**
   Transport and runtime substrate: timeouts, connection resets, TLS handshakes, raw rate-limit signals **as received**, process limits—**unless** the framework elevates specific signals to semantic categories by explicit policy.

**Interoperability failures (semantic)**
   Intent cannot be satisfied lawfully; mapping cannot commit honestly; versions mismatch; capability ceiling breached; partiality floor violated; silent degradation would have occurred.

Conflation risk
----------------

If semantic failures masquerade as “try again,” operators chase outages while the real issue is **misconfiguration or inevitable incompatibility**. If execution failures masquerade as semantic, clients stop retrying recoverable faults.

Conceptual taxonomy (semantic)
------------------------------

Categories are **law vocabulary**; concrete exception types are implementation artifacts.

**Capability mismatch**
   Intent exceeds declared offers (operation shape, projection, pagination mode, auth prerequisites).

**Unsupported semantics**
   Strategy-defined construct absent from this binding.

**Schema or canonical version incompatibility**
   Requested canonical output not certified by adapter targets; provider revision drifts from claimed mapping without contract update.

**Normalization failure**
   Deterministic mapping cannot yield lawful canonical output—contradiction, unmappable state, invariant clash.

**Partial-compatibility floor violation**
   Partial path attempted but cannot meet **minimum completeness** declared by strategy.

**Semantic degradation violation**
   Outcome would require silent weakening relative to requested semantics—**disallowed**; must surface as structured failure or lawful explicit degraded success per policy.

**Integrity violations**
   Attempts to return outcomes that violate primitive distinctions (:doc:`partiality-projection`) or normalization purity (:doc:`normalization`).

Computable incompatibility philosophy
-------------------------------------

Categories must be **machine-actionable**: narrow projection, change scopes, pick alternate bindings in **optional** layers, or halt. **Opaque“ERROR” strings are constitutional debt.**

Observability rules
-------------------

**IE-1 — Explicit categories**
   Semantic failures carry discriminated categories independent of wire format.

**IE-2 — Degradation visibility**
   Where degraded success is lawful, residual semantics are **explicit**—never ambiguous absence.

**IE-3 — Retry semantics clarity**
   Outer execution envelope may indicate transport retryability; inner semantic outcome indicates whether retrying **the same intent** is futile.

**IE-4 — Causal layering**
   Semantic failure may wrap execution causes **as context** without losing category identity.

Lawful failure semantics
------------------------

Failures are **lawful** when they **preserve**: primitive distinctions, capability honesty, and deterministic mapping posture.

Interoperability truths that MUST NOT be hidden
-------------------------------------------------

- Unsupported facets  
- Incompatible canonical targets  
- Unmappable provider states  
- Partial results presented as full  
- Ordering/stability weaker than requested **without** degraded classification  

Related chapters
----------------

- :doc:`semantic-primitives`  
- :doc:`capability-contracts`  
- :doc:`partiality-projection`  
- :doc:`normalization`  
