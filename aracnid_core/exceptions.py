"""Exception types for aracnid-core.
"""
class AracnidError(Exception):
    """Base exception type for aracnid-core.
    """
    pass


class QueryValidationError(AracnidError, ValueError):
    """Raised when a query does not conform to Query DSL v1.
    """
    pass


class UnsupportedQueryError(AracnidError, NotImplementedError):
    """Raised when a valid query contains an operator or construct not supported by a specific adapter.
    """

    def __init__(
        self,
        adapter: str,
        operator: str,
        field: str | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the exception with details about the unsupported query.
        
        Args:
            adapter (str): The name of the adapter that does not support the operator.
            operator (str): The unsupported operator.
            field (str | None): The field on which the operator was attempted, if applicable.
            message (str | None): Optional custom message for the exception.
        """
        detail = (
            message
            or f"Adapter '{adapter}' does not support operator '{operator}'"
            + (f" on field '{field}'" if field else "")
        )
        super().__init__(detail)
        self.adapter = adapter
        self.operator = operator
        self.field = field


class QueryCompilationError(AracnidError, RuntimeError):
    """Raised when query compilation fails unexpectedly.
    """
    pass
