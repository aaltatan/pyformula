from typing import Any


class FormulaAlreadyRegisteredError(Exception):
    """Raised when attempting to register a formula name that already exists."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Formula already registered: {name}")


class FormulaNotRegisteredError(Exception):
    """Raised when a requested formula name has not been registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Formula not registered: {name}")


class FormulaNotFoundError(Exception):
    """Raised when a compiled expression references a formula that is not in scope."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Formula not found: {name}")


class InvalidExpressionError(Exception):
    """Raised when an expression structure does not match the compiler schema."""

    def __init__(self, expression: Any, /) -> None:
        super().__init__(f"Invalid expression: {expression}")
