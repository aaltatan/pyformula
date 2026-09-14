import operator
from collections.abc import Callable
from decimal import Decimal
from typing import TypeAlias, cast

from .models import NumberType, OperatorType

OperatorFn: TypeAlias = Callable[[NumberType, NumberType], NumberType]


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
}

OPERATORS_SYMBOLS: dict[OperatorType, str] = {
    "add": "+",
    "subtract": "-",
    "multiply": "*",
    "divide": "/",
    "floor_divide": "//",
    "modulo": "%",
    "power": "**",
}


class Formula[T]:
    def __init__(
        self,
        fn: Callable[[T], NumberType],
        *,
        name: str | None = None,
    ) -> None:
        self._fn = fn
        self._name = name

    def __call__(self, obj: T) -> NumberType:
        return self._fn(obj)

    def __add__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("add", other, reverse=False)

    def __radd__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("add", other, reverse=True)

    def __sub__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("subtract", other, reverse=False)

    def __rsub__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("subtract", other, reverse=True)

    def __mul__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("multiply", other, reverse=False)

    def __rmul__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("multiply", other, reverse=True)

    def __truediv__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("divide", other, reverse=False)

    def __rtruediv__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("divide", other, reverse=True)

    def __mod__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("modulo", other, reverse=False)

    def __rmod__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("modulo", other, reverse=True)

    def __floordiv__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("floor_divide", other, reverse=False)

    def __rfloordiv__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("floor_divide", other, reverse=True)

    def __pow__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("power", other, reverse=False)

    def __rpow__(self, other: "Formula[T] | NumberType") -> "Formula[T]":
        return self._operate("power", other, reverse=True)

    def __pos__(self) -> "Formula[T]":
        return Formula(self, name=f"+{self}")

    def __neg__(self) -> "Formula[T]":
        return Formula(lambda obj: -self(obj), name=f"-{self}")

    def __abs__(self) -> "Formula[T]":
        return Formula(lambda obj: abs(self(obj)), name=f"|{self}|")

    def __str__(self) -> str:
        if self._name is not None:
            return self._name

        if self._fn.__name__ == "<lambda>":
            return "anonymous"

        return self._fn.__name__

    def __repr__(self) -> str:
        return f"Formula({self})"

    def _operate(
        self,
        operator: OperatorType,
        other: "Formula[T] | NumberType",
        *,
        reverse: bool,
    ) -> "Formula[T]":
        operator_fn = OPERATORS_SAFE_FUNCTIONS[operator]
        other_fn = other if isinstance(other, Formula) else Formula(lambda _: other)

        def inner(obj: T) -> NumberType:
            value = self(obj)
            other_value = other_fn(obj)
            return operator_fn(other_value, value) if reverse else operator_fn(value, other_value)

        return Formula(inner, name=f"({self} {OPERATORS_SYMBOLS[operator]} {other})")
