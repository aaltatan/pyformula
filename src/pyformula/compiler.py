import operator
from collections.abc import Callable
from typing import Any, TypeAlias, TypedDict, TypeGuard

from .exceptions import FormulaNotFoundError
from .formula import Formula
from .models import NumberType, OperatorType, is_number

# -----------------------
# models
# -----------------------


ExpressionType: TypeAlias = "FormulaDict | WrapperType | NumberType"
WrapperType: TypeAlias = "str | NegativeWrapperDict | AbsWrapperDict | PositiveWrapperDict"


class FormulaDict(TypedDict):
    operator: OperatorType
    expressions: list[ExpressionType]


class PositiveWrapperDict(TypedDict):
    positive: WrapperType


class NegativeWrapperDict(TypedDict):
    negative: WrapperType


class AbsWrapperDict(TypedDict):
    absolute: WrapperType


# -----------------------
# checkers
# -----------------------


def is_wrapped_dict(obj: object, key: str) -> bool:
    return isinstance(obj, dict) and key in obj and len(obj.keys()) == 1


def is_positive_wrapper_dict(obj: object) -> TypeGuard[PositiveWrapperDict]:
    return is_wrapped_dict(obj, "positive")


def is_negative_wrapper_dict(obj: object) -> TypeGuard[NegativeWrapperDict]:
    return is_wrapped_dict(obj, "negative")


def is_absolute_wrapper_dict(obj: object) -> TypeGuard[AbsWrapperDict]:
    return is_wrapped_dict(obj, "absolute")


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return (
        isinstance(obj, dict)
        and "operator" in obj
        and "expressions" in obj
        and len(obj.keys()) == 2
    )


# -----------------------
# constants
# -----------------------


OPERATORS_APPLIERS: dict[OperatorType, Callable[[Formula[Any], Formula[Any]], Formula[Any]]] = {
    "add": operator.add,
    "subtract": operator.sub,
    "multiply": operator.mul,
    "divide": operator.truediv,
    "modulo": operator.mod,
    "floor_divide": operator.floordiv,
    "power": operator.pow,
}


# -----------------------
# compiler
# -----------------------


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

        return self._compile_wrapped_expression(expression)

    def _compile_wrapped_expression(self, expression: ExpressionType) -> Formula[T]:
        if is_positive_wrapper_dict(expression):
            return +self._compile_wrapped_expression(expression["positive"])

        if is_negative_wrapper_dict(expression):
            return -self._compile_wrapped_expression(expression["negative"])

        if is_absolute_wrapper_dict(expression):
            return abs(self._compile_wrapped_expression(expression["absolute"]))

        if not isinstance(expression, str):
            msg = f"Invalid expression: {expression}"
            raise TypeError(msg)

        if expression not in self._fns:
            raise FormulaNotFoundError(expression)

        return self._fns[expression]
