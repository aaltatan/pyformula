from collections.abc import Callable
from decimal import Decimal
from typing import Literal, TypeAlias, TypedDict, TypeGuard

NumberType: TypeAlias = Decimal | int | float
OperatorFn: TypeAlias = Callable[[NumberType, NumberType], NumberType]
OperatorType: TypeAlias = Literal[
    "add",
    "subtract",
    "multiply",
    "divide",
    "modulo",
    "power",
    "floor_divide",
    "left_shift",
    "right_shift",
]
ExpressionType: TypeAlias = "FormulaDict | str | NumberType"


class FormulaDict(TypedDict):
    operator: OperatorType
    expressions: list[ExpressionType]


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return (
        isinstance(obj, dict)
        and "operator" in obj
        and "expressions" in obj
        and len(obj.keys()) == 2
    )


def is_number(obj: object) -> TypeGuard[NumberType]:
    return isinstance(obj, (int, float, Decimal))
