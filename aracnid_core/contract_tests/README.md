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
```

Run:

```bash
pytest -m contract
```

Use environment-gated fixtures for live provider credentials.
