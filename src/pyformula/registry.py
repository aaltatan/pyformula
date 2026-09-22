from collections.abc import Callable

from .exceptions import FormulaAlreadyRegisteredError, FormulaNotRegisteredError
from .formula import Formula
from .models import Number
from .variable import variable


class VariablesRegistry[T]:
    """Store named formulas and expose them through a registry-backed lookup API.

    # Examples:
    ```python
    from dataclasses import dataclass

    from pyformula import VariablesRegistry


    @dataclass
    class Rectangular:
        width: float
        height: float


    registry = VariablesRegistry()


    @registry.variable()
    def width(rectangle: Rectangular) -> float:
        return rectangle.width


    @registry.variable()
    def height(rectangle: Rectangular) -> float:
        return rectangle.height


    def main() -> None:
        perimeter = (registry["width"] + registry["height"]) * 2
        area = registry["width"] * registry["height"]

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

    def __init__(self) -> None:
        """Initialize an empty registry with no visible or hidden variables."""
        self._variables: dict[str, Formula[T]] = {}
        self._hidden: set[str] = set()

    @property
    def variables(self) -> dict[str, Formula[T]]:
        """Return the mapping of registered variable names to formula instances."""
        return self._variables

    def __getitem__(self, name: str) -> Formula[T]:
        """Return a registered variable by name, raising if it is hidden or missing."""
        if name in self._hidden or name not in self._variables:
            raise FormulaNotRegisteredError(name)

        return self._variables[name]

    def variable(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        hidden: bool = False,
    ) -> Callable[[Callable[[T], Number]], Formula[T]]:
        """Return a decorator that registers a function as a formula variable."""

        def decorator(fn: Callable[[T], Number]) -> Formula[T]:
            return self._register(fn, name=name, description=description, hidden=hidden)

        return decorator

    def register_variable(
        self,
        fn: Callable[[T], Number],
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        hidden: bool = False,
    ) -> None:
        """Register a callable as a named formula variable in the registry."""
        self._register(fn, name=name, description=description, hidden=hidden)

    def _register(
        self,
        fn: Callable[[T], Number],
        /,
        *,
        name: str | None,
        description: str | None,
        hidden: bool,
    ) -> Formula[T]:
        reg_name = name or fn.__name__

        if reg_name in self._variables:
            raise FormulaAlreadyRegisteredError(reg_name)

        if hidden:
            self._hidden.add(reg_name)

        var = variable(name=reg_name)(fn)

        if description or fn.__doc__:
            var.__doc__ = description or fn.__doc__

        self._variables[reg_name] = var

        return var
