from collections.abc import Callable, Mapping

from pyvocabulary import Text, Vocabulary

from .exceptions import (
    FormulaAlreadyRegisteredError,
    FormulaNotRegisteredError,
    InvalidFormulaNameError,
)
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
        self._variables: Vocabulary[Formula[T]] = Vocabulary(
            "formula",
            does_not_exist=lambda name, _: FormulaNotRegisteredError(name),
            already_registered=FormulaAlreadyRegisteredError,
            invalid_name=InvalidFormulaNameError,
        )

    @property
    def variables(self) -> Mapping[str, Formula[T]]:
        """Return a read-only view of the visible variables, the ones a compiler may use."""
        return self._variables

    @property
    def labels(self) -> dict[str, Text]:
        """Return the labels of the visible variables that have one, by name."""
        return self._variables.labels

    def __getitem__(self, name: str) -> Formula[T]:
        """Return a registered variable by name, raising if it is hidden or missing."""
        return self._variables[name]

    def variable(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        hidden: bool = False,
        label: Text | None = None,
    ) -> Callable[[Callable[[T], Number]], Formula[T]]:
        """Return a decorator that registers a function as a formula variable.

        Args:
            name: The name used in JSON. Defaults to the function name.
            description: Overrides the docstring.
            hidden: Keep the variable usable from Python, but out of compilers and schemas.
            label: Shown to people instead of the name: a string, or `{"en": ..., "ar": ...}`.

        """

        def decorator(fn: Callable[[T], Number]) -> Formula[T]:
            return self._register(
                fn, name=name, description=description, hidden=hidden, label=label
            )

        return decorator

    def register_variable(
        self,
        fn: Callable[[T], Number],
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        hidden: bool = False,
        label: Text | None = None,
    ) -> None:
        """Register a callable as a named formula variable in the registry."""
        self._register(fn, name=name, description=description, hidden=hidden, label=label)

    def _register(
        self,
        fn: Callable[[T], Number],
        /,
        *,
        name: str | None,
        description: str | None,
        hidden: bool,
        label: Text | None,
    ) -> Formula[T]:
        reg_name = name or fn.__name__
        var = variable(name=reg_name)(fn)

        if description or fn.__doc__:
            var.__doc__ = description or fn.__doc__

        return self._variables.add(reg_name, var, hidden=hidden, label=label)
