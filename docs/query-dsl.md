# Aracnid Query DSL v1

## Purpose

Aracnid Query DSL provides a backend-agnostic query format for `read_many()` across adapters (Airtable, MongoDB, Xero, Square, etc.).

This specification defines:

- the allowed query shape,
- supported operators,
- validation rules,
- and expected adapter behavior.

---

## Scope (v1)

This version covers filtering predicates (`query`).  
Pagination, sorting, and projection can be added in v1.1+.

---

## Public API

Query DSL is passed via `query`:

```python
read_many(query: dict[str, Any] | None = None, ...)
```

If `query` is `None` or `{}`, no filtering is applied.

---

## Canonical DSL Shape

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

---

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

### 1) Complex predicate

```json
{
  "$and": [
    { "Account Type": { "$eq": "Current Asset" } },
    { "Adjusting Account Code": { "$exists": true, "$ne": "" } }
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

---

## Invalid Examples

### 1) Unknown operator

```json
{ "Amount": { "$between": [1, 10] } }
```

Reason: `$between` not in v1.

### 2) Empty logical array

```json
{ "$and": [] }
```

Reason: logical arrays must be non-empty.

### 3) Bad `$exists` type

```json
{ "code": { "$exists": "yes" } }
```

Reason: `$exists` must be boolean.

### 4) Mixed logical and field keys at same object level

```json
{
  "$and": [{ "status": { "$eq": "active" } }],
  "type": { "$eq": "asset" }
}
```

Reason: object must be either logical-node or field-node (not both).

---

## Validation Rules

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

---

## Normalization Rules

Normalization MUST produce canonical explicit DSL.

### Required transformations

- Scalar shorthand:
  - `{"status":"active"}` -> `{"status":{"$eq":"active"}}`
- Multi-field shorthand:
  - `{"a":1,"b":2}` -> `{"$and":[{"a":{"$eq":1}},{"b":{"$eq":2}}]}`
- Preserve already-canonical logical structure.
- Reject ambiguous/invalid structures early with `QueryValidationError`.

---

## Adapter Compilation Contract

Each adapter implements:

```python
compile_query(query_dsl: dict[str, Any]) -> CompiledQuery
```

Where `CompiledQuery` is adapter-specific (e.g., Airtable formula string, Mongo dict, REST filter params).

### Required behavior

1. Validate (or trust pre-validated input from base layer).
2. Compile all supported operators.
3. For unsupported operators:
   - raise `UnsupportedQueryError` with:
     - adapter name,
     - operator,
     - optional field,
     - human-readable guidance.

### Optional behavior

Adapters MAY support partial pushdown + local filtering for small result sets, but MUST document this explicitly.

---

## Error Types

- `QueryValidationError`: malformed DSL.
- `UnsupportedQueryError`: valid DSL operator unsupported by adapter.
- `QueryCompilationError`: unexpected compile failure.

Suggested message format:

```text
UnsupportedQueryError: Adapter 'airtable' does not support operator '$startsWith' on field 'Name'
```

---

## Versioning

- This document defines **Query DSL v1**.
- New operators or semantics changes require:
  - doc update,
  - tests,
  - release note entry.

---
