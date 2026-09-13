import operator
from collections.abc import Callable
from decimal import Decimal
from typing import Any, cast

from .formula import Formula
from .models import NumberType, OperatorFn, OperatorType

OPERATORS_APPLIERS: dict[OperatorType, Callable[[Formula[Any], Formula[Any]], Formula[Any]]] = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
    "divide": operator.truediv,
    "modulo": operator.mod,
    "floor_divide": operator.floordiv,
    "power": operator.pow,
    "left_shift": operator.lshift,
    "right_shift": operator.rshift,
}


def _safe_operate(fn: OperatorFn) -> OperatorFn:
    def inner(a: NumberType, b: NumberType) -> NumberType:
        if isinstance(a, Decimal) and isinstance(b, float):
            b = Decimal.from_float(b)

        if isinstance(b, Decimal) and isinstance(a, float):
            a = Decimal.from_float(a)

        return fn(a, b)

    return inner


OPERATORS_SAFE_FUNCTIONS: dict[OperatorType, OperatorFn] = {
    "add": _safe_operate(cast("OperatorFn", operator.add)),
    "subtract": _safe_operate(cast("OperatorFn", operator.sub)),
    "multiply": _safe_operate(cast("OperatorFn", operator.mul)),
    "divide": _safe_operate(operator.truediv),
    "floor_divide": _safe_operate(operator.floordiv),
    "modulo": _safe_operate(cast("OperatorFn", operator.mod)),
    "power": _safe_operate(operator.pow),
    "left_shift": _safe_operate(operator.lshift),
    "right_shift": _safe_operate(operator.rshift),
}
