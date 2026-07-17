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
