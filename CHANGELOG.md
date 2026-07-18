# Changelog
<!-- markdownlint-disable no-duplicate-heading -->

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
