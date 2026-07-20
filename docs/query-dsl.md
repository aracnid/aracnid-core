# Aracnid Query DSL v1

## Purpose

Aracnid Query DSL provides a backend-agnostic query format for `read_many()` across adapters (Airtable, MongoDB, Xero, Square, etc.).

This specification defines:

- the allowed query shape,
- supported operators,
- sort shape and validation rules,
- and expected adapter behavior.

---

## Scope (v1)

This version covers filtering predicates (`query`) and sorting (`sort`).  
Pagination and projection can be added in a later version.

---

## Public API

Query DSL is passed via `query` and `sort`:

```python
read_many(
    query: dict[str, Any] | None = None,
    sort: list[dict[str, int]] | None = None,
    ...
)
```

If `query` is `None` or `{}`, no filtering is applied.  
If `sort` is `None`, no sorting is applied.

---

## Canonical DSL Shape

### Query predicate (`query`)

A query is a predicate object. Query DSL supports equivalent forms:

1. **Shorthand equality form**

   ```json
   { "status": "active" }
   ```

2. **Explicit operator form**

   ```json
   { "status": { "$eq": "active" } }
   ```

3. **Logical form**

   ```json
   {
     "$and": [
       { "status": { "$eq": "active" } },
       { "amount": { "$gt": 10 } }
     ]
   }
   ```

Multiple operators on the same field are combined with implicit AND.

### Sort spec (`sort`)

Sorting uses Mongo-style list precedence:

```json
[
  { "DueDate": 1 },
  { "Priority": -1 }
]
```

- `1` = ascending
- `-1` = descending
- earlier list entries have higher precedence

---

## Supported Value Types and Temporal Semantics (v1)

Field operator values in Query DSL MAY be any JSON-like scalar/object value accepted by the adapter, including:

- string
- number
- boolean
- null
- arrays (where required by operator, e.g. `$in`, `$nin`)
- temporal values (`date`, `datetime`) when provided by the caller/runtime language

### Temporal semantics

To ensure consistent cross-adapter behavior, temporal values follow this contract:

#### `date`

- Represents a **calendar date only** (no time-of-day, no timezone semantics).
- Example intent: `"2026-07-19"` means that calendar day.

#### `datetime` (timezone-aware required)

- `datetime` values **MUST be timezone-aware**.
- Naive datetimes (no timezone info / `tzinfo is None`) are **invalid** and MUST raise `QueryValidationError`.
- Aware datetimes represent an **absolute instant in time**.
- Adapters MAY normalize representation (for example, to UTC), but MUST preserve the same instant.

### Conformance requirements

- Adapters MUST accept timezone-aware datetimes, including non-UTC timezones (e.g., application local timezone).
- Adapters MUST apply the same temporal semantics across all temporal-capable operators (`$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, and others if added later).
- Adapters MUST reject naive datetimes consistently with a clear validation error.
- Adapters MUST document any backend-specific representation constraints while preserving the above semantics.

## Supported Operators (v1)

### Logical operators

- `$and`: array of predicates, length >= 1
- `$or`: array of predicates, length >= 1
- `$not`: single predicate object

### Field operators

- `$eq`
- `$ne`
- `$gt`
- `$gte`
- `$lt`
- `$lte`
- `$in` (non-empty array)
- `$nin` (non-empty array)
- `$exists` (boolean)
- `$contains` (string containment, backend support optional)
- `$startsWith` (string prefix, backend support optional)

---

## Sort Rules (v1.2.0)

Sort entries must follow Mongo-style shape:

```json
[{ "FieldName": 1 }, { "OtherField": -1 }]
```

Validation rules:

1. `sort` must be `None` or a list.
2. If a list, it must be non-empty.
3. Each list item must be an object with exactly one key.
4. Field name must be a non-empty string and MUST NOT start with `$`.
5. Direction must be exactly `1` (ascending) or `-1` (descending).
6. Duplicate fields in the same sort spec are invalid.

Invalid sort specs MUST raise `QueryValidationError`.

---

## Equivalent Query Forms

The following are semantically equivalent:

### Single-field equality

```json
{ "status": "active" }
```

```json
{ "status": { "$eq": "active" } }
```

### Multi-field equality

```json
{
  "status": "active",
  "type": "asset"
}
```

```json
{
  "$and": [
    { "status": { "$eq": "active" } },
    { "type": { "$eq": "asset" } }
  ]
}
```

---

## Allowed Examples

### 1) Complex predicate with sort

```json
{
  "query": {
    "$and": [
      { "Account Type": { "$eq": "Current Asset" } },
      { "Adjusting Account Code": { "$exists": true, "$ne": "" } }
    ]
  },
  "sort": [
    { "Account Type": 1 },
    { "Adjusting Account Code": -1 }
  ]
}
```

### 2) OR predicate

```json
{
  "$or": [
    { "status": { "$eq": "draft" } },
    { "status": { "$eq": "pending" } }
  ]
}
```

### 3) NOT predicate

```json
{
  "$not": {
    "archived": { "$eq": true }
  }
}
```

### 4) Sort-only call (no filter)

```json
[
  { "CreatedAt": -1 },
  { "Name": 1 }
]
```

---

## Invalid Examples

### Query examples

#### 1) Unknown operator

```json
{ "Amount": { "$between": [1, 10] } }
```

Reason: `$between` not in v1.

#### 2) Empty logical array

```json
{ "$and": [] }
```

Reason: logical arrays must be non-empty.

#### 3) Bad `$exists` type

```json
{ "code": { "$exists": "yes" } }
```

Reason: `$exists` must be boolean.

#### 4) Mixed logical and field keys at same object level

```json
{
  "$and": [{ "status": { "$eq": "active" } }],
  "type": { "$eq": "asset" }
}
```

Reason: object must be either logical-node or field-node (not both).

### Sort examples

#### 5) Bad direction

```json
[{ "DueDate": 0 }]
```

Reason: direction must be `1` or `-1`.

#### 6) Multiple keys in one sort entry

```json
[{ "DueDate": 1, "Priority": -1 }]
```

Reason: each sort entry must contain exactly one field.

#### 7) Duplicate sort field

```json
[{ "DueDate": 1 }, { "DueDate": -1 }]
```

Reason: duplicate sort fields are invalid.

---

## Validation Rules

### Query validation

1. Query must be a JSON-like object (`dict`).
2. Top-level node must be either:
   - logical node (`$and` / `$or` / `$not`), or
   - field node (`{ fieldName: condition, ... }`)
3. Logical node rules:
   - `$and` and `$or` require non-empty arrays of predicate objects.
   - `$not` requires exactly one predicate object.
4. Field node rules:
   - Field names MUST NOT start with `$`.
   - Field condition may be:
     - scalar shorthand (interpreted as `$eq`)
     - explicit operator object (`{"$eq": ...}`)
5. Operator rules:
   - only supported operators allowed.
   - `$in`/`$nin` require non-empty arrays.
   - `$exists` requires boolean.
6. Null handling:
   - `{"field": null}` is valid and equivalent to `{"field":{"$eq":null}}`.
   - adapters decide backend-specific null semantics.
7. Empty query (`None` or `{}`) means “no filter”.

### Sort validation

1. `sort=None` means “no sort”.
2. Otherwise, `sort` must be a non-empty list.
3. Each entry must be a one-key dict `{field: direction}`.
4. `field` must be a non-empty string and MUST NOT start with `$`.
5. `direction` must be `1` or `-1`.
6. Duplicate `field` entries are invalid.

---

## Normalization Rules

Normalization MUST produce canonical explicit DSL.

### Query normalization transformations

- Scalar shorthand:
  - `{"status":"active"}` -> `{"status":{"$eq":"active"}}`
- Multi-field shorthand:
  - `{"a":1,"b":2}` -> `{"$and":[{"a":{"$eq":1}},{"b":{"$eq":2}}]}`
- Preserve already-canonical logical structure.
- Reject ambiguous/invalid structures early with `QueryValidationError`.

### Sort normalization transformations

- `None` -> `[]`
- Preserve list order and validated directions exactly.
- Reject invalid structures early with `QueryValidationError`.

---

## Adapter Compilation Contract

Each adapter implements:

```python
compile_query(query_dsl: dict[str, Any]) -> CompiledQuery
```

and compiles sort according to adapter capabilities.

Where `CompiledQuery` is adapter-specific (e.g., Airtable formula string, Mongo dict, REST filter params).

### Required behavior

1. Validate (or trust pre-validated input from base layer).
2. Compile all supported operators.
3. Apply sort precedence in list order when backend supports sorting.
4. For unsupported operators or sort behavior:
   - raise `UnsupportedQueryError` with:
     - adapter name,
     - operator (or sort detail),
     - optional field,
     - human-readable guidance.

### Optional behavior

Adapters MAY support partial pushdown + local filtering for small result sets, but MUST document this explicitly.

---

## Error Types

- `QueryValidationError`: malformed DSL (query or sort).
- `UnsupportedQueryError`: valid DSL operator/sort unsupported by adapter.
- `QueryCompilationError`: unexpected compile failure.

Suggested message format:

```text
UnsupportedQueryError: Adapter 'airtable' does not support operator '$startsWith' on field 'Name'
```

---

## Versioning

- This document defines **Query DSL v1** (with v1.2.0 temporal/sort clarifications).
- New operators or semantics changes require:
  - doc update,
  - tests,
  - release note entry.

---