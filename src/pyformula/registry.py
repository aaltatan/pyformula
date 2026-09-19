from collections.abc import Callable

from .exceptions import FormulaAlreadyRegisteredError, FormulaNotRegisteredError
from .formula import Formula
from .models import NumberType
from .variable import variable


class VariablesRegistry[T]:
    def __init__(self) -> None:
        self._variables: dict[str, Formula[T]] = {}
        self._hidden: set[str] = set()

    @property
    def variables(self) -> dict[str, Formula[T]]:
        return self._variables

    def __getitem__(self, name: str) -> Formula[T]:
        if name in self._hidden or name not in self._variables:
            raise FormulaNotRegisteredError(name)

        return self._variables[name]

    def variable(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        hidden: bool = False,
    ) -> Callable[[Callable[[T], NumberType]], Formula[T]]:
        def decorator(fn: Callable[[T], NumberType]) -> Formula[T]:
            return self._register(fn, name=name, description=description, hidden=hidden)

        return decorator

    def register_variable(
        self,
        fn: Callable[[T], NumberType],
        /,
        *,
        name: str | None = None,
        description: str | None = None,
        hidden: bool = False,
    ) -> Formula[T]:
        return self._register(fn, name=name, description=description, hidden=hidden)

    def _register(
        self,
        fn: Callable[[T], NumberType],
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
