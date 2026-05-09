Normalization constitution
============================

Preamble
--------

**Normalization** is **deterministic semantic translation** from provider-grounded representations to **versioned canonical** resource semantics under declared capability slices. It is the hinge between **provider truth** and **canonical truth**.

Foundational truth demands **honesty**: when translation cannot commit without guessing, the outcome is **structured incompatibility**—not plausible fabrication.

Normalization philosophy
------------------------

Normalization **commits** to meaning—or refuses. It is **not** cosmetic JSON cleanup, **not** “best effort shape casting,” and **not** a place to hide vendor quirks behind canonical fields.

Provider truth vs canonical truth
---------------------------------

**Provider truth:** what the vendor’s API asserts—payloads, codes, implicit conventions.

**Canonical truth:** what API Pools commits downstream **for interoperability** under a **normalization target** (canonical version band and strategy interpretation).

**Law:** Provider truth remains authoritative for **vendor-local** facts outside canonical scope. Canonical truth is authoritative **within** the declared normalization contract.

Deterministic semantic translation
----------------------------------

Given the same inputs—decoded wire context class, declared API revision context, capability slice, normalization target—translation yields:

- the **same** lawful canonical outcome, or  
- the **same class** of interoperability failure.

Semantic fidelity
-----------------

Fidelity is assessed **per projection** and **capability slice**:

- **High** — conforms to expectations for that slice.  
- **Partial** — lawful degraded semantics **explicitly** surfaced.  
- **Failed** — **unmappable** without invention—must error per :doc:`interoperability-errors`.

Degradation reporting
---------------------

Any lawful degradation must align with :doc:`partiality-projection` and capability policy—**never** silent.

Normalization boundaries
------------------------

**Inside normalization (semantic):** mapping rules, value transforms, enum alignment, identity construction **as permitted** by strategy.

**Outside normalization (execution):** network I/O, token refresh, rate limiting, transport selection, retry policy application.

**N-1 — Purity**
   Normalization **must not** perform I/O or time-dependent “fill” operations. Caching remote lookups inside normalization is **void**.

**N-2 — Wire isolation**
   Canonical instances **are not** raw wire dicts; decoding is adapter-adjacent but **separate** from committing canonical meaning.

**N-3 — Determinism**
   Same inputs ⇒ same semantic outcome/failure class.

**N-4 — Version-aware targets**
   Every normalization path declares **which canonical targets** it implements; implicit “latest” without governance is **disallowed**.

**N-5 — Semantic guessing prohibition**
   Inventing currency, timezone, approval states, or identities to satisfy types is **forbidden** unless the strategy names an explicit authorized defaulting policy.

Why purity matters
------------------

Mixing I/O with semantics **entangles** transient outages with **contract falsehoods**, destroys reproducible tests, and obscures **who** is responsible: transport vs mapping vs capability lies.

Dangers of semantic guessing
------------------------------

Guessing produces **seductive green paths** in demos and **catastrophic wrongness** in production—especially in regulated or financial domains.

Normalization integrity
-----------------------

Integrity fails when mappings silently reinterpret fields across provider revisions **without** target bumps—or when missing keys become **implicit defaults**.

Canonical preservation
----------------------

Meaning evolves through **version policy** (:doc:`canonical-versioning`), not through stealth edits to “the same” canonical label.

Related chapters
----------------

- :doc:`semantic-primitives`  
- :doc:`partiality-projection`  
- :doc:`provider-adapters`  
- :doc:`dependency-boundaries`  
