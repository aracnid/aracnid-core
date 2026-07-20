"""Contract tests for the read_many() method of BaseConnector.
"""
from typing import Any

import pytest

from aracnid_core.base import BaseConnector
from aracnid_core.query_dsl import QueryValidationError


class SpyConnector(BaseConnector):
    """
    Concrete connector for read_many contract assertions.
    Captures the normalized query passed to _read_many_normalized.
    """

    def __init__(self) -> None:
        self.last_query: dict[str, Any] | None = None
        self.last_sort: list[dict[str, Any]] | None = None
        self.result_to_return: list[dict] = [{"id": "r1", "name": "alpha"}]

    @property
    def capabilities(self) -> dict[str, bool]:
        return {
            "supports_query": True,
            "supports_partial_update": True,
            "supports_replace_one": True,
            "supports_soft_delete": True,
            "supports_hard_delete": True,
            "supports_transactions": False,
        }

    def create_one(self, record: dict[str, Any]) -> dict[str, Any]:
        return {"id": "created", **record}

    def read_one(self, record_id: str) -> dict[str, Any] | None:
        return {"id": record_id, "name": "alpha"}

    def update_one(self, record_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        return {"id": record_id, **changes}

    def replace_one(self, record_id: str, new_record: dict[str, Any]) -> dict[str, Any]:
        return {"id": record_id, **new_record}

    def delete_one(self, record_id: str, hard: bool = False) -> bool:
        return True

    def _read_many_normalized(self, query_dsl: dict[str, Any], sort_dsl: list[dict[str, Any]] | None = None) -> list[dict]:
        self.last_query = query_dsl
        self.last_sort = sort_dsl
        return self.result_to_return


@pytest.fixture
def connector() -> SpyConnector:
    return SpyConnector()


def test_read_many_none_normalizes_to_empty_query(connector: SpyConnector) -> None:
    out = connector.read_many(None)
    assert out == connector.result_to_return
    assert connector.last_query == {}


def test_read_many_shorthand_eq_is_normalized(connector: SpyConnector) -> None:
    out = connector.read_many({"name": "beta"})
    assert out == connector.result_to_return
    assert connector.last_query == {"name": {"$eq": "beta"}}


def test_read_many_multi_field_shorthand_normalizes_to_and(connector: SpyConnector) -> None:
    _ = connector.read_many({"name": "beta", "status": "active"})
    assert connector.last_query == {
        "$and": [
            {"name": {"$eq": "beta"}},
            {"status": {"$eq": "active"}},
        ]
    }


def test_read_many_nested_boolean_nodes_normalize_recursively(connector: SpyConnector) -> None:
    _ = connector.read_many(
        {
            "$or": [
                {"name": "beta"},
                {"$and": [{"status": "active"}, {"score": {"$gt": 10}}]},
            ]
        }
    )
    assert connector.last_query == {
        "$or": [
            {"name": {"$eq": "beta"}},
            {"$and": [{"status": {"$eq": "active"}}, {"score": {"$gt": 10}}]},
        ]
    }


def test_read_many_invalid_query_raises_validation_error(connector: SpyConnector) -> None:
    with pytest.raises(QueryValidationError):
        connector.read_many({"$or": {"name": "beta"}})  # must be list


def test_read_many_does_not_mutate_input(connector: SpyConnector) -> None:
    query = {"name": "beta", "status": "active"}
    before = dict(query)

    _ = connector.read_many(query)

    assert query == before


def test_read_many_passes_normalized_not_raw_shape(connector: SpyConnector) -> None:
    raw = {"name": "beta"}

    _ = connector.read_many(raw)

    assert connector.last_query == {"name": {"$eq": "beta"}}
    assert connector.last_query != raw


def test_read_many_returns_executor_result_passthrough(connector: SpyConnector) -> None:
    connector.result_to_return = [{"id": "x1", "name": "zeta"}]

    out = connector.read_many({"name": "zeta"})

    assert out == [{"id": "x1", "name": "zeta"}]


def test_read_many_passes_normalized_query_and_sort_to_adapter() -> None:
    c = SpyConnector()
    c.read_many(
        query={"status": "active"},
        sort=[{"DueDate": 1}, {"Priority": -1}],
    )
    assert c.last_query == {"status": {"$eq": "active"}}
    assert c.last_sort == [{"DueDate": 1}, {"Priority": -1}]


def test_read_many_defaults_sort_to_empty_list() -> None:
    c = SpyConnector()
    c.read_many(query={"status": "active"})
    assert c.last_sort == []
