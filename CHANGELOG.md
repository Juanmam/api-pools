# Changelog

All notable changes to this project are documented here. The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Semantic versioning

- **MAJOR**: incompatible changes to the documented stable public API (`apipools` root exports, module paths marked stable, exception types raised for contract violations).
- **MINOR**: additive features, new optional extras, backward-compatible extensions.
- **PATCH**: bug fixes and documentation that do not change observable behavior of the stable API.

## [0.2.0] — 2026-05-08

### Changed (breaking)

- The installable **`apipools`** package no longer ships reference mocks, demo `ProviderA`/`ProviderB`, `SocialAPIStrategy`, Instagram-shaped legacy normalizers, or **`apipools.contrib.social.live`**. Implement adapters in your application; this repo keeps **test-only** copies under `tests/support/`.
- **`apipools.versioning`**: `LEGACY_SOCIAL_NORMALIZATION_V1`, `SUPPORTED_LEGACY_SOCIAL_VERSIONS`, and `assert_legacy_social_projection_version` replaced by **`assert_supported_projection_version(version, supported, ...)`**.
- **`apipools.normalization`**: Instagram legacy functions removed from the public package (use generic `CapabilityNormalizer` or your own mappers).
- **`apipools.core.providers`**: exports only **`ProviderRequest`** and **`ProviderRegistry`**; concrete demo providers moved to **`tests/support/demo_providers.py`**.
- **`apipools.reference`** removed; test defaults (e.g. cursor HMAC secret) live in **`tests/support/constants.py`**.
- Constitution CLI package moved from `apipools.compliance` to **`compliance_cli`**; entry points remain **`apipools-compliance`** and **`python -m compliance_cli`**.

### Added

- Sphinx **Furo** theme and expanded API reference (normalization submodules, `core.execution`, resilience).
- **`docs/source/architecture/implementation-map.rst`** describing package layout vs concepts.

### Removed

- **`social-live`** optional extra from `pyproject.toml` (HTTP deps remain on **`dev`** for repository tests).

## [0.1.0] — 2026-05-08

### Added

- Installable package metadata via `pyproject.toml` (setuptools, `src/` layout, `py.typed`).
- Stable root exports focused on semantic primitives; reference social slice under `apipools.contrib.social`.
- `apipools.routing` facade for deterministic multi-binding selection and execution (non-orchestration).
- `apipools.execution` errors (`ExecutionError`, `TransportTimeoutError`) and execution-scoped `RateLimitExceededError`, separate from `InteroperabilityError`.
- Pagination `OpaqueCursorStorage` protocol, `MemoryCursorStore`, and optional `RedisCursorStore` (Redis-compatible client).
- `apipools.reference.constants` for documented test defaults (e.g. cursor HMAC secret placeholder).
- Single source for legacy social normalization version checks in `apipools.versioning`.
- `Protocol` ports in `apipools.protocols` for reference bindings.
- CLI `apipools-compliance` and compliance package.
- Library user docs: Quickstart, API reference (Sphinx), pagination operations.
- GitHub Actions CI and optional PyPI publishing workflow (tag-triggered).
