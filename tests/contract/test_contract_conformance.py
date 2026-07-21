from __future__ import annotations

import pytest

from aracnid_core.base import QueryDict, BaseConnector
from aracnid_core.contract_tests import base_connector_contract as contract_tests
from aracnid_core.contract_tests import query_dsl_sort_contract as sort_contract_tests
from aracnid_core.contract_tests import query_dsl_temporal_contract as temporal_contract_tests
from aracnid_core.query_dsl import SortSpec


class DummyConnector(BaseConnector):
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

    def create_one(self, record):
        if not isinstance(record, dict):
            raise ValueError
        return {"id": "1", "fields": dict(record)}

    def read_one(self, record_id):
        if not isinstance(record_id, str) or not record_id:
            raise ValueError
        return None

    def update_one(self, record_id, changes):
        if not isinstance(record_id, str) or not record_id:
            raise ValueError
        if not isinstance(changes, dict):
            raise ValueError
        raise RuntimeError("not found")

    def replace_one(self, record_id, new_record):
        if not isinstance(record_id, str) or not record_id:
            raise ValueError
        if not isinstance(new_record, dict):
            raise ValueError
        raise RuntimeError("not found")

    def delete_one(self, record_id, hard=False):
        if not isinstance(record_id, str) or not record_id:
            raise ValueError
        return False

    def _read_many_normalized(self, query_dsl: QueryDict, sort_dsl: SortSpec) -> list[dict]:
        if query_dsl is not None and not isinstance(query_dsl, dict):
            raise ValueError
        return []


@pytest.fixture
def connector() -> BaseConnector:
    return DummyConnector()


# Re-export shared tests so pytest discovers them in this repo
test_required_capabilities_keys = contract_tests.test_required_capabilities_keys
test_read_many_returns_list = contract_tests.test_read_many_returns_list
test_read_one_validates_input = contract_tests.test_read_one_validates_input
test_create_one_validates_input = contract_tests.test_create_one_validates_input
test_update_one_validates_input = contract_tests.test_update_one_validates_input
test_replace_one_validates_input = contract_tests.test_replace_one_validates_input
test_delete_one_validates_input = contract_tests.test_delete_one_validates_input
test_input_objects_not_mutated = contract_tests.test_input_objects_not_mutated

# Query DSL Sort contract tests
test_normalize_sort_accepts_none = (
    sort_contract_tests.test_normalize_sort_accepts_none
)
test_normalize_sort_accepts_single_and_multi = (
    sort_contract_tests.test_normalize_sort_accepts_single_and_multi
)
test_normalize_sort_rejects_invalid_shapes = (
    sort_contract_tests.test_normalize_sort_rejects_invalid_shapes
)
test_normalize_sort_rejects_duplicate_fields = (
    sort_contract_tests.test_normalize_sort_rejects_duplicate_fields
)

# Temporal Query DSL contract tests
test_normalize_query_accepts_timezone_aware_datetime_local_tz = (
    temporal_contract_tests.test_normalize_query_accepts_timezone_aware_datetime_local_tz
)
test_normalize_query_accepts_timezone_aware_datetime_utc = (
    temporal_contract_tests.test_normalize_query_accepts_timezone_aware_datetime_utc
)
test_normalize_query_rejects_naive_datetime = (
    temporal_contract_tests.test_normalize_query_rejects_naive_datetime
)
test_normalize_query_date_literal_still_valid = (
    temporal_contract_tests.test_normalize_query_date_literal_still_valid
)