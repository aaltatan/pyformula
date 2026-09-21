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
# rounding
# -----------------------


class FloorWrapperDict(TypedDict):
    floor: "WrapperType"


class CeilWrapperDict(TypedDict):
    ceil: "WrapperType"


class TruncWrapperDict(TypedDict):
    trunc: "WrapperType"


# -----------------------
# roots and powers
# -----------------------


class SqrtWrapperDict(TypedDict):
    sqrt: "WrapperType"


class CbrtWrapperDict(TypedDict):
    cbrt: "WrapperType"


# ----------------------------------------------
# exponential and logarithmic
# ----------------------------------------------


class ExpWrapperDict(TypedDict):
    exp: "WrapperType"


class Exp2WrapperDict(TypedDict):
    exp2: "WrapperType"


class Expm1WrapperDict(TypedDict):
    expm1: "WrapperType"


class Log10WrapperDict(TypedDict):
    log10: "WrapperType"


class Log1pWrapperDict(TypedDict):
    log1p: "WrapperType"


class Log2WrapperDict(TypedDict):
    log2: "WrapperType"


# ----------------------------------------------
# trigonometry
# ----------------------------------------------


class SinWrapperDict(TypedDict):
    sin: "WrapperType"


class SinhWrapperDict(TypedDict):
    sinh: "WrapperType"


class AsinWrapperDict(TypedDict):
    asin: "WrapperType"


class AsinhWrapperDict(TypedDict):
    asinh: "WrapperType"


class CosWrapperDict(TypedDict):
    cos: "WrapperType"


class CoshWrapperDict(TypedDict):
    cosh: "WrapperType"


class AcosWrapperDict(TypedDict):
    acos: "WrapperType"


class AcoshWrapperDict(TypedDict):
    acosh: "WrapperType"


class TanWrapperDict(TypedDict):
    tan: "WrapperType"


class TanhWrapperDict(TypedDict):
    tanh: "WrapperType"


class AtanWrapperDict(TypedDict):
    atan: "WrapperType"


class AtanhWrapperDict(TypedDict):
    atanh: "WrapperType"


# ----------------------------------------------
# angular conversion
# ----------------------------------------------


class DegreesWrapperDict(TypedDict):
    degrees: "WrapperType"


class RadiansWrapperDict(TypedDict):
    radians: "WrapperType"


# ----------------------------------------------
# special functions
# ----------------------------------------------


class ErfWrapperDict(TypedDict):
    erf: "WrapperType"


class ErfcWrapperDict(TypedDict):
    erfc: "WrapperType"


class GammaWrapperDict(TypedDict):
    gamma: "WrapperType"


class LgammaWrapperDict(TypedDict):
    lgamma: "WrapperType"


class FabsWrapperDict(TypedDict):
    fabs: "WrapperType"


class UlpWrapperDict(TypedDict):
    ulp: "WrapperType"


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
    # rounding
    | FloorWrapperDict
    | CeilWrapperDict
    | TruncWrapperDict
    # roots and powers
    | SqrtWrapperDict
    | CbrtWrapperDict
    # exponential and logarithmic
    | ExpWrapperDict
    | Exp2WrapperDict
    | Expm1WrapperDict
    | Log10WrapperDict
    | Log1pWrapperDict
    | Log2WrapperDict
    # trigonometry
    | SinWrapperDict
    | SinhWrapperDict
    | AsinWrapperDict
    | AsinhWrapperDict
    | CosWrapperDict
    | CoshWrapperDict
    | AcosWrapperDict
    | AcoshWrapperDict
    | TanWrapperDict
    | TanhWrapperDict
    | AtanWrapperDict
    | AtanhWrapperDict
    # angular conversion
    | DegreesWrapperDict
    | RadiansWrapperDict
    # special functions
    | ErfWrapperDict
    | ErfcWrapperDict
    | GammaWrapperDict
    | LgammaWrapperDict
    | FabsWrapperDict
    | UlpWrapperDict
)


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return _is_typed_dict(obj, "operator", "expressions")


# -----------------------
# helper
# -----------------------


def _is_typed_dict(obj: object, *keys: str) -> bool:
    return (
        isinstance(obj, dict) and all(key in obj for key in keys) and len(obj.keys()) == len(keys)
    )
