from __future__ import annotations

from typing import Any

import pytest

from aracnid_core.base import BaseConnector


REQUIRED_CAPABILITY_KEYS = {
    "supports_filters",
    "supports_partial_update",
    "supports_replace_one",
    "supports_soft_delete",
    "supports_hard_delete",
    "supports_transactions",
}


class _RuntimeFailure(Exception):
    pass


class DummyConnector(BaseConnector):
    """
    Contract-test dummy implementation.
    This provides deterministic behavior to validate baseline contract expectations.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._counter = 0
        self._force_runtime_error = False

    @property
    def capabilities(self) -> dict[str, bool]:
        return {
            "supports_filters": True,
            "supports_partial_update": True,
            "supports_replace_one": True,
            "supports_soft_delete": True,
            "supports_hard_delete": True,
            "supports_transactions": False,
            # optional keys (allowed)
            "supports_create_many": False,
            "supports_update_many": False,
            "supports_replace_many": False,
            "supports_delete_many": False,
        }

    def _maybe_runtime_error(self) -> None:
        if self._force_runtime_error:
            try:
                raise _RuntimeFailure("simulated upstream/provider failure")
            except _RuntimeFailure as exc:
                raise RuntimeError("Provider failure") from exc

    def create_one(self, record: dict[str, Any]) -> dict[str, Any]:
        self._maybe_runtime_error()
        if not isinstance(record, dict):
            raise ValueError("record must be a dict")
        self._counter += 1
        rid = f"rec_{self._counter}"
        stored = {"id": rid, "fields": dict(record)}
        self._store[rid] = stored
        return dict(stored)

    def read_one(self, record_id: str) -> dict[str, Any] | None:
        self._maybe_runtime_error()
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        item = self._store.get(record_id)
        return dict(item) if item else None

    def read_many(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self._maybe_runtime_error()
        if filters is not None and not isinstance(filters, dict):
            raise ValueError("filters must be a dict or None")

        rows = list(self._store.values())
        if not filters:
            return [dict(r) for r in rows]

        def match(row: dict[str, Any]) -> bool:
            fields = row.get("fields", {})
            return all(fields.get(k) == v for k, v in filters.items())

        return [dict(r) for r in rows if match(r)]

    def update_one(self, record_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        self._maybe_runtime_error()
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        if not isinstance(changes, dict):
            raise ValueError("changes must be a dict")
        if record_id not in self._store:
            raise RuntimeError("Provider failure: record not found for update")
        self._store[record_id]["fields"].update(dict(changes))
        return dict(self._store[record_id])

    def replace_one(self, record_id: str, new_record: dict[str, Any]) -> dict[str, Any]:
        self._maybe_runtime_error()
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        if not isinstance(new_record, dict):
            raise ValueError("new_record must be a dict")
        if record_id not in self._store:
            raise RuntimeError("Provider failure: record not found for replace")
        self._store[record_id]["fields"] = dict(new_record)
        return dict(self._store[record_id])

    def delete_one(self, record_id: str, hard: bool = False) -> bool:
        self._maybe_runtime_error()
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError("record_id must be a non-empty string")
        if record_id not in self._store:
            return False
        if hard:
            del self._store[record_id]
            return True
        self._store[record_id]["fields"]["is_deleted"] = True
        return True


@pytest.fixture
def connector() -> DummyConnector:
    return DummyConnector()


def test_capabilities_contains_required_keys(connector: DummyConnector) -> None:
    caps = connector.capabilities
    assert isinstance(caps, dict)
    missing = REQUIRED_CAPABILITY_KEYS - set(caps.keys())
    assert not missing, f"Missing required capability keys: {missing}"


def test_read_one_not_found_returns_none(connector: DummyConnector) -> None:
    assert connector.read_one("rec_missing") is None


def test_read_many_returns_list(connector: DummyConnector) -> None:
    result = connector.read_many()
    assert isinstance(result, list)
    assert result == []


def test_create_one_validates_input(connector: DummyConnector) -> None:
    with pytest.raises(ValueError):
        connector.create_one("not-a-dict")  # type: ignore[arg-type]


def test_read_one_validates_input(connector: DummyConnector) -> None:
    with pytest.raises(ValueError):
        connector.read_one("")  # empty


def test_update_one_validates_input(connector: DummyConnector) -> None:
    with pytest.raises(ValueError):
        connector.update_one("", {"a": 1})
    with pytest.raises(ValueError):
        connector.update_one("rec_1", "not-a-dict")  # type: ignore[arg-type]


def test_replace_one_validates_input(connector: DummyConnector) -> None:
    with pytest.raises(ValueError):
        connector.replace_one("", {"a": 1})
    with pytest.raises(ValueError):
        connector.replace_one("rec_1", "not-a-dict")  # type: ignore[arg-type]


def test_delete_one_validates_input(connector: DummyConnector) -> None:
    with pytest.raises(ValueError):
        connector.delete_one("")


def test_runtime_failures_are_runtimeerror(connector: DummyConnector) -> None:
    connector._force_runtime_error = True
    with pytest.raises(RuntimeError):
        connector.create_one({"x": 1})
    with pytest.raises(RuntimeError):
        connector.read_one("rec_1")
    with pytest.raises(RuntimeError):
        connector.read_many()
    with pytest.raises(RuntimeError):
        connector.update_one("rec_1", {"x": 2})
    with pytest.raises(RuntimeError):
        connector.replace_one("rec_1", {"x": 3})
    with pytest.raises(RuntimeError):
        connector.delete_one("rec_1")


def test_input_objects_not_mutated(connector: DummyConnector) -> None:
    payload = {"name": "alpha"}
    payload_before = dict(payload)
    created = connector.create_one(payload)
    assert payload == payload_before
    assert created["fields"]["name"] == "alpha"

    rid = created["id"]

    changes = {"status": "active"}
    changes_before = dict(changes)
    connector.update_one(rid, changes)
    assert changes == changes_before

    replacement = {"name": "beta"}
    replacement_before = dict(replacement)
    connector.replace_one(rid, replacement)
    assert replacement == replacement_before

    filters = {"name": "beta"}
    filters_before = dict(filters)
    _ = connector.read_many(filters)
    assert filters == filters_before


def test_delete_one_returns_bool(connector: DummyConnector) -> None:
    created = connector.create_one({"x": 1})
    rid = created["id"]

    assert connector.delete_one(rid, hard=False) is True
    # second delete may be false depending on semantics; this dummy returns True until hard delete
    assert isinstance(connector.delete_one(rid, hard=True), bool)