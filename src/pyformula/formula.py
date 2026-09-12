import operator
from collections.abc import Callable
from decimal import Decimal

from .models import Operator

OPERATORS: dict[Operator, Callable[[Decimal, Decimal], Decimal]] = {
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


class Formula[T]:
    def __init__(self, fn: Callable[[T], Decimal]) -> None:
        self._fn = fn

    def __call__(self, obj: T) -> Decimal:
        return self._fn(obj)

    def __add__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("add", other, reverse=False)

    def __radd__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("add", other, reverse=True)

    def __sub__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("subtract", other, reverse=False)

    def __rsub__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("subtract", other, reverse=True)

    def __mul__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("multiply", other, reverse=False)

    def __rmul__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("multiply", other, reverse=True)

    def __truediv__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("divide", other, reverse=False)

    def __rtruediv__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("divide", other, reverse=True)

    def __mod__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("modulo", other, reverse=False)

    def __rmod__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("modulo", other, reverse=True)

    def __floordiv__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("floor_divide", other, reverse=False)

    def __rfloordiv__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("floor_divide", other, reverse=True)

    def __pow__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("power", other, reverse=False)

    def __rpow__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("power", other, reverse=True)

    def __lshift__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("left_shift", other, reverse=False)

    def __rlshift__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("left_shift", other, reverse=True)

    def __rshift__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("right_shift", other, reverse=False)

    def __rrshift__(self, other: "Formula[T] | Decimal") -> "Formula[T]":
        return self._operate("right_shift", other, reverse=True)

    def _operate(
        self,
        operator: Operator,
        other: "Formula[T] | Decimal",
        *,
        reverse: bool,
    ) -> "Formula[T]":
        operator_fn = OPERATORS[operator]
        other_fn = other if isinstance(other, Formula) else Formula(lambda _: other)

        def inner(obj: T) -> Decimal:
            value = self(obj)
            other_value = other_fn(obj)
            return operator_fn(other_value, value) if reverse else operator_fn(value, other_value)

        return Formula(inner)
