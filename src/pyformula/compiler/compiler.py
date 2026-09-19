# ruff: noqa: PLR0911
import math
from typing import cast

from pyformula.exceptions import FormulaNotFoundError
from pyformula.formula import Formula
from pyformula.math import wrap
from pyformula.models import is_number
from pyformula.operator import OPERATORS

from .checkers import (
    is_absolute_wrapper_dict,
    is_ceil_wrapper_dict,
    is_floor_wrapper_dict,
    is_formula_dict,
    is_negative_wrapper_dict,
    is_positive_wrapper_dict,
    is_round_wrapper_dict,
    is_trunc_wrapper_dict,
)
from .models import ExpressionType, FormulaDict


class FormulaCompiler[T]:
    def __init__(self, fns: dict[str, Formula[T]], /) -> None:
        self._fns = fns

    def compile(self, formula: FormulaDict) -> Formula[T]:
        first_expression = next(iter(formula["expressions"]))
        result = self._compile_expression(first_expression)

        for expression in formula["expressions"][1:]:
            applier, _ = OPERATORS[formula["operator"]]
            result = applier(result, self._compile_expression(expression))

        return cast("Formula[T]", result)

    def _compile_expression(self, expression: ExpressionType) -> Formula[T]:
        if is_formula_dict(expression):
            return self.compile(expression)

        if is_number(expression):
            return Formula(lambda _: expression)

        return self._compile_wrapped_expression(expression)

    def _compile_wrapped_expression(self, expression: ExpressionType) -> Formula[T]:
        if is_positive_wrapper_dict(expression):
            return +self._compile_wrapped_expression(expression["positive"])

        if is_negative_wrapper_dict(expression):
            return -self._compile_wrapped_expression(expression["negative"])

        if is_absolute_wrapper_dict(expression):
            return abs(self._compile_wrapped_expression(expression["absolute"]))

        if is_round_wrapper_dict(expression):
            return round(
                self._compile_wrapped_expression(expression["round"]),
                ndigits=expression["ndigits"],
            )

        if is_floor_wrapper_dict(expression):
            return wrap(self._compile_wrapped_expression(expression["floor"]), math_fn=math.floor)

        if is_ceil_wrapper_dict(expression):
            return wrap(self._compile_wrapped_expression(expression["ceil"]), math_fn=math.ceil)

        if is_trunc_wrapper_dict(expression):
            return wrap(self._compile_wrapped_expression(expression["trunc"]), math_fn=math.trunc)

        if not isinstance(expression, str):
            msg = f"Invalid expression: {expression}"
            raise TypeError(msg)

        if expression not in self._fns:
            raise FormulaNotFoundError(expression)

        return self._fns[expression]
