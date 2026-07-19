# Changelog
<!-- markdownlint-disable no-duplicate-heading -->

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.2.0] - 2026-07-19

### Added

- Query DSL v1 temporal semantics contract documentation in `docs/query-dsl.md` under:
  - `Supported Value Types and Temporal Semantics (v1)`

### Changed

- Query DSL normalization/validation now enforces timezone-aware `datetime` literals.
- Naive `datetime` values (missing/invalid `tzinfo`) are rejected with `QueryValidationError`.
- Core preserves caller-provided aware datetime representation; UTC normalization is adapter-defined.

### Contract / Conformance

- Added shared temporal contract tests for Query DSL datetime behavior.
- Integrated temporal contract tests into core conformance test execution.
- Required behavior now includes:
  - accepting timezone-aware datetimes (including non-UTC/local timezones),
  - rejecting naive datetimes,
  - preserving `date` as calendar-date semantic.

## [v1.1.0] - 2026-07-18

### Added

- Added Query DSL v1 utilities in `aracnid_core.query_dsl`:
  - `validate_query(query)`
  - `normalize_query(query)`
- Added support for logical operators: `$and`, `$or`, `$not`.
- Added support for field operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$exists`, `$contains`, `$startsWith`.
- Added normalized execution hook to connector contract:
  - `BaseConnector._read_many_normalized(query_dsl)`.

### Changed

- Updated `BaseConnector.read_many(...)` to accept Query DSL input (`query`) and normalize it before execution.
- Updated connector capability naming from filter-oriented to query-oriented:
  - `supports_filters` ➜ `supports_query`.
- Expanded contract tests for `read_many` normalization/delegation behavior and Query DSL validation coverage.

### Fixed

- Fixed Query DSL validation for non-string field keys to raise `QueryValidationError` consistently (instead of `AttributeError` in edge cases).

### Breaking changes

- Connector implementations of `BaseConnector` must implement:
  - `_read_many_normalized(self, query_dsl) -> list[dict]`
- Connector capability dictionaries should expose `supports_query` (replacing `supports_filters`).
- `read_many` contract is now Query DSL–based rather than raw filter-dict semantics.

### Notes

- This release introduces a normalized, validated query path for multi-record reads and improves error-path consistency and test coverage.

## [1.0.0] - 2026-07-12

### Added

- Initial stable `BaseConnector` v1.0 contract for connector implementations.
- Shared conformance testkit under `aracnid_core.contract_tests` for downstream connector repos.
- Contract marker configuration for pytest (`@pytest.mark.contract`) to support targeted conformance test runs.
- Public testkit entrypoint export via `aracnid_core.contract_tests`.

### Defined

- Baseline connector capabilities contract keys:
  - `supports_filters`
  - `supports_partial_update`
  - `supports_replace_one`
  - `supports_soft_delete`
  - `supports_hard_delete`
  - `supports_transactions`
- Required method-level input validation behavior for connector operations.
- Non-mutation expectation for caller-provided input dictionaries during CRUD operations.

### Testing

- Added reusable contract/conformance assertions for connector implementations.
- Added local contract test wrappers so `aracnid-core` validates its own contract suite.
- Enabled contract-only test execution via:
  - `pytest -m contract`
- Maintained compatibility with full-suite execution:
  - `pytest`

### Notes

- `v1.0.0` establishes the compatibility baseline for connector packages (for example `i-airtable`) to verify conformance by importing and running `aracnid_core.contract_tests`.
- Future connector-specific behavior may extend this baseline, but `BaseConnector` v1 semantics are now considered stable.

---

## [0.2.0] - 2026-07-12

### Added

- Pre-1.0 groundwork for `aracnid-core` packaging, schema components, and testing/tooling setup.
