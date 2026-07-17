# Base Connector Interface Specification (v1)
<!-- markdownlint-disable no-duplicate-heading -->

## Purpose

Define a stable, minimal connector contract shared by Aracnid integration packages (e.g., `i-airtable`, `i-mongodb`, `i-xero2`) for common CRUD workflows.

This contract is intentionally narrow:

- portable across providers
- explicit about errors and return semantics
- extensible via capabilities and provider-specific methods

---

## Design principles

1. **Minimal common denominator**
   - Only define behaviors that can be implemented consistently across providers.
2. **Provider-neutral core**
   - No Airtable/Xero/Mongo-specific field/query semantics in the base API.
3. **Stable error model**
   - Input validation and provider failures are distinguishable.
4. **Capability-based extension**
   - Provider-specific features exposed through capability flags and optional extra methods.
5. **Backward-safe evolution**
   - Breaking changes require a spec version bump.
6. **Testable contract**
   - Spec compliance is validated by shared conformance tests.

---

## Core interface

## Class

`BaseConnector` (abstract)

## Constructor

Provider-specific constructor signatures are allowed.

Implementations MUST:

- validate required constructor inputs
- fail fast on invalid configuration
- avoid side effects beyond required client initialization

---

## Method contract (required)

## 1) create_one

```python
create_one(record: dict[str, Any]) -> dict[str, Any]
```

Create a new record/document/entity.

### Input

- `record` MUST be a dictionary-like payload.

### Return

- Provider response for created entity as `dict[str, Any]`.

### Errors

- `ValueError` for invalid input shape.
- `RuntimeError` for provider/API failures.

---

## 2) read_one

```python
read_one(record_id: str) -> dict[str, Any] | None
```

Fetch one entity by provider-native identifier.

### Input

- `record_id` MUST be a non-empty string.

### Return

- Entity dictionary if found.
- `None` if not found.

### Errors

- `ValueError` for invalid `record_id`.
- `RuntimeError` for provider failures unrelated to not-found.

---

## 3) read_many

```python
read_many(query: dict[str, Any] | None = None) -> list[dict[str, Any]]
```

Fetch multiple entities matching provider-supported filtering.

### Input

- `query` is optional and provider-interpreted.

### Return

- List of entity dictionaries.
- Empty list when no matches.

### Errors

- `ValueError` for invalid filter shape/type.
- `RuntimeError` for provider/API failures.

### Notes

- Pagination is implementation detail; method returns a flattened list unless documented otherwise by implementation.
- Connectors MAY provide extended overload/options in their own package docs while still supporting this base signature.

---

## 4) update_one

```python
update_one(record_id: str, changes: dict[str, Any]) -> dict[str, Any]
```

Partial update (patch-like semantics) of a single entity.

### Input

- `record_id` non-empty string.
- `changes` dictionary of fields to modify.

### Return

- Updated entity as dictionary.

### Errors

- `ValueError` for invalid inputs.
- `RuntimeError` for provider/API failures.

---

## 5) replace_one

```python
replace_one(record_id: str, new_record: dict[str, Any]) -> dict[str, Any]
```

Full replacement (put-like semantics) of a single entity.

### Input

- `record_id` non-empty string.
- `new_record` full replacement payload dictionary.

### Return

- Replaced entity as dictionary.

### Errors

- `ValueError` for invalid inputs.
- `RuntimeError` for provider/API failures.

---

## 6) delete_one

```python
delete_one(record_id: str, hard: bool = False) -> bool
```

Delete one entity.

### Input

- `record_id` non-empty string.
- `hard` requests physical delete when supported.

### Return

- `True` when delete operation succeeds.
- `False` allowed for not-found/no-op policy (must be documented by implementation).

### Errors

- `ValueError` for invalid inputs.
- `RuntimeError` for provider/API failures.

### Notes

- Soft delete semantics are provider-specific.
- If soft delete is unsupported and `hard=False`, implementation MUST document behavior (e.g., fallback to hard delete or raise).

---

## Reserved optional bulk methods (standardized names/signatures)

These methods are **not required in v1**, but their names/signatures are reserved to prevent cross-package drift.

### 1) create_many (optional)

```python
create_many(records: list[dict[str, Any]]) -> list[dict[str, Any]]
```

- Creates multiple entities.
- Return is provider responses for created entities.

### 2) update_many (optional)

```python
update_many(query: dict[str, Any], changes: dict[str, Any]) -> int | list[dict[str, Any]]
```

- Applies partial update to multiple entities matching `query`.
- Return MUST be documented per connector as either:
  - affected count (`int`), or
  - list of updated entities (`list[dict[str, Any]]`).

### 3) replace_many (optional)

```python
replace_many(query: dict[str, Any], new_record: dict[str, Any]) -> int | list[dict[str, Any]]
```

- Applies full replacement to multiple entities matching `query`.
- Return semantics follow `update_many`.

### 4) delete_many (optional)

```python
delete_many(query: dict[str, Any], hard: bool = False) -> int
```

- Deletes multiple entities matching `query`.
- Returns affected count.

### Bulk-method requirements when implemented

If any optional bulk method is implemented, connector docs MUST define:

- atomicity guarantees (all-or-nothing vs partial success)
- partial failure behavior/reporting
- idempotency expectations
- provider rate-limit implications
- exact return-shape semantics

---

## Error normalization (required)

Implementations MUST normalize errors into:

- **`ValueError`**: caller/input/config validation issues.
- **`RuntimeError`**: upstream/provider/runtime failures.

Implementations SHOULD preserve causal context:

```python
raise RuntimeError("Provider update failed") from exc
```

---

## Input mutation guarantee (required)

Implementations MUST NOT mutate caller-provided input objects (`record`, `changes`, `new_record`, `query`, etc.).

If transformation is needed, operate on copied data structures.

---

## Thread-safety and instance lifecycle

- Thread safety is **not guaranteed by default** unless a connector explicitly documents it.
- Connector docs MUST state whether instances are:
  - safe for concurrent use,
  - safe per-thread only, or
  - single-use/request-scoped.

---

## Timeout and retry policy ownership

- The base contract does not prescribe specific timeout/retry values.
- Each connector MUST document:
  - where timeouts are configured,
  - whether retries are automatic,
  - what failures are retryable.
- Callers SHOULD assume no retries unless documented.

---

## Logging and redaction rules

Implementations SHOULD log operation-level metadata (operation name, safe identifiers, timing) and MUST avoid secrets.

Implementations MUST NOT log:

- API keys/tokens/secrets
- authorization headers
- full sensitive payloads unless explicitly redacted

---

## Identifier semantics

- Base contract uses `record_id: str`.
- Providers MAY internally use other identifier types but MUST accept string at boundary and document conversions.

---

## Return-shape guidance

- Returned dictionaries SHOULD preserve provider-native keys unless a connector explicitly documents normalization.
- If normalization is performed, it MUST be consistent and documented in provider package docs.

---

## Capabilities (required property)

Each implementation MUST expose a capabilities descriptor:

```python
@property
def capabilities(self) -> dict[str, bool]:
    ...
```

Minimum required keys:

- `supports_query`
- `supports_partial_update`
- `supports_replace_one`
- `supports_soft_delete`
- `supports_hard_delete`
- `supports_transactions`

Optional standardized keys (recommended when applicable):

- `supports_create_many`
- `supports_update_many`
- `supports_replace_many`
- `supports_delete_many`
- `supports_field_projection`
- `supports_sort`
- `supports_pagination_controls`

Optional provider-specific keys are allowed.

---

## Conformance testing (required)

`aracnid-core` SHOULD provide a shared conformance test suite that connector packages run to validate contract compliance.

### Required base conformance assertions

1. Required methods exist with compatible call behavior.
2. `read_one` returns `None` on not-found.
3. Invalid inputs raise `ValueError` for required methods.
4. Provider/runtime failures surface as `RuntimeError`.
5. `read_many` returns a list (empty list when no matches).
6. `delete_one` returns `bool` and follows documented not-found behavior.
7. `capabilities` exists and includes all required keys.
8. Input objects are not mutated by connector methods.

### Capability-aware optional assertions

When capability flag is true and method exists, tests SHOULD validate:

- method return type/shape matches connector docs
- documented partial failure semantics
- documented idempotency/atomicity behavior where applicable

---

## Optional extension points (non-required)

Implementations MAY add provider-specific methods beyond reserved bulk methods, e.g.:

- advanced query languages/formulas
- projection/select fields
- ordering/sort
- provider-native bulk APIs
- upsert helpers
- transaction/session helpers

These MUST NOT break required base method behavior.

---

## Compliance checklist (for connector packages)

A connector is BaseConnector v1 compliant if it:

1. Implements all required methods with compatible signatures.
2. Enforces validation and error normalization rules.
3. Documents not-found and delete semantics.
4. Exposes `capabilities` property with required keys.
5. Does not mutate caller input objects.
6. Documents thread-safety, timeout, and retry policy.
7. Provides package-level docs for provider-specific extensions.
8. Passes shared base conformance tests.
9. If implementing reserved bulk methods, uses reserved names/signatures and documents bulk semantics.

---

## Versioning and change policy

- This document defines **BaseConnector v1**.
- Breaking interface or semantic changes require:
  1. version bump (v2),
  2. migration notes,
  3. connector compatibility update notes.

---

## Reference implementation sketch

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    @property
    @abstractmethod
    def capabilities(self) -> dict[str, bool]:
        raise NotImplementedError

    @abstractmethod
    def create_one(self, record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def read_one(self, record_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def read_many(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def update_one(self, record_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def replace_one(self, record_id: str, new_record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete_one(self, record_id: str, hard: bool = False) -> bool:
        raise NotImplementedError
```
