from .exceptions import FormulaNotFoundError
from .formula import Formula
from .models import ExpressionType, FormulaDict, is_formula_dict, is_number
from .operators import OPERATORS_APPLIERS


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

        if isinstance(expression, str):
            if expression not in self._fns:
                raise FormulaNotFoundError(expression)

            return self._fns[expression]

        if is_number(expression):
            return Formula(lambda _: expression)

        msg = f"Invalid expression: {expression}"
        raise ValueError(msg)
