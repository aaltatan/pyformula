from collections.abc import Callable, Mapping
from decimal import Decimal
from typing import Any, cast

from pyvocabulary import index_path, key_path, located

from pyformula import math
from pyformula.exceptions import FormulaNotFoundError, InvalidExpressionError, PyformulaError
from pyformula.formula import Formula
from pyformula.models import Number
from pyformula.operator import OPERATORS

from .models import (
    Expression,
    FormulaDict,
    RoundWrapperDict,
    is_formula_dict,
    is_round_wrapper_dict,
)

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


type LiteralFn = Callable[[Number], Any]


class FormulaCompiler[T]:
    """Compile a structured expression tree into a runtime formula.

    Args:
        fns: The named formulas an expression may reference.
        literal: Converts every number literal in an expression before use.
            JSON numbers arrive as `float`, so formulas over `Decimal` money
            should pass `literal=decimal_literal`, which goes through `str`
            to keep `0.8` exact. Defaults to using literals as they are.

    Example:
    ```python
    >>> from decimal import Decimal
    >>> price = Formula(lambda order: order["price"], name="price")
    >>> exact = FormulaCompiler({"price": price}, literal=decimal_literal)
    >>> discounted = exact.compile({"operator": "multiply", "expressions": ["price", 0.8]})
    >>> discounted
    Formula((price * 0.8))
    >>> discounted({"price": Decimal("120.00")})
    Decimal('96.000')
    >>> FormulaCompiler({"price": price}).compile("pricee")
    Traceback (most recent call last):
    ...
    pyformula.exceptions.FormulaNotFoundError: Formula not found: pricee. Available formulas: price

    ```

    Examples:
    ```python
    from dataclasses import dataclass
    from pyformula import Formula


    @dataclass
    class Rectangular:
        width: float
        height: float


    def main() -> None:
        fms: dict[str, Formula[Rectangular]] = {
            "width": Formula[Rectangular](lambda rectangle: rectangle.width),
            "height": Formula[Rectangular](lambda rectangle: rectangle.height),
        }

        compiler = FormulaCompiler[Rectangular](fms)

        perimeter = compiler.compile(
            {
                "operator": "multiply",
                "expressions":[
                    "operator": "add",
                    "expressions": [
                        "width",
                        "height",
                    ], 2,
                ]
            }
        )

        area = compiler.compile(
            {
                "operator": "multiply",
                "expressions": [
                    "width",
                    "height",
                ],
            }
        )

        print(perimeter(Rectangular(width=10, height=20)))  # 60.0
        print(area(Rectangular(width=10, height=20)))  # 200.0

        print(perimeter(Rectangular(width=5, height=10)))  # 30.0
        print(area(Rectangular(width=5, height=10)))  # 50.0


    if __name__ == "__main__":
        main()
    ```


    """

    def __init__(
        self,
        fns: Mapping[str, Formula[T]],
        /,
        *,
        literal: LiteralFn | None = None,
    ) -> None:
        self._fns = fns
        self._literal = literal

    def compile(self, expression: Expression) -> Formula[T]:
        """Compile an expression object into a formula callable for a given model type."""
        if isinstance(expression, bool):
            raise InvalidExpressionError(expression)

        if isinstance(expression, (int, float, Decimal)):
            return self._compile_literal(expression)

        if isinstance(expression, str):
            return self._compile_name(expression)

        if is_formula_dict(expression):
            return self._compile_formula(expression)

        if is_round_wrapper_dict(expression):
            return self._compile_round(expression)

        if isinstance(expression, dict):
            wrapped = self._compile_wrapper(expression)
            if wrapped is not None:
                return wrapped

        raise InvalidExpressionError(expression)

    def _compile_literal(self, number: Number) -> Formula[T]:
        value = number if self._literal is None else self._literal(number)
        return Formula(lambda _: value, name=str(value))

    def _compile_name(self, name: str) -> Formula[T]:
        if name not in self._fns:
            raise FormulaNotFoundError(name, self._fns.keys())

        return self._fns[name]

    def _compile_round(self, expression: RoundWrapperDict) -> Formula[T]:
        ndigits = expression["ndigits"]

        if not isinstance(ndigits, int) or isinstance(ndigits, bool):
            raise InvalidExpressionError(expression)

        return round(self._compile_at(expression["round"], "$.round"), ndigits=ndigits)

    def _compile_wrapper(self, expression: Mapping[str, object]) -> Formula[T] | None:
        if len(expression) != 1:
            return None

        for fn_name, wrap in WRAPPER_FNS.items():
            if fn_name in expression:
                operand = cast("Expression", expression[fn_name])
                return wrap(self._compile_at(operand, key_path("$", fn_name)))

        return None

    def _compile_formula(self, fm_dict: FormulaDict) -> Formula[T]:
        expressions = fm_dict["expressions"]
        operator = fm_dict["operator"]

        if (
            not isinstance(expressions, list)
            or not expressions
            or not isinstance(operator, str)
            or operator not in OPERATORS
        ):
            raise InvalidExpressionError(fm_dict)

        formula = self._compile_at(expressions[0], "$.expressions[0]")
        applier, _ = OPERATORS[operator]

        for index, expression in enumerate(expressions[1:], start=1):
            operand = self._compile_at(expression, index_path("$.expressions", index))
            formula = applier(formula, operand)

        return cast("Formula[T]", formula)

    def _compile_at(self, expression: Expression, path: str) -> Formula[T]:
        # Each level notes its path relative to `$`; `located` prefixes the outer
        # levels, so the error ends up with the absolute path.
        with located(path, PyformulaError):
            return self.compile(expression)


def decimal_literal(number: Number, /) -> Decimal:
    """Convert a JSON number to `Decimal` through `str`, so `0.8` stays exactly `0.8`.

    Example:
    ```python
    >>> decimal_literal(0.8), Decimal(0.8) == decimal_literal(0.8)
    (Decimal('0.8'), False)

    ```

    """
    return number if isinstance(number, Decimal) else Decimal(str(number))
