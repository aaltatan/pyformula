import operator
from collections.abc import Callable
from decimal import Decimal
from typing import Any, TypedDict, TypeGuard

from .exceptions import FormulaNotFoundError
from .formula import Formula
from .models import Operator

OPERATORS_APPLIERS: dict[Operator, Callable[[Formula[Any], Formula[Any]], Formula[Any]]] = {
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


class FormulaDict(TypedDict):
    operator: Operator
    expressions: list["FormulaDict | str | Decimal"]


class FormulaCompiler[T]:
    def __init__(self, fns: dict[str, Formula[T]], /) -> None:
        self._fns = fns

    def compile(self, formula: FormulaDict) -> Formula[T]:
        first_expression = next(iter(formula["expressions"]))
        result = self._compile_expression(first_expression)

        for expression in formula["expressions"][1:]:
            applier = OPERATORS_APPLIERS[formula["operator"]]
            result = applier(result, self._compile_expression(expression))

        return result

    def _compile_expression(self, expression: FormulaDict | str | Decimal) -> Formula[T]:
        if is_formula_dict(expression):
            return self.compile(expression)

        if isinstance(expression, str):
            if expression not in self._fns:
                raise FormulaNotFoundError(expression)

            return self._fns[expression]

        if is_decimal(expression):
            return Formula(lambda _: expression)

        msg = f"Invalid expression: {expression}"
        raise ValueError(msg)


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return (
        isinstance(obj, dict)
        and "operator" in obj
        and "expressions" in obj
        and len(obj.keys()) == 2
    )


def is_decimal(obj: object) -> TypeGuard[Decimal]:
    return isinstance(obj, (int, float, Decimal))
