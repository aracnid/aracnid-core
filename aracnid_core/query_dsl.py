"""Query DSL v1 validation and normalization utilities.
"""
from typing import Any, Final

from .exceptions import QueryValidationError

QueryDict = dict[str, Any]

LOGICAL_OPS: Final[set[str]] = {"$and", "$or", "$not"}
FIELD_OPS: Final[set[str]] = {
    "$eq",
    "$ne",
    "$gt",
    "$gte",
    "$lt",
    "$lte",
    "$in",
    "$nin",
    "$exists",
    "$contains",
    "$startsWith",
}
ALL_OPS: Final[set[str]] = LOGICAL_OPS | FIELD_OPS


def validate_query(query: QueryDict | None) -> None:
    """Validate a Query DSL v1 object.

    Rules:
    - None or {} is valid (no filter).
    - Node must be either logical-node OR field-node (not mixed).
    - Logical node:
      - $and/$or: non-empty list of predicate objects
      - $not: single predicate object
    - Field node:
      - keys must not start with $
      - values may be scalar (shorthand eq) or operator object
    - Operator object:
      - only supported field operators
      - $in/$nin non-empty lists
      - $exists boolean

    Args:
        query (QueryDict | None): The query to validate.

    Raises:
        QueryValidationError: If the query does not conform to the rules.
    """
    if query is None:
        return
    if not isinstance(query, dict):
        raise QueryValidationError("Query must be a dict or None.")
    if query == {}:
        return

    _validate_node(query, path="$")


def normalize_query(query: QueryDict | None) -> QueryDict:
    """Normalize a query into canonical explicit form.

    Canonicalization:
    - None / {} -> {}
    - scalar shorthand: {"a": 1} -> {"a": {"$eq": 1}}
    - multi-field shorthand/object field-node:
      {"a": 1, "b": {"$gt": 2}} -> {"$and": [{"a": {"$eq": 1}}, {"b": {"$gt": 2}}]}
    - preserve logical structure while recursively normalizing children.

    Args:
        query (QueryDict | None): The query to normalize.

    Returns:
        QueryDict: The normalized query.
    """
    if query is None or query == {}:
        return {}

    validate_query(query)
    return _normalize_node(query)


def _validate_node(node: Any, path: str) -> None:
    """Recursively validate a predicate node.

    Args:
        node (Any): The predicate node to validate.
        path (str): The path to the node in the query, for error messages.
    
    Raises:
        QueryValidationError: If the node does not conform to the rules.
    """
    if not isinstance(node, dict):
        raise QueryValidationError(f"{path}: predicate node must be an object.")

    if not node:
        # empty dict only valid at top-level for "no filter"; here it is nested
        raise QueryValidationError(f"{path}: empty predicate object is not allowed.")

    logical_keys = [k for k in node if k in LOGICAL_OPS]
    dollar_keys = [k for k in node if isinstance(k, str) and k.startswith("$")]

    # unknown $operator keys
    for k in dollar_keys:
        if k not in LOGICAL_OPS:
            raise QueryValidationError(f"{path}: unknown logical operator '{k}'.")

    # mixed logical + field keys disallowed
    has_logical = len(logical_keys) > 0
    has_field = any(not k.startswith("$") for k in node.keys())
    if has_logical and has_field:
        raise QueryValidationError(
            f"{path}: cannot mix logical keys {logical_keys} with field keys."
        )

    if has_logical:
        if len(node) != 1:
            raise QueryValidationError(
                f"{path}: logical node must contain exactly one logical operator."
            )
        op = logical_keys[0]
        value = node[op]
        if op in {"$and", "$or"}:
            if not isinstance(value, list) or len(value) == 0:
                raise QueryValidationError(
                    f"{path}.{op}: must be a non-empty list of predicates."
                )
            for i, child in enumerate(value):
                _validate_node(child, f"{path}.{op}[{i}]")
        elif op == "$not":
            if not isinstance(value, dict):
                raise QueryValidationError(f"{path}.$not: must be a predicate object.")
            _validate_node(value, f"{path}.$not")
        return

    # field-node
    for field, condition in node.items():
        if not isinstance(field, str):
            raise QueryValidationError(f"{path}: field names must be strings.")
        if field.startswith("$"):
            raise QueryValidationError(
                f"{path}: field name '{field}' cannot start with '$'."
            )

        if isinstance(condition, dict):
            _validate_field_ops(condition, f"{path}.{field}")
        else:
            # scalar shorthand is valid; no further checks here
            continue


def _validate_field_ops(op_obj: dict[str, Any], path: str) -> None:
    """Validate a field operator object.

    Args:
        op_obj (dict[str, Any]): The field operator object to validate.
        path (str): The path to the object in the query, for error messages.

    Raises:
        QueryValidationError: If the field operator object does not conform to the rules.
    """
    if not op_obj:
        raise QueryValidationError(f"{path}: operator object cannot be empty.")

    for op, value in op_obj.items():
        if op not in FIELD_OPS:
            raise QueryValidationError(f"{path}: unsupported field operator '{op}'.")

        if op in {"$in", "$nin"}:
            if not isinstance(value, list) or len(value) == 0:
                raise QueryValidationError(f"{path}.{op}: must be a non-empty list.")

        if op == "$exists" and not isinstance(value, bool):
            raise QueryValidationError(f"{path}.$exists: must be boolean.")


def _normalize_node(node: dict[str, Any]) -> dict[str, Any]:
    """Recursively normalize a predicate node into canonical explicit form.

    Args:
        node (dict[str, Any]): The predicate node to normalize.
    
    Returns:
        dict[str, Any]: The normalized predicate node.
    """
    # logical node
    for op in LOGICAL_OPS:
        if op in node:
            if op in {"$and", "$or"}:
                normalized_children = [_normalize_node(child) for child in node[op]]
                return {op: normalized_children}
            if op == "$not":
                return {"$not": _normalize_node(node["$not"])}

    # field-node -> canonical explicit; multi-field => $and of single-field nodes
    single_field_nodes: list[dict[str, Any]] = []
    for field, condition in node.items():
        if isinstance(condition, dict):
            single_field_nodes.append({field: dict(condition)})
        else:
            single_field_nodes.append({field: {"$eq": condition}})

    if len(single_field_nodes) == 1:
        return single_field_nodes[0]

    return {"$and": single_field_nodes}
