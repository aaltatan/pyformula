# ruff: noqa: PLR0911, C901
from decimal import Decimal
from typing import cast

from pyformula.exceptions import FormulaNotFoundError
from pyformula.formula import Formula
from pyformula.math import ceil, floor, trunc
from pyformula.operator import OPERATORS

from .models import (
    ExpressionType,
    FormulaDict,
    is_absolute_wrapper_dict,
    is_ceil_wrapper_dict,
    is_floor_wrapper_dict,
    is_formula_dict,
    is_negative_wrapper_dict,
    is_positive_wrapper_dict,
    is_round_wrapper_dict,
    is_trunc_wrapper_dict,
)


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
        # -----------------------
        # formula case
        # -----------------------

        if is_formula_dict(expression):
            return self.compile(expression)

        # -----------------------
        # number case
        # -----------------------

        if isinstance(expression, (int, float, Decimal)):
            return Formula(lambda _: expression)

        # -----------------------
        # string case
        # -----------------------

        if isinstance(expression, str) and expression not in self._fns:
            raise FormulaNotFoundError(expression)

        if isinstance(expression, str):
            return self._fns[expression]

        # -----------------------
        # basic operators
        # -----------------------

        if is_positive_wrapper_dict(expression):
            return +self._compile_expression(expression["positive"])

        if is_negative_wrapper_dict(expression):
            return -self._compile_expression(expression["negative"])

        if is_absolute_wrapper_dict(expression):
            return abs(self._compile_expression(expression["absolute"]))

        if is_round_wrapper_dict(expression):
            return round(
                self._compile_expression(expression["round"]),
                ndigits=expression["ndigits"],
            )

        # -----------------------
        # math operators
        # -----------------------

        if is_floor_wrapper_dict(expression):
            return floor(self._compile_expression(expression["floor"]))

        if is_ceil_wrapper_dict(expression):
            return ceil(self._compile_expression(expression["ceil"]))

        if is_trunc_wrapper_dict(expression):
            return trunc(self._compile_expression(expression["trunc"]))

        msg = f"Invalid expression: {expression}"
        raise TypeError(msg)
