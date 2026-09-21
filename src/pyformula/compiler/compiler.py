# ruff: noqa: PLR0911, C901
from collections.abc import Callable
from decimal import Decimal
from typing import Any, cast

from pyformula import math
from pyformula.exceptions import FormulaNotFoundError
from pyformula.formula import Formula
from pyformula.operator import OPERATORS

from .models import (
    ExpressionType,
    FormulaDict,
    is_absolute_wrapper_dict,
    is_formula_dict,
    is_negative_wrapper_dict,
    is_positive_wrapper_dict,
    is_round_wrapper_dict,
)

MATHS_FNS: dict[str, Callable[[Formula[Any]], Formula[Any]]] = {
    "ceil": math.ceil,
    "floor": math.floor,
    "trunc": math.trunc,
    "sqrt": math.sqrt,
    "cbrt": math.cbrt,
    "exp": math.exp,
    "exp2": math.exp2,
    "expm1": math.expm1,
    "log10": math.log10,
    "log1p": math.log1p,
    "log2": math.log2,
    "sin": math.sin,
    "sinh": math.sinh,
    "asin": math.asin,
    "asinh": math.asinh,
    "cos": math.cos,
    "cosh": math.cosh,
    "acos": math.acos,
    "acosh": math.acosh,
    "tan": math.tan,
    "tanh": math.tanh,
    "atan": math.atan,
    "atanh": math.atanh,
    "degrees": math.degrees,
    "radians": math.radians,
    "erf": math.erf,
    "erfc": math.erfc,
    "gamma": math.gamma,
    "lgamma": math.lgamma,
    "fabs": math.fabs,
    "ulp": math.ulp,
}


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

        for fn_name, math_fn in MATHS_FNS.items():
            if fn_name in expression:
                return math_fn(self._compile_expression(expression[fn_name]))

        msg = f"Invalid expression: {expression}"
        raise TypeError(msg)
