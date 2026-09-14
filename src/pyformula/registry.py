from collections.abc import Callable

from .exceptions import FormulaAlreadyRegisteredError, FormulaNotRegisteredError
from .formula import Formula
from .models import NumberType
from .variable import variable


class FormulasRegistry[T]:
    def __init__(self) -> None:
        self._fns: dict[str, Formula[T]] = {}
        self._hidden_fns: set[str] = set()

    @property
    def fns(self) -> dict[str, Formula[T]]:
        return self._fns

    def __getitem__(self, name: str) -> Formula[T]:
        if name in self._hidden_fns or name not in self._fns:
            raise FormulaNotRegisteredError(name)

        return self._fns[name]

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

        if reg_name in self._fns:
            raise FormulaAlreadyRegisteredError(reg_name)

        if hidden:
            self._hidden_fns.add(reg_name)

        formula = variable(name=reg_name)(fn)

        if description or fn.__doc__:
            formula.__doc__ = description or fn.__doc__

        self._fns[reg_name] = formula

        return formula
