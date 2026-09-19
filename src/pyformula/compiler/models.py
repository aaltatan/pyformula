from typing import TypeAlias, TypedDict, TypeGuard

from pyformula.models import NumberType, OperatorType

# -----------------------
# basic operators
# -----------------------


class PositiveWrapperDict(TypedDict):
    positive: "WrapperType"


def is_positive_wrapper_dict(obj: object) -> TypeGuard[PositiveWrapperDict]:
    return _is_typed_dict(obj, "positive")


class NegativeWrapperDict(TypedDict):
    negative: "WrapperType"


def is_negative_wrapper_dict(obj: object) -> TypeGuard[NegativeWrapperDict]:
    return _is_typed_dict(obj, "negative")


class AbsoluteWrapperDict(TypedDict):
    absolute: "WrapperType"


def is_absolute_wrapper_dict(obj: object) -> TypeGuard[AbsoluteWrapperDict]:
    return _is_typed_dict(obj, "absolute")


class RoundWrapperDict(TypedDict):
    round: "WrapperType"
    ndigits: int


def is_round_wrapper_dict(obj: object) -> TypeGuard[RoundWrapperDict]:
    return _is_typed_dict(obj, "round", "ndigits")


# -----------------------
# math operators
# -----------------------


class FloorWrapperDict(TypedDict):
    floor: "WrapperType"


def is_floor_wrapper_dict(obj: object) -> TypeGuard[FloorWrapperDict]:
    return _is_typed_dict(obj, "floor")


class CeilWrapperDict(TypedDict):
    ceil: "WrapperType"


def is_ceil_wrapper_dict(obj: object) -> TypeGuard[CeilWrapperDict]:
    return _is_typed_dict(obj, "ceil")


class TruncWrapperDict(TypedDict):
    trunc: "WrapperType"


def is_trunc_wrapper_dict(obj: object) -> TypeGuard[TruncWrapperDict]:
    return _is_typed_dict(obj, "trunc")


# -----------------------
# formula
# -----------------------


class FormulaDict(TypedDict):
    operator: OperatorType
    expressions: list["ExpressionType"]


ExpressionType: TypeAlias = "FormulaDict | WrapperType | NumberType"


WrapperType: TypeAlias = (
    str
    # basic operators
    | PositiveWrapperDict
    | NegativeWrapperDict
    | AbsoluteWrapperDict
    | RoundWrapperDict
    # math operators
    | FloorWrapperDict
    | CeilWrapperDict
    | TruncWrapperDict
)


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return _is_typed_dict(obj, "operator", "expression")


# -----------------------
# helper
# -----------------------


def _is_typed_dict(obj: object, *keys: str) -> bool:
    return (
        isinstance(obj, dict) and all(key in obj for key in keys) and len(obj.keys()) == len(keys)
    )
