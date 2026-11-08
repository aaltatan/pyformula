"""Exceptions raised by pyformula.

Every exception derives from `PyformulaError`, so callers can catch the whole
family at once.
"""

from collections.abc import Iterable
from typing import Any


class PyformulaError(Exception):
    """Base class for every exception raised by pyformula."""


class FormulaAlreadyRegisteredError(PyformulaError):
    """Raised when attempting to register a formula name that already exists."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Formula already registered: {name}")


class FormulaNotRegisteredError(PyformulaError):
    """Raised when a requested formula name has not been registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Formula not registered: {name}")


class FormulaNotFoundError(PyformulaError):
    """Raised when a compiled expression references a formula that is not in scope.

    Example:
    ```python
    >>> str(FormulaNotFoundError("pricee", ["price", "quantity"]))
    'Formula not found: pricee. Available formulas: price, quantity'

    ```

    """

    def __init__(self, name: str, available: Iterable[str] | None = None) -> None:
        msg = f"Formula not found: {name}"

        if available is not None:
            msg += f". Available formulas: {', '.join(available) or '(none)'}"

        super().__init__(msg)


class InvalidExpressionError(PyformulaError):
    """Raised when an expression structure does not match the compiler schema."""

    def __init__(self, expression: Any, /) -> None:
        super().__init__(f"Invalid expression: {expression}")
