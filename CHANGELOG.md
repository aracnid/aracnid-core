# Changelog
<!-- markdownlint-disable no-duplicate-heading -->

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.6.0] - 2026-11-14

### Added

- Exported `RecordNotFoundError`, `WriteRejectedError`, and
  `WriteOutcomeUnknownError`. All three remain catchable as `RuntimeError`.

### Changed

- Required `update_one` to update an existing record by ID and raise
  `RecordNotFoundError` for a confirmed missing target without creating a record
  (D-074).
- Defined separate outcomes for confirmed provider rejections and writes whose
  effects cannot be confirmed. Provider adapters preserve this distinction so
  calling operations can decide whether to reconcile or resubmit (D-075).

### Testing

- Added a reusable conformance check that updating a missing ID raises
  `RecordNotFoundError` and creates no record.
- Added coverage for the new exceptions' inheritance and distinct write outcome
  classifications.

## [v1.5.1] - 2026-07-30

### Changed

- Clarified and aligned Query DSL logical identity behavior for empty predicate objects (`{}`):
  - `{}` is allowed as a child predicate within `$and` and `$or` and represents logical TRUE / match-all.
  - `{ "$not": {} }` remains invalid.
- Updated Query DSL normalization semantics for identity simplification:
  - `{"$and": [{}, P]}` normalizes to `P`.
  - `{"$and": [{}, {}]}` normalizes to `{}`.
  - `{"$or": [P, {}]}` normalizes to `{}`.
- Updated Query DSL documentation to explicitly state that these identity simplifications occur during normalization before adapter translation.

### Testing

- Updated Query DSL contract tests to reflect the new validation behavior for empty logical children.
- Added focused normalization coverage for all-identity `$and` collapse (`{"$and": [{}, {}]} -> {}`).

## [v1.5.0] - 2026-07-26

### Added

- Added Mongo-style Query DSL regex predicate support:
  - `$regex` field operator for pattern matching.
  - `$options` modifier operator (requires `$regex`) with supported flags: `i`, `m`, `s`, `x`, `u`.

### Changed

- Updated Query DSL validation to enforce regex-specific operator rules:
  - `$regex` must be a string pattern or compiled regex object.
  - `$options` must be a string and is only valid when `$regex` is present in the same operator object.
- Updated Query DSL documentation (`docs/query-dsl.md`) with regex semantics and validation constraints.

### Testing

- Added Query DSL contract test coverage for `$regex`/`$options` valid and invalid forms.

## [v1.4.0] - 2026-07-25

### Changed

- Clarified reserved optional bulk method return semantics in the base connector spec:
  - `create_many(records)` returns `list[dict[str, Any]]` (created entities).
  - `update_many(query, changes)` returns non-negative `int` (affected count).
  - `replace_many(query, new_record)` returns non-negative `int` (affected count).
  - `delete_many(query, hard=False)` returns non-negative `int` (affected count).
- Updated bulk-method documentation requirements to explicitly require connector docs to define affected-count meaning (`matched`, `modified`, or `successfully processed`) for count-based bulk operations.
- Updated capability-aware conformance guidance in the spec to reflect split return semantics (`create_many` list return vs count returns for update/replace/delete).

### Testing

- Added shared capability-gated contract checks for optional bulk count-return methods:
  - `update_many`, `replace_many`, and `delete_many` must return non-negative `int` when their corresponding capability flag is enabled.
- Re-exported the new optional bulk contract checks in local conformance wrappers and updated contract-test README integration examples.

## [v1.3.2] - 2026-07-21

### Added

- Added shared core datetime timezone configuration:
  - `ARACNID_DATETIME_TZ_MODE=utc|local|keep`
  - `ARACNID_LOCAL_TIMEZONE=<IANA timezone>` (required for `local` mode).
- Added shared datetime coercion helpers for ISO datetime parsing and timezone normalization.
- Added contract tests for timezone coercion and environment configuration validation.

### Changed

- Standardized aware datetime coercion behavior across connectors via `aracnid-core`.
- `local` timezone mode now requires explicit `ARACNID_LOCAL_TIMEZONE`; no implicit system-local fallback is used.
- Updated `docs/base-connector-interface-spec.md` with an optional standardized section:
  - datetime timezone coercion modes (`utc|local|keep`)
  - required `ARACNID_LOCAL_TIMEZONE` for `local` mode
  - explicit prohibition on implicit host/system-local fallback
  - validation requirement that naive datetimes raise `ValueError`

### Validation

- Naive datetimes are explicitly unsupported and raise validation errors.

## [v1.3.1] - 2026-07-20

### Added

- Added reusable Query DSL sort contract tests in `aracnid_core.contract_tests` for downstream adapter conformance.

### Changed

- No runtime behavior changes; this patch improves shared contract-test coverage for sort validation/normalization.

## [v1.3.0] - 2026-07-20

### Added

- Added Mongo-style sorting support to Query DSL for `read_many(...)`:
  - `sort=[{"FieldA": 1}, {"FieldB": -1}]`
  - `1` = ascending, `-1` = descending
  - list order defines sort precedence (multi-key sort)

### Changed

- Updated `BaseConnector.read_many(...)` to accept optional `sort` input.
- Updated base connector normalized execution contract so adapters receive both:
  - normalized `query_dsl`
  - normalized `sort_dsl`
- Expanded Query DSL docs (`docs/query-dsl.md`) to include:
  - sort API shape
  - validation rules
  - normalization behavior
  - valid/invalid examples

### Validation / Contract

- Added `validate_sort(...)` and `normalize_sort(...)` to Query DSL utilities.
- Enforced strict sort validation with `QueryValidationError` on invalid specs:
  - `sort` must be `None` or a non-empty list
  - each entry must be a single-key object
  - field name must be a non-empty string and must not start with `$`
  - direction must be exactly `1` or `-1` (boolean values rejected)
  - duplicate sort fields are invalid

### Tests

- Extended Query DSL contract tests to cover sort validation and normalization.
- Updated read-many contract tests (including spy connector signature) to verify normalized query and sort forwarding behavior.
  
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
