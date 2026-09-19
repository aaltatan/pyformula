from typing import TypeAlias, TypedDict

from pyformula.models import NumberType, OperatorType


class FormulaDict(TypedDict):
    operator: OperatorType
    expressions: list["ExpressionType"]


class PositiveWrapperDict(TypedDict):
    positive: "WrapperType"


class NegativeWrapperDict(TypedDict):
    negative: "WrapperType"


class AbsWrapperDict(TypedDict):
    absolute: "WrapperType"


class RoundWrapperDict(TypedDict):
    round: "WrapperType"
    ndigits: int


class FloorWrapperDict(TypedDict):
    floor: "WrapperType"


class CeilWrapperDict(TypedDict):
    ceil: "WrapperType"


class TruncWrapperDict(TypedDict):
    trunc: "WrapperType"


ExpressionType: TypeAlias = "FormulaDict | WrapperType | NumberType"
WrapperType: TypeAlias = (
    str
    | PositiveWrapperDict
    | NegativeWrapperDict
    | AbsWrapperDict
    | FloorWrapperDict
    | CeilWrapperDict
    | TruncWrapperDict
    | RoundWrapperDict
)
