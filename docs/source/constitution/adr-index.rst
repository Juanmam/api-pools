Architecture Decision Records — index
=======================================

Preamble
--------

**ADRs** record **irreversible or high-cost** decisions, **rejected alternatives**, and the **risks** each decision is designed to prevent. This index proposes **foundational** ADRs to author next; **full ADR bodies are intentionally out of scope** here.

How to read this index
----------------------

For each item: **title**, **purpose**, **architectural motivation**, **risks prevented**.

Proposed foundational ADRs
--------------------------

**ADR-001 — Semantic interoperability over wrapper ergonomics**
   **Purpose:** Lock the product identity as **meaning-first** interoperability, not transport sugar.
   **Motivation:** Prevents the framework from becoming a **veneer** that obscures vendor divergence.
   **Risks prevented:** Accidental positioning as a generic client; silent acceptance of dishonest “unified” objects.

**ADR-002 — Canonical resource-centered architecture**
   **Purpose:** Establish **resources + strategies + adapters** as the minimum coherent core.
   **Motivation:** Stabilizes ontology, queries, and errors around **nouns** and **lawful operations**.
   **Risks prevented:** Operation-soup APIs; duplicated pagination/error semantics per verb.

**ADR-003 — Capabilities as contracts**
   **Purpose:** Elevate capabilities from metadata to **typed behavioral offers**.
   **Motivation:** Makes compatibility **computable** and failures **honest**.
   **Risks prevented:** Stringly-typed features; impossible-to-automate compatibility checks.

**ADR-004 — Normalization purity and determinism**
   **Purpose:** Forbid I/O and nondeterminism inside semantic translation cores.
   **Motivation:** Separates **semantic** from **operational** failure; enables auditable mapping.
   **Risks prevented:** Flaky tests; guesswork masked as mapping; entangled retries.

**ADR-005 — Pagination as semantic primitive**
   **Purpose:** Treat continuation and ordering as **resource-access law**, not per-endpoint trivia.
   **Motivation:** Aligns heterogeneous vendor pagination behind explicit stability classes.
   **Risks prevented:** Offset assumptions; hidden vendor tokens as canonical state.

**ADR-006 — Explicit incompatibility philosophy**
   **Purpose:** Encode **first-class** interoperability failures distinct from execution failures.
   **Motivation:** Operators and automation must see **misconfiguration vs outage** clearly.
   **Risks prevented:** Masked mismatch; retry storms on futile intents.

**ADR-007 — Orchestration as non-core**
   **Purpose:** Exclude planners/federation from core dependency surface.
   **Motivation:** Preserves **semantic clarity** and prevents runtime god-objects.
   **Risks prevented:** Orchestration creep; core imports of coordination engines.

**ADR-008 — Rejection of universal canonical models**
   **Purpose:** Forbid cross-domain mega-schemas in core.
   **Motivation:** Bounded contexts remain honest; anti-corruption stays at edges.
   **Risks prevented:** Dishonest joins; unbounded breaking-change blast radius.

**ADR-009 — Deterministic normalization**
   **Purpose:** Require deterministic outcomes/failure classes for declared mapping contexts.
   **Motivation:** Reproducibility and contract testing for semantic paths.
   **Risks prevented:** “Works sometimes” mappings; production nondeterminism.

**ADR-010 — Provider adapter boundaries**
   **Purpose:** Codify **MAY / MUST NEVER** for adapters (:doc:`provider-adapters`).
   **Motivation:** Stops adapters from becoming mini-federations or guessers.
   **Risks prevented:** Cross-provider merges; hidden incompatibility; planner leakage.

**ADR-011 — Partiality primitive distinctions**
   **Purpose:** Encode missing vs unsupported vs unknown vs unmappable as **non-interchangeable**.
   **Motivation:** Prevents existential ambiguity in downstream logic.
   **Risks prevented:** Silent degradation; compliance and analytics false negatives; existential ambiguity in automation.

**ADR-012 — Canonical versioning governance**
   **Purpose:** Require explicit targets and governed transitions for semantic change.
   **Motivation:** Prevents silent drift of meaning across releases.
   **Risks prevented:** Breaking semantics under stable labels; uncertified adapters.

Future ADRs (examples)
----------------------

- Capability negotiation vs static matching (when negotiation graduates from flags).  
- Consistency classes for list staleness (strategy-local).  
- Provenance depth vs lineage platform boundary.

Related chapters
----------------

- :doc:`dependency-boundaries`  
- :doc:`non-goals`  
