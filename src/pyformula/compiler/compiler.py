from collections.abc import Callable
from decimal import Decimal
from typing import Any, cast

from pyformula import math
from pyformula.exceptions import FormulaNotFoundError
from pyformula.formula import Formula
from pyformula.operator import OPERATORS

from .models import Expression, FormulaDict, is_formula_dict, is_round_wrapper_dict

WRAPPER_FNS: dict[str, Callable[[Formula[Any]], Formula[Any]]] = {
    "positive": lambda fm: +fm,
    "negative": lambda fm: -fm,
    "absolute": abs,
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

    def compile(self, expression: Expression) -> Formula[T]:
        if isinstance(expression, (int, float, Decimal)):
            return Formula(lambda _: expression)

        if isinstance(expression, str) and expression not in self._fns:
            raise FormulaNotFoundError(expression)

        if isinstance(expression, str):
            return self._fns[expression]

        if is_formula_dict(expression):
            return self._compile_formula(expression)

        if is_round_wrapper_dict(expression) and not isinstance(expression["ndigits"], int):
            msg = f"Invalid expression: {expression}"
            raise TypeError(msg)

        if is_round_wrapper_dict(expression):
            return round(self.compile(expression["round"]), ndigits=expression["ndigits"])

        if not isinstance(expression, dict):
            msg = f"Invalid expression: {expression}"
            raise TypeError(msg)

        for fn_name, wrap in WRAPPER_FNS.items():
            if fn_name in expression and len(expression) == 1:
                return wrap(self.compile(expression[fn_name]))

        msg = f"Invalid expression: {expression}"
        raise TypeError(msg)

    def _compile_formula(self, fm_dict: FormulaDict) -> Formula[T]:
        expressions = fm_dict["expressions"]
        operator = fm_dict["operator"]

        if (
            not isinstance(expressions, list)
            or not expressions
            or not isinstance(operator, str)
            or operator not in OPERATORS
        ):
            msg = f"Invalid expression: {fm_dict}"
            raise TypeError(msg)

        formula = self.compile(expressions[0])
        applier, _ = OPERATORS[operator]

        for expression in expressions[1:]:
            formula = applier(formula, self.compile(expression))

        return cast("Formula[T]", formula)
