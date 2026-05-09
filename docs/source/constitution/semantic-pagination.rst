Semantic pagination constitution
==================================

Preamble
--------

Pagination is a **first-class semantic primitive**: it defines how **resource collections** are traversed lawfully—**not** a per-endpoint afterthought. Foundational truth requires that **continuation and ordering** be honest: callers must know what “next page” **means** for this binding.

Scope
-----

This chapter governs **semantic** pagination—concepts, guarantees, and opacity rules. It does **not** specify URL patterns, client iterators, or storage.

Pagination as semantic traversal
--------------------------------

**Traversal** is the strategy-bounded act of walking a **collection** of resources (or events) under declared **ordering** and **continuation** rules. Pagination encodes **how** traversal advances and **when** it ends.

Opaque cursor semantics
-----------------------

**Opaque cursors** encapsulate provider-specific continuation state. **Canonical** continuations are **opaque to callers** when required to preserve vendor invariants; **diagnostics** of provider tokens belong in **provenance or debug channels**, not in canonical identity fields.

**C1 — Opacity with law**
   Opaqueness must not prevent **integrity**: ordering family and stability class must still be **declared** at the capability level.

Continuation semantics
----------------------

**Continuation** answers: *given a page, what is the lawful next page token, and is there a next page?* **Dead ends** and **gaps** (e.g., deletions between pages) must be classified per strategy: **eventual** vs **strong** list stability, if modeled at all.

Traversal guarantees
--------------------

Guarantees are **binding-local** and **resource-scoped**. The constitution **does not** require global cross-provider alignment of pages.

**T1 — Deterministic traversal under declared stability class**
   For a fixed cursor and unchanged remote state per the stability class, the **next** page is deterministic.

**T2 — No hidden cross-provider order**
   Core does not define a **global** merge order across providers; that is **non-core** territory.

Ordering guarantees
-------------------

**Ordering family** (e.g., time-descending, id-ascending, relevance with stated approximate semantics) is a **capability** and **strategy** matter. **Naive offset/limit** is not a universal primitive; where offsets are dishonest, they must not be the **only** exposed model.

Snapshot vs incremental semantics
----------------------------------

**Snapshot** traversal: a logical view of a collection as of a **cursor snapshot class** (strategy-defined). **Incremental** traversal: **delta** or **change feeds** with their own ordering and cursor rules. The two are **not** interchangeable; capabilities must declare which family applies.

Pagination integrity
--------------------

**PI-1 — Semantic ordering visibility**
   Callers can discover which ordering modes exist for a resource family on this binding.

**PI-2 — Continuation integrity**
   Lawful cursors do not “skip” in undeclared ways; **jumps** or **reorders** are either **impossible** (error) or **declared** (e.g., approximate feeds).

**PI-3 — Provider adaptation without truth leakage**
   Adapters map vendor pagination into canonical continuation envelopes **without** exposing vendor tokens as canonical identifiers unless the strategy explicitly permits **that encoding**.

Why naive offset assumptions fail
---------------------------------

Many APIs break offset pagination under concurrency, deletion, or relevance reordering. Constitutional pagination favors **explicit** continuation models and **declared** stability classes.

Constitutional constraints
--------------------------

**PG-1 — Pagination is resource-scoped**
   Continuation tokens are meaningful within their **collection scope** (strategy-defined), not as global strings.

**PG-2 — Provider-aware, canonical-shaped**
   Vendor mechanics remain behind envelopes; **canonical** exposes lawful continuation **shape**.

**PG-3 — No silent weakening**
   If only weaker ordering/stability is available than requested, outcome must be **degraded explicitly** or rejected—see :doc:`partiality-projection`.

Related chapters
----------------

- :doc:`semantic-primitives`  
- :doc:`capability-contracts`  
- :doc:`provider-adapters`  
