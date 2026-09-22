from decimal import Decimal
from typing import Literal, TypeAlias

Number: TypeAlias = Decimal | int | float
Operator: TypeAlias = Literal[
    "add",
    "subtract",
    "multiply",
    "divide",
    "modulo",
    "power",
    "floor_divide",
]
