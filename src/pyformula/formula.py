import decimal
from collections.abc import Callable
from typing import cast

from .models import Number, Operator
from .operator import OPERATORS


class Formula[T]:
    """Represent a lazily evaluated numeric transformation over an input object.

    Formula instances can be composed with arithmetic operators, wrapped with
    mathematical functions, and later evaluated by calling the formula with an
    instance of the source type.

    # Examples:
    ```python
    from dataclasses import dataclass
    from pyformula import Formula


    @dataclass
    class Rectangular:
        width: float
        height: float


    def main() -> None:
        width = Formula[Rectangular](lambda rectangle: rectangle.width)
        height = Formula[Rectangular](lambda rectangle: rectangle.height)

        perimeter = (width + height) * 2
        area = width * height

        r1 = Rectangular(width=10, height=20)
        print(perimeter(r1))  # 60.0
        print(area(r1))  # 200.0

        r2 = Rectangular(width=5, height=10)
        print(perimeter(r2))  # 30.0
        print(area(r2))  # 50.0


    if __name__ == "__main__":
        main()
    ```
    """

    def __init__(
        self,
        fn: Callable[[T], Number],
        *,
        name: str | None = None,
    ) -> None:
        """Create a formula from a callable that derives a numeric value."""
        self._fn = fn
        self._name = name

    def __call__(self, obj: T) -> Number:
        """Evaluate the formula against the provided object."""
        return self._fn(obj)

    def __add__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the sum of this formula and another value or formula."""
        return self._operate("add", other, reverse=False)

    def __radd__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the sum of another value and this formula."""
        return self._operate("add", other, reverse=True)

    def __sub__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return this formula minus another value or formula."""
        return self._operate("subtract", other, reverse=False)

    def __rsub__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return another value minus this formula."""
        return self._operate("subtract", other, reverse=True)

    def __mul__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the product of this formula and another value or formula."""
        return self._operate("multiply", other, reverse=False)

    def __rmul__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return another value multiplied by this formula."""
        return self._operate("multiply", other, reverse=True)

    def __truediv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return this formula divided by another value or formula."""
        return self._operate("divide", other, reverse=False)

    def __rtruediv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return another value divided by this formula."""
        return self._operate("divide", other, reverse=True)

    def __mod__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the modulo of this formula with another value or formula."""
        return self._operate("modulo", other, reverse=False)

    def __rmod__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the modulo of another value with this formula."""
        return self._operate("modulo", other, reverse=True)

    def __floordiv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the floor division of this formula and another value or formula."""
        return self._operate("floor_divide", other, reverse=False)

    def __rfloordiv__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return the floor division of another value by this formula."""
        return self._operate("floor_divide", other, reverse=True)

    def __pow__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return this formula raised to the power of another value or formula."""
        return self._operate("power", other, reverse=False)

    def __rpow__(self, other: "Formula[T] | Number", /) -> "Formula[T]":
        """Return another value raised to the power of this formula."""
        return self._operate("power", other, reverse=True)

    def __pos__(self) -> "Formula[T]":
        """Return a formula that preserves the value of the current formula."""
        return Formula(self, name=f"+{self}")

    def __neg__(self) -> "Formula[T]":
        """Return a formula that negates the current formula's value."""
        return Formula(lambda obj: -self(obj), name=f"-{self}")

    def __abs__(self) -> "Formula[T]":
        """Return a formula that computes the absolute value of this formula."""
        return Formula(lambda obj: abs(self(obj)), name=f"|{self}|")

    def __round__(self, ndigits: int | None = None) -> "Formula[T]":
        """Return a formula that rounds the current result to the given precision."""

        def inner(obj: T) -> Number:
            value = self(obj)

            if isinstance(value, decimal.Decimal):
                rounded = round(value, ndigits)
                if isinstance(rounded, decimal.Decimal):
                    return rounded

                return decimal.Decimal(rounded)

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
