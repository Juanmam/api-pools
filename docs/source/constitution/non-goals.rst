Non-goals constitution
======================

Preamble
--------

This chapter is **constitutional exclusion**. API Pools’ **core identity** is **semantic interoperability** with **explicit incompatibility**. The following systems are **not** core concerns. Their absence from core is **law**, not a temporary gap.

**They MAY exist later as optional, separately bounded modules** that **depend on** core contracts—and **must never** be depended upon by core.

Excluded from core (non-exhaustive)
------------------------------------

**Orchestration engines**
   Multi-step semantic workflows across calls/providers—**non-core**.

**Federation systems**
   Unified query or graph across heterogeneous sources—**non-core**.

**Distributed planners**
   Global optimization across providers, budgets, and execution graphs—**non-core**.

**Workflow runtimes**
   Long-running orchestrated processes—**non-core**.

**ETL platforms**
   Bulk extraction/transform/load pipelines as a product surface—**non-core**.

**Identity graph systems**
   Cross-provider entity resolution, confidence scoring, merge graphs—**non-core**.

**Merge engines**
   Reconciling competing records into synthetic truths—**non-core**.

**Universal canonical models**
   Cross-domain mega-schemas—**constitutionally rejected** in core (:doc:`canonical-resources`).

Why exclusion matters
---------------------

**Attractive complexity** migrates into core through “small helpers.” These domains carry **different correctness criteria** (eventual consistency, CRDTs, planner SLOs) that **corrupt** semantic law if allowed to penetrate adapters or runtime.

Optional futures without contamination
--------------------------------------

Optional modules may:

- Consume **canonical ports** and **capability contracts**.  
- Compose **multiple bindings** at the **application** or **extension** tier.  
- Implement planners **outside** core packages—**never** inside provider adapters.

Bounded architecture
--------------------

Boundedness keeps **semantic truth** maintainable. **Core** answers: *what does this mean for one binding under declared contracts?* **Everything else** composes **above**.

Related chapters
----------------

- :doc:`dependency-boundaries`  
- :doc:`provider-adapters`  
- :doc:`adr-index`  
