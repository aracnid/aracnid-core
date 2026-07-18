"""Tests for the Query DSL normalization and validation.
"""
import pytest

from aracnid_core.exceptions import QueryValidationError
from aracnid_core.query_dsl import normalize_query, validate_query


def test_validate_accepts_none_and_empty() -> None:
    validate_query(None)
    validate_query({})


def test_validate_shorthand_and_explicit() -> None:
    validate_query({"status": "active"})
    validate_query({"status": {"$eq": "active"}})


def test_validate_logical_nodes() -> None:
    validate_query({"$and": [{"a": {"$eq": 1}}, {"b": {"$gt": 2}}]})
    validate_query({"$or": [{"a": 1}, {"b": 2}]})
    validate_query({"$not": {"archived": {"$eq": True}}})

def test_normalize_query_preserves_not_and_normalizes_child() -> None:
    query = {"$not": {"name": "alpha"}}

    out = normalize_query(query)

    assert out == {"$not": {"name": {"$eq": "alpha"}}}

def test_validate_rejects_unknown_operator() -> None:
    with pytest.raises(QueryValidationError):
        validate_query({"amount": {"$between": [1, 2]}})


def test_validate_rejects_mixed_logical_and_field() -> None:
    with pytest.raises(QueryValidationError):
        validate_query({"$and": [{"a": 1}], "b": 2})


def test_validate_rejects_empty_and_or() -> None:
    with pytest.raises(QueryValidationError):
        validate_query({"$and": []})
    with pytest.raises(QueryValidationError):
        validate_query({"$or": []})


def test_validate_exists_must_be_bool() -> None:
    with pytest.raises(QueryValidationError):
        validate_query({"code": {"$exists": "yes"}})


def test_validate_in_nin_must_be_non_empty_list() -> None:
    with pytest.raises(QueryValidationError):
        validate_query({"a": {"$in": []}})
    with pytest.raises(QueryValidationError):
        validate_query({"a": {"$nin": "x"}})


def test_normalize_single_shorthand() -> None:
    assert normalize_query({"status": "active"}) == {"status": {"$eq": "active"}}


def test_normalize_multifield_to_and() -> None:
    assert normalize_query({"a": 1, "b": 2}) == {
        "$and": [{"a": {"$eq": 1}}, {"b": {"$eq": 2}}]
    }


def test_normalize_preserves_logical_structure() -> None:
    assert normalize_query({"$or": [{"a": 1}, {"b": {"$gt": 2}}]}) == {
        "$or": [{"a": {"$eq": 1}}, {"b": {"$gt": 2}}]
    }


def test_normalize_none_empty() -> None:
    assert normalize_query(None) == {}
    assert normalize_query({}) == {}

@pytest.mark.parametrize(
    "query,match",
    [
        (42, r"dict or None"),
        ({"$or": {"name": "alpha"}}, r"\$or.*non-empty list"),
        ({"$or": [1]}, r"predicate node must be an object"),
        ({"$and": {"name": "alpha"}}, r"\$and.*non-empty list"),
        ({"$or": []}, r"\$or.*non-empty list"),
        ({"$not": [{"name": "alpha"}]}, r"\$not.*predicate object"),
        ({"$wat": [{"name": "alpha"}]}, r"unknown logical operator '\$wat'"),
        ({"$and": [{"name": "a"}], "$or": [{"name": "b"}]}, r"logical node must contain exactly one logical operator"),
        ({"$or": [{"name": "a"}, {}]}, r"empty predicate object is not allowed"),
        ({"name": {}}, r"operator object cannot be empty"),
        ({"name": {"$wat": 1}}, r"unsupported field operator '\$wat'"),
        ({"name": {"$in": "not-a-list"}}, r"\$in.*non-empty list"),
        ({"name": {"$nin": []}}, r"\$nin.*non-empty list"),
        ({"name": {"$exists": "yes"}}, r"\$exists.*boolean"),
        ({1: "alpha"}, r"field names must be strings"),
    ],
)
def test_validate_query_raises_expected_errors(query, match: str) -> None:
    with pytest.raises(QueryValidationError, match=match):
        validate_query(query)  # direct validation branch coverage


@pytest.mark.parametrize(
    "query",
    [
        {"$or": {"name": "alpha"}},
        {"name": {"$exists": "yes"}},
        {"name": {"$in": []}},
        {"$not": [{"name": "alpha"}]},
        {"name": {}},
    ],
)
def test_normalize_query_propagates_validation_error(query) -> None:
    with pytest.raises(QueryValidationError):
        normalize_query(query)

@pytest.mark.parametrize(
    "query",
    [
        {"$or": {"name": "alpha"}},                 # logical op expects list
        {"$and": {"name": "alpha"}},                # logical op expects list
        {"$or": []},                                # logical op list empty
        {"name": {"$wat": 1}},                      # unknown field operator
        {"$wat": [{"name": "alpha"}]},              # unknown top-level operator
        {"name": {"$in": "not-a-list"}},            # $in expects list
        {"name": {"$nin": "not-a-list"}},           # $nin expects list
        {"$not": [{"name": "alpha"}]},              # $not expects object, not list
    ],
)
def test_normalize_query_raises_query_validation_error(query: dict) -> None:
    with pytest.raises(QueryValidationError):
        normalize_query(query)


def test_validate_query_rejects_dollar_field_name_defensive_branch() -> None:
    """Test that validate_query rejects a field name starting with $.
     
    This case will probably never occur in practice,
    but we want to ensure that the field-node validation branch is exercised.        
    """
    class _HiddenDollarKeyDict(dict):
        """Hide keys from plain iteration so field-node validation is exercised."""

        def __iter__(self):
            return iter(())

    query = _HiddenDollarKeyDict({"$bad": 1})

    with pytest.raises(
        QueryValidationError,
        match=r"field name '\$bad' cannot start with '\$'",
    ):
        validate_query(query)

