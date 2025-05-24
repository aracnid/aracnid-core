from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MetadataBase(BaseModel):
    """Base model for system metadata associated with records.

    This includes:
    - is_deleted: Logical deletion flag (default is False)
    - synced_at: Timestamp of last successful sync (optional)
    """
    is_deleted: Optional[bool] = False
    synced_at: Optional[datetime] = None


class SourceBase(BaseModel):
    """Base model for source information associated with records.

    This includes:
    - type: Type of source, specific to the connector.
    - id: Unique identifier for the source (optional)
    - created_at: Timestamp when the source was created (optional)
    - modified_at: Timestamp when the source was last modified (optional)
    """
    type: str
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

class RecordBase(BaseModel):
    """Base model for all records, blending system fields with source fields.

    System-managed fields:
    - id: Universal record identifier (may match source ID)
    - is_deleted: Logical deletion flag (not always supported by source)
    - synced_at: Timestamp of last successful sync
    - metadata: Connector-specific information (e.g., source IDs, timestamps)
    """
    id: Optional[str] = None
    metadata: MetadataBase = MetadataBase()
    source: SourceBase
