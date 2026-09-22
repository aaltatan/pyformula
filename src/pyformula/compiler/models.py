from typing import TypeAlias, TypedDict, TypeGuard

from pyformula.models import Number, Operator

# -----------------------
# basic operators
# -----------------------


class PositiveWrapperDict(TypedDict):
    positive: "Expression"


class NegativeWrapperDict(TypedDict):
    negative: "Expression"


class AbsoluteWrapperDict(TypedDict):
    absolute: "Expression"


class RoundWrapperDict(TypedDict):
    round: "Expression"
    ndigits: int


def is_round_wrapper_dict(obj: object) -> TypeGuard[RoundWrapperDict]:
    return _is_typed_dict(obj, "round", "ndigits")


# -----------------------
# rounding
# -----------------------


class FloorWrapperDict(TypedDict):
    floor: "Expression"


class CeilWrapperDict(TypedDict):
    ceil: "Expression"


class TruncWrapperDict(TypedDict):
    trunc: "Expression"


# -----------------------
# roots and powers
# -----------------------


class SqrtWrapperDict(TypedDict):
    sqrt: "Expression"


class CbrtWrapperDict(TypedDict):
    cbrt: "Expression"


# ----------------------------------------------
# exponential and logarithmic
# ----------------------------------------------


class ExpWrapperDict(TypedDict):
    exp: "Expression"


class Exp2WrapperDict(TypedDict):
    exp2: "Expression"


class Expm1WrapperDict(TypedDict):
    expm1: "Expression"


class Log10WrapperDict(TypedDict):
    log10: "Expression"


class Log1pWrapperDict(TypedDict):
    log1p: "Expression"


class Log2WrapperDict(TypedDict):
    log2: "Expression"


# ----------------------------------------------
# trigonometry
# ----------------------------------------------


class SinWrapperDict(TypedDict):
    sin: "Expression"


class SinhWrapperDict(TypedDict):
    sinh: "Expression"


class AsinWrapperDict(TypedDict):
    asin: "Expression"


class AsinhWrapperDict(TypedDict):
    asinh: "Expression"


class CosWrapperDict(TypedDict):
    cos: "Expression"


class CoshWrapperDict(TypedDict):
    cosh: "Expression"


class AcosWrapperDict(TypedDict):
    acos: "Expression"


class AcoshWrapperDict(TypedDict):
    acosh: "Expression"


class TanWrapperDict(TypedDict):
    tan: "Expression"


class TanhWrapperDict(TypedDict):
    tanh: "Expression"


class AtanWrapperDict(TypedDict):
    atan: "Expression"


class AtanhWrapperDict(TypedDict):
    atanh: "Expression"


# ----------------------------------------------
# angular conversion
# ----------------------------------------------


class DegreesWrapperDict(TypedDict):
    degrees: "Expression"


class RadiansWrapperDict(TypedDict):
    radians: "Expression"


# ----------------------------------------------
# special functions
# ----------------------------------------------


class ErfWrapperDict(TypedDict):
    erf: "Expression"


class ErfcWrapperDict(TypedDict):
    erfc: "Expression"


class GammaWrapperDict(TypedDict):
    gamma: "Expression"


class LgammaWrapperDict(TypedDict):
    lgamma: "Expression"


class FabsWrapperDict(TypedDict):
    fabs: "Expression"


class UlpWrapperDict(TypedDict):
    ulp: "Expression"


# -----------------------
# formula
# -----------------------


Expression: TypeAlias = "FormulaDict | WrapperDict | str | Number"


WrapperDict: TypeAlias = (
    # basic operators
    PositiveWrapperDict
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


class FormulaDict(TypedDict):
    operator: Operator
    expressions: list["Expression"]


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return _is_typed_dict(obj, "operator", "expressions")


# -----------------------
# helper
# -----------------------


def _is_typed_dict(obj: object, *keys: str) -> bool:
    return (
        isinstance(obj, dict) and all(key in obj for key in keys) and len(obj.keys()) == len(keys)
    )
