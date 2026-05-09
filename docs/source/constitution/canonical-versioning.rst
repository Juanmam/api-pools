Canonical versioning constitution
====================================

Preamble
--------

**Canonical versioning** governs **semantic evolution** of canonical resources and normalization targets. Silent mutation of meaning is **the** existential risk to interoperability: downstream systems trust labels they no longer understand.

Foundational truth requires **governed** change—not implicit drift.

Semantic evolution
--------------------

**Compatible evolution** (conceptual classes):

- **Additive** changes within a major lineage where meaning is preserved for existing projections under declared rules.  
- **Clarifications** that narrow previously ambiguous semantics **must** be reviewed as potential breaking clarifications.

**Incompatible evolution:**

- **Breaking** semantic changes require **new major** canonical families or explicit dual-target operation with **documented loss**.

Compatibility expectations
--------------------------

Consumers declare **which canonical targets** they consume; adapters declare **which targets** they certify for which projections. **Mismatch** is a **version incompatibility** outcome—not silent coercion.

Additive vs breaking changes
----------------------------

**Additive** is **not** automatic permission to reinterpret existing fields. **Renaming** meaning while retaining field names is **breaking**.

Canonical lineage
-----------------

**Lineage** tracks obligation chains: which normalization targets a binding implements and **which version bands** are authoritative for which resources.

Version-aware normalization
---------------------------

Every normalization path declares **targets**; “implicit latest” without governance is **disallowed**—see :doc:`normalization`.

Semantic stability guarantees
------------------------------

Stability is promised **relative to explicit targets** and **declared provider revision classes**—not absolute immutability against vendor chaos.

Constitutional constraints
--------------------------

**V-1 — No silent meaning mutation**
   Changing canonical semantics without version discipline is **void**.

**V-2 — Explicit transitions**
   Consumers upgrade targets through **declared** migration paths; shims document **lossiness**.

**V-3 — Adapter certification honesty**
   Claimed targets must match actual mapping behavior—drift is **contract falsification**.

**V-4 — Strategy alignment**
   Strategy contracts reference governable resource versions; unmanaged divergence between strategy docs and canonical targets is **technical debt** requiring resolution.

Why governance matters
----------------------

Vendor APIs move continuously; **without** version law, adapters become archaeological layers of implicit reinterpretation.

Related chapters
----------------

- :doc:`canonical-resources`  
- :doc:`normalization`  
- :doc:`interoperability-errors`  
