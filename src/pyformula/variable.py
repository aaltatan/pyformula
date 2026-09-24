from collections.abc import Callable
from functools import update_wrapper

from .formula import Formula
from .models import Number


def variable[T](*, name: str | None = None) -> Callable[[Callable[[T], Number]], Formula[T]]:
    """Return a decorator that turns a function into a named formula.

    The original function metadata is preserved, while the wrapped callable is
    exposed as a lazily evaluated formula object.

    # Examples:
    ```python
    from dataclasses import dataclass

    from pyformula import variable


    @dataclass
    class Rectangular:
        width: float
        height: float


    @variable()
    def width(rectangle: Rectangular) -> float:
        return rectangle.width


    @variable()
    def height(rectangle: Rectangular) -> float:
        return rectangle.height


    def main() -> None:
        perimeter = (width + height) * 2

        r1 = Rectangular(width=10, height=20)
        print(perimeter(r1))  # 60.0

        r2 = Rectangular(width=5, height=10)
        print(perimeter(r2))  # 30.0


    if __name__ == "__main__":
        main()
    ```

    """

    def decorator(fn: Callable[[T], Number]) -> Formula[T]:
        formula = Formula(fn, name=name or fn.__name__)
        update_wrapper(formula, fn)
        return formula

    return decorator
