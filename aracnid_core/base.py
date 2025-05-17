from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseConnector(ABC):
    '''Abstract base class for CRUD operations across data sources.'''

    @abstractmethod
    def create(self, record: Dict) -> Dict:
        pass

    @abstractmethod
    def read_one(self, record_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def read_many(self, filters: Optional[Dict] = None) -> List[Dict]:
        pass

    @abstractmethod
    def update(self, record_id: str, changes: Dict) -> Dict:
        pass

    @abstractmethod
    def replace(self, record_id: str, new_record: Dict) -> Dict:
        pass

    @abstractmethod
    def delete_one(self, record_id: str, hard: bool = False) -> bool:
        pass

    @abstractmethod
    def delete_many(self, filters: Optional[Dict] = None, hard: bool = False) -> int:
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        pass
