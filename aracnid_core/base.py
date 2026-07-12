from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


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
        """
        Required capability keys:
          - supports_filters
          - supports_partial_update
          - supports_replace_one
          - supports_soft_delete
          - supports_hard_delete
          - supports_transactions
        """
        raise NotImplementedError

    @abstractmethod
    def create_one(self, record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def read_one(self, record_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def read_many(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def update_one(self, record_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def replace_one(self, record_id: str, new_record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete_one(self, record_id: str, hard: bool = False) -> bool:
        raise NotImplementedError
    