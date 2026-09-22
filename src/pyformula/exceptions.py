from typing import Any


class FormulaAlreadyRegisteredError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Formula already registered: {name}")


class FormulaNotRegisteredError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Formula not registered: {name}")


class FormulaNotFoundError(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Formula not found: {name}")


class InvalidExpressionError(Exception):
    def __init__(self, expression: Any, /) -> None:
        super().__init__(f"Invalid expression: {expression}")
