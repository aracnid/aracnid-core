# BaseConnector Contract Tests

This package provides reusable conformance tests for `BaseConnector` implementations.

## In a connector repo (example: i-airtable)

1. Add `aracnid-core` as a test dependency.
2. Create a `connector` fixture returning your configured connector instance.
3. Re-use tests from `aracnid_core.contract_tests.base_connector_contract`.

Example:

```python
# tests/contract/test_conformance.py
import pytest

from aracnid_core.contract_tests import base_connector_contract as contract_tests
from i_airtable.connector import AirtableConnector


@pytest.fixture
def connector():
    return AirtableConnector(
        # test credentials/config
    )


# Re-export shared tests into local pytest discovery
test_required_capabilities_keys = contract_tests.test_required_capabilities_keys
test_read_many_returns_list = contract_tests.test_read_many_returns_list
test_read_one_validates_input = contract_tests.test_read_one_validates_input
test_create_one_validates_input = contract_tests.test_create_one_validates_input
test_update_one_validates_input = contract_tests.test_update_one_validates_input
test_replace_one_validates_input = contract_tests.test_replace_one_validates_input
test_delete_one_validates_input = contract_tests.test_delete_one_validates_input
test_input_objects_not_mutated = contract_tests.test_input_objects_not_mutated
test_update_many_returns_non_negative_count_when_supported = (
    contract_tests.test_update_many_returns_non_negative_count_when_supported
)
test_replace_many_returns_non_negative_count_when_supported = (
    contract_tests.test_replace_many_returns_non_negative_count_when_supported
)
test_delete_many_returns_non_negative_count_when_supported = (
    contract_tests.test_delete_many_returns_non_negative_count_when_supported
)
```

Run:

```bash
pytest -m contract
```

Use environment-gated fixtures for live provider credentials.

To check that an update cannot create a record, also re-export
`test_update_one_missing_record_creates_nothing`. Supply a `missing_record_id`
fixture with a valid provider-native ID known to be absent and a
`valid_update_changes` fixture with a payload valid for the test store. Use an
isolated store where `read_many()` lists all records and concurrent writes are
excluded.

Test write outcome classification with provider-specific fixtures that simulate
a confirmed rejection and a lost response after dispatch.
