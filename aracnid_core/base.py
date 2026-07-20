from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .query_dsl import QueryDict, normalize_query, normalize_sort, SortSpec


class BaseConnector(ABC):
    """
    BaseConnector v1 contract.

    Required methods:
      - create_one
      - read_one
      - read_many
      - update_one
      - replace_one
      - delete_one

    Required property:
      - capabilities
    """
    @property
    @abstractmethod
    def capabilities(self) -> dict[str, bool]:
        """Provides a dictionary of the connector's capabilities.
        
        Required capability keys:
          - supports_query
          - supports_partial_update
          - supports_replace_one
          - supports_soft_delete
          - supports_hard_delete
          - supports_transactions
        """
        raise NotImplementedError


    @abstractmethod
    def create_one(self, record: dict[str, Any]) -> dict[str, Any]:
        """Create a single record in the data store.
        """
        raise NotImplementedError


    @abstractmethod
    def read_one(self, record_id: str) -> dict[str, Any] | None:
        """Read a single record by its unique identifier.
        """
        raise NotImplementedError


    def read_many(
        self,
        query: QueryDict | None = None,
        sort: SortSpec | None = None,
    ) -> list[dict]:
        """Read multiple records using Query DSL v1.

        The query and sort are normalized to canonical explicit form before
        adapter-specific execution.
        """
        query_dsl = normalize_query(query)
        sort_dsl = normalize_sort(sort)
        return self._read_many_normalized(query_dsl, sort_dsl)



    @abstractmethod
    def update_one(self, record_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        """Update a single record by its unique identifier with the given changes.
        """
        raise NotImplementedError


    @abstractmethod
    def replace_one(self, record_id: str, new_record: dict[str, Any]) -> dict[str, Any]:
        """Replace a single record by its unique identifier with a new record.
        """
        raise NotImplementedError


    @abstractmethod
    def delete_one(self, record_id: str, hard: bool = False) -> bool:
        """Delete a single record by its unique identifier.
        
        If `hard` is True, perform a hard delete; otherwise, perform a soft delete if supported.
        """
        raise NotImplementedError
    

    @abstractmethod
    def _read_many_normalized(
        self,
        query_dsl: QueryDict,
        sort_dsl: SortSpec,
    ) -> list[dict]:
        """Execute normalized Query DSL + sort spec and return records.

        Implementations should assume both are already validated
        and normalized.
        """
        raise NotImplementedError    