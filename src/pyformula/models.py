from decimal import Decimal
from typing import Literal, TypeAlias

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
