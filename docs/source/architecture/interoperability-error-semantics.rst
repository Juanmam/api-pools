Interoperability error semantics
================================

Purpose
-------

This document defines **interoperability error semantics**: failure modes that arise **at semantic boundaries**—not transport outages alone—and why these failures are first-class, structured, and essential to honest interoperability.

It does **not** define exception classes, HTTP status codes, or logging formats.

Why interoperability errors are distinct
----------------------------------------

Failures partition into:

1. **Execution failures** — timeouts, connection resets, TLS errors, rate-limit responses as raw signals.
2. **Interoperability failures** — requests or mappings cannot satisfy **strategy**, **capability**, **canonical versioning**, or **normalization** commitments.

API Pools requires **explicit treatment** of (2). Conflating (2) with (1) produces **masked incompatibility**: callers cannot distinguish “down” from “not meaningfully supported.”

Interoperability failures (conceptual categories)
-----------------------------------------------

The taxonomy is **semantic**; names may vary in implementation.

Capability mismatch
~~~~~~~~~~~~~~~~~~~

Caller intent exceeds **declared offers** for this binding:

- Unsupported resource operation shape.
- Projection not offered.
- Pagination mode incompatible with request.
- Authentication or scope prerequisites unmet.

These are **expected** outcomes when pushing beyond declared contracts—not adapter defects.

Unsupported semantics
~~~~~~~~~~~~~~~~~~~~~

The strategy defines a construct that this provider binding **does not implement**:

- Distinct from transient failure.
- Should be discoverable via capability declarations and validated early where possible.

Schema or version incompatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Canonical** or **normalization target** mismatch:

- Caller requests canonical output this adapter does not certify.
- Provider API revision no longer mappable to claimed targets without contract update.

This is a **contract drift** signal, not a user input validation error in the HTTP sense.

Normalization failure
~~~~~~~~~~~~~~~~~~~~~

Deterministic mapping cannot produce lawful canonical output:

- Contradictory provider payload vs invariants.
- Missing required identity or fields for requested projection with no lawful partial result.

Normalization failures are **semantic**, not “parser exceptions,” even if low-level parse errors triggered investigation.

Partial compatibility failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When partial compatibility is allowed but **cannot meet declared floors** (strategy-defined minimum completeness):

- Operation aborts as interoperability failure rather than silent truncation.

Semantic degradation (disallowed silent form)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Silent degradation**—returning partial or weaker data **without** declaring it—is treated as an **interoperability integrity violation** relative to API Pools principles.

Explicit degradation **with** structured reporting may be lawful where strategies permit.

Why silent degradation is dangerous
-----------------------------------

Silent degradation breaks:

- **Downstream invariants** — consumers assume completeness.
- **Compliance and auditing** — missing fields mistaken for absence of events.
- **Debugging** — failures appear as logic bugs rather than contract gaps.

API Pools favors **computability**: callers can **program against** declared gaps.

Explicit incompatibility reporting
----------------------------------

Incompatibility must be **structured** enough to support:

- User-facing messages **without** losing machine categories.
- **Retry semantics**—whether changing intent helps vs retrying execution.
- **Telemetry**—rates of mismatch vs outage.

Conceptual dimensions for structured reporting:

- **Category** — capability, version, normalization, unsupported.
- **Scope** — which resource, operation, projection, or version band.
- **Residual intent** — what subset might still succeed if retried with narrower intent.

Computable incompatibility
--------------------------

**Computable** means automated agents can reason:

- Adjust projections or pagination modes.
- Select alternate bindings **outside core** (extension layers).
- Escalate to human configuration changes (scopes, plans).

This depends on **stable taxonomies** and **discriminated failure categories**, not opaque strings.

Structured semantic failures
----------------------------

Structure preserves meaning across layers:

- Execution errors wrap transport detail **as causes**.
- Interoperability errors carry **semantic categories** independent of wire.

Boundary rule: **core semantic layers must not lose** interoperability categories when surfacing to callers.

Boundary enforcement
--------------------

Enforcement points:

- **Request validation** against capabilities before expensive work.
- **Normalization exit** with failure types when mapping cannot complete lawfully.
- **Response validation** where strategies define observable checks.

Boundaries prevent **normalization from compensating** for capability lies.

Semantic observability
----------------------

Observability distinguishes:

- **Mismatch rates** — configuration or product expectations vs vendor reality.
- **Version skew** — normalization targets drifting from provider APIs.
- **Partial success patterns** — intentional vs accidental truncation.

Metrics and traces should **tag interoperability categories** distinctly from HTTP status.

Relationship to execution errors
--------------------------------

Interoperability failures may **co-occur** with execution failures (e.g., partial response then mapping failure). **Causality** should preserve both:

- Outer envelope may indicate transport retry eligibility.
- Inner semantic failure explains whether retrying the **same intent** is futile.

Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Principle
     - Meaning
   * - First-class semantics
     - Interoperability failures ≠ generic errors
   * - No silent degradation
     - Gaps explicit and typed
   * - Computability
     - Categories support automation and routing of intent
   * - Observability
     - Distinct telemetry for semantic mismatch

Related documents
-----------------

- :doc:`capability-contracts`
- :doc:`normalization-contracts`
- :doc:`strategy-contracts`
- :doc:`canonical-resource-system`
