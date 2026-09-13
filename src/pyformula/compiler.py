import operator
from collections.abc import Callable
from typing import Any

from .exceptions import FormulaNotFoundError
from .formula import Formula
from .models import ExpressionType, FormulaDict, OperatorType, is_formula_dict, is_number

OPERATORS_APPLIERS: dict[OperatorType, Callable[[Formula[Any], Formula[Any]], Formula[Any]]] = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
    "divide": operator.truediv,
    "modulo": operator.mod,
    "floor_divide": operator.floordiv,
    "power": operator.pow,
}


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

    def _compile_expression(self, expression: ExpressionType) -> Formula[T]:

        if is_formula_dict(expression):
            return self.compile(expression)

        if is_number(expression):
            return Formula(lambda _: expression)

        if isinstance(expression, str):
            # TODO(abdullah): implement compile for negative, positive, and abs methods
            # 003
            # positive => +<string_expression>
            # negative => -<string_expression>
            # abs => |<string_expression>|

            if expression not in self._fns:
                raise FormulaNotFoundError(expression)

            return self._fns[expression]

        msg = f"Invalid expression: {expression}"
        raise ValueError(msg)
