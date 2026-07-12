from __future__ import annotations

from typing import Protocol, runtime_checkable

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


@runtime_checkable
class BaseConnectorFactory(Protocol):
    """
    A callable fixture/provider that returns a ready-to-test BaseConnector.
    """

    def __call__(self) -> BaseConnector: ...


def assert_base_connector_conformance(
    connector_factory: BaseConnectorFactory,
) -> None:
    """
    Smoke-style conformance entrypoint for external connector repos.
    Intended for use inside pytest tests.
    """
    c = connector_factory()
    assert isinstance(c, BaseConnector)

    caps = c.capabilities
    assert isinstance(caps, dict)
    missing = REQUIRED_CAPABILITY_KEYS - set(caps.keys())
    assert not missing, f"Missing required capability keys: {missing}"

    # minimal required semantics checks that do not require provider-specific data setup
    assert c.read_one("nonexistent-id") is None or isinstance(c.read_one("nonexistent-id"), dict)
    rows = c.read_many()
    assert isinstance(rows, list)


@pytest.mark.contract
def test_required_capabilities_keys(connector: BaseConnector) -> None:
    caps = connector.capabilities
    assert isinstance(caps, dict)
    missing = REQUIRED_CAPABILITY_KEYS - set(caps.keys())
    assert not missing, f"Missing required capability keys: {missing}"


@pytest.mark.contract
def test_read_many_returns_list(connector: BaseConnector) -> None:
    result = connector.read_many()
    assert isinstance(result, list)


@pytest.mark.contract
def test_read_one_validates_input(connector: BaseConnector) -> None:
    with pytest.raises(ValueError):
        connector.read_one("")


@pytest.mark.contract
def test_create_one_validates_input(connector: BaseConnector) -> None:
    with pytest.raises(ValueError):
        connector.create_one("not-a-dict")  # type: ignore[arg-type]


@pytest.mark.contract
def test_update_one_validates_input(connector: BaseConnector) -> None:
    with pytest.raises(ValueError):
        connector.update_one("", {"a": 1})
    with pytest.raises(ValueError):
        connector.update_one("id", "not-a-dict")  # type: ignore[arg-type]


@pytest.mark.contract
def test_replace_one_validates_input(connector: BaseConnector) -> None:
    with pytest.raises(ValueError):
        connector.replace_one("", {"a": 1})
    with pytest.raises(ValueError):
        connector.replace_one("id", "not-a-dict")  # type: ignore[arg-type]


@pytest.mark.contract
def test_delete_one_validates_input(connector: BaseConnector) -> None:
    with pytest.raises(ValueError):
        connector.delete_one("")


@pytest.mark.contract
def test_input_objects_not_mutated(connector: BaseConnector) -> None:
    # These tests assume the connector may raise RuntimeError for missing IDs.
    # We only verify mutation behavior on inputs.
    record = {"name": "alpha"}
    record_before = dict(record)
    try:
        connector.create_one(record)
    except RuntimeError:
        pass
    assert record == record_before

    changes = {"status": "active"}
    changes_before = dict(changes)
    try:
        connector.update_one("missing-id", changes)
    except RuntimeError:
        pass
    assert changes == changes_before

    replacement = {"name": "beta"}
    replacement_before = dict(replacement)
    try:
        connector.replace_one("missing-id", replacement)
    except RuntimeError:
        pass
    assert replacement == replacement_before

    filters = {"x": 1}
    filters_before = dict(filters)
    try:
        connector.read_many(filters)
    except RuntimeError:
        pass
    assert filters == filters_before