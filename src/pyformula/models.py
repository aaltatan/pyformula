from decimal import Decimal
from typing import Literal, TypeAlias, TypeGuard

NumberType: TypeAlias = Decimal | int | float
OperatorType: TypeAlias = Literal[
    "add",
    "subtract",
    "multiply",
    "divide",
    "modulo",
    "power",
    "floor_divide",
]


def is_number(obj: object) -> TypeGuard[NumberType]:
    return isinstance(obj, (int, float, Decimal)) and not isinstance(obj, bool)
