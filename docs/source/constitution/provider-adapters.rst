Provider semantic adapter constitution
========================================

Preamble
--------

**Provider semantic adapters** translate **provider truth** into **canonical commitments** offered by **capability contracts** and **normalization targets**. They sit at the boundary between foreign APIs and core semantics.

Adapters are **not** miniature orchestrators, **not** federation engines, and **not** authorities on cross-provider identity.

Lawful responsibilities (MAY)
------------------------------

**A-MAY-1 — Translate semantics**
   Map wire-domain representations to canonical outcomes **deterministically** under declared rules.

**A-MAY-2 — Expose limitations**
   Surface unsupported facets, weaker pagination modes, or incompatible targets via **capabilities** and **structured outcomes**.

**A-MAY-3 — Adapt pagination**
   Encode vendor continuation into **canonical continuation envelopes** without leaking vendor tokens into canonical identity unless strategy explicitly permits.

**A-MAY-4 — Map canonical meaning faithfully**
   Produce instances that satisfy declared projections—or refuse lawfully.

**A-MAY-5 — Attach provenance**
   Add non-domain annotations describing retrieval context per strategy rules.

**A-MAY-6 — Decode safely**
   Perform syntactic decoding **adjacent** to normalization, preserving separation of wire shapes from canonical types.

Prohibited behaviors (MUST NEVER)
---------------------------------

**A-NOT-1 — Orchestrate providers**
   No multi-provider fan-out, merging timelines, or coordinated scheduling **inside** adapters.

**A-NOT-2 — Merge semantic truths**
   No reconciling competing meanings across vendors or accounts into a “best” canonical object in core.

**A-NOT-3 — Hide incompatibilities**
   No translating **unsupported** into **empty**, **default**, or “soft null.”

**A-NOT-4 — Semantic guessing**
   No inventing business meaning to satisfy schemas—see :doc:`partiality-projection`.

**A-NOT-5 — Absorb orchestration intelligence**
   No embedding planners, policy engines, or cross-request learning that decides **what** to call **when** for multi-step semantic goals.

**A-NOT-6 — Implicit federation**
   No stitching graphs across vendors **within** the adapter boundary.

**A-NOT-7 — Non-deterministic normalization**
   No hidden randomness or time-dependent semantic defaults inside mapping cores.

**A-NOT-8 — Normalize with I/O**
   Violates :doc:`normalization` purity.

Deterministic adaptation
------------------------

Adapters must make **the same** lawful choice at semantic fork points given the same inputs and declared contexts.

Provider limitation visibility
------------------------------

Limitations appear in **declared capabilities** and **lawful failures**—not only logs.

Semantic boundary enforcement
-------------------------------

Adapters **stop** at canonical commitments. **Cross-resource synthesis** beyond provider truth belongs to higher layers—explicitly **non-core** when it resembles orchestration or federation.

Related chapters
----------------

- :doc:`normalization`  
- :doc:`capability-contracts`  
- :doc:`dependency-boundaries`  
- :doc:`non-goals`  
