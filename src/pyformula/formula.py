import decimal
from collections.abc import Callable
from typing import cast

from .models import Number, Operator
from .operator import OPERATORS


class Formula[T]:
    def __init__(
        self,
        fn: Callable[[T], Number],
        *,
        name: str | None = None,
    ) -> None:
        self._fn = fn
        self._name = name

    def __call__(self, obj: T) -> Number:
        return self._fn(obj)

    def __add__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("add", other, reverse=False)

    def __radd__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("add", other, reverse=True)

    def __sub__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("subtract", other, reverse=False)

    def __rsub__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("subtract", other, reverse=True)

    def __mul__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("multiply", other, reverse=False)

    def __rmul__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("multiply", other, reverse=True)

    def __truediv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("divide", other, reverse=False)

    def __rtruediv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("divide", other, reverse=True)

    def __mod__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("modulo", other, reverse=False)

    def __rmod__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("modulo", other, reverse=True)

    def __floordiv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("floor_divide", other, reverse=False)

    def __rfloordiv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("floor_divide", other, reverse=True)

    def __pow__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("power", other, reverse=False)

    def __rpow__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        return self._operate("power", other, reverse=True)

    def __pos__(self) -> "Formula[T]":
        return Formula(self, name=f"+{self}")

    def __neg__(self) -> "Formula[T]":
        return Formula(lambda obj: -self(obj), name=f"-{self}")

    def __abs__(self) -> "Formula[T]":
        return Formula(lambda obj: abs(self(obj)), name=f"|{self}|")

    def __round__(self, ndigits: int | None = None) -> "Formula[T]":
        def inner(obj: T) -> Number:
            value = self(obj)

            if isinstance(value, decimal.Decimal):
                rounded = round(value, ndigits)
                if isinstance(rounded, decimal.Decimal):
                    return rounded

                return decimal.Decimal.from_float(rounded)

            if isinstance(value, float):
                return float(round(value, ndigits))

            return int(round(value, ndigits))

        return Formula(inner, name=f"round({self}, {ndigits})")

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
        operator: Operator,
        other: "Formula[T] | Number",
        *,
        reverse: bool,
    ) -> "Formula[T]":
        operator_fn, symbol = OPERATORS[operator]
        other_fn = other if isinstance(other, Formula) else Formula(lambda _: other)

        def inner(obj: T) -> Number:
            value = self(obj)
            other_value = other_fn(obj)
            return cast(
                "Number",
                (operator_fn(other_value, value)) if reverse else operator_fn(value, other_value),
            )

        return Formula(inner, name=f"({self} {symbol} {other})")
