from .base import BaseConnector
from .query_dsl import QueryDict, SortSpec

try:
    from importlib.metadata import version as _version
except ImportError:  # pragma: no cover
    from importlib_metadata import version as _version  # type: ignore

__version__ = _version("aracnid-core")

__all__ = ["__version__", "BaseConnector", "QueryDict", "SortSpec"]
