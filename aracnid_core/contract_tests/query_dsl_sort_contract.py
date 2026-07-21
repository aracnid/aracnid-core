"""Reusable contract tests for Query DSL sort normalization/validation.

Adapters can re-export these tests to ensure consistent sort DSL behavior
across implementations.
"""
from __future__ import annotations

import pytest

from aracnid_core.exceptions import QueryValidationError
from aracnid_core.query_dsl import normalize_sort


def test_normalize_sort_accepts_none() -> None:
    assert normalize_sort(None) == []


def test_normalize_sort_accepts_single_and_multi() -> None:
    assert normalize_sort([{"DueDate": 1}]) == [{"DueDate": 1}]
    assert normalize_sort([{"DueDate": 1}, {"Priority": -1}]) == [
        {"DueDate": 1},
        {"Priority": -1},
    ]


@pytest.mark.parametrize(
    "sort",
    [
        "not-a-list",
        [],
        [1],
        [{}],
        [{"DueDate": 1, "Priority": -1}],
        [{"": 1}],
        [{"$bad": 1}],
        [{"DueDate": 0}],
        [{"DueDate": "asc"}],
        [{"DueDate": True}],
    ],
)
def test_normalize_sort_rejects_invalid_shapes(sort) -> None:
    with pytest.raises(QueryValidationError):
        normalize_sort(sort)


def test_normalize_sort_rejects_duplicate_fields() -> None:
    with pytest.raises(QueryValidationError, match=r"duplicate sort field"):
        normalize_sort([{"DueDate": 1}, {"DueDate": -1}])