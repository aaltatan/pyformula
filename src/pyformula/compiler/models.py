from typing import TypeAlias, TypedDict, TypeGuard

from pyformula.models import Number, Operator

# -----------------------
# basic operators
# -----------------------


class PositiveWrapperDict(TypedDict):
    """Typed dict for a unary positive wrapper expression."""

    positive: "Expression"


class NegativeWrapperDict(TypedDict):
    """Typed dict for a unary negative wrapper expression."""

    negative: "Expression"


class AbsoluteWrapperDict(TypedDict):
    """Typed dict for an absolute-value wrapper expression."""

    absolute: "Expression"


class RoundWrapperDict(TypedDict):
    """Typed dict for a round wrapper that carries an integer precision."""

    round: "Expression"
    ndigits: int


def is_round_wrapper_dict(obj: object) -> TypeGuard[RoundWrapperDict]:
    """Return whether the object matches the round-wrapper schema."""
    return _is_typed_dict(obj, "round", "ndigits")


# -----------------------
# rounding
# -----------------------


class FloorWrapperDict(TypedDict):
    """Typed dict for a floor wrapper expression."""

    floor: "Expression"


class CeilWrapperDict(TypedDict):
    """Typed dict for a ceil wrapper expression."""

    ceil: "Expression"


class TruncWrapperDict(TypedDict):
    """Typed dict for a trunc wrapper expression."""

    trunc: "Expression"


# -----------------------
# roots and powers
# -----------------------


class SqrtWrapperDict(TypedDict):
    """Typed dict for a square-root wrapper expression."""

    sqrt: "Expression"


class CbrtWrapperDict(TypedDict):
    """Typed dict for a cube-root wrapper expression."""

    cbrt: "Expression"


# ----------------------------------------------
# exponential and logarithmic
# ----------------------------------------------


class ExpWrapperDict(TypedDict):
    """Typed dict for an exp wrapper expression."""

    exp: "Expression"


class Exp2WrapperDict(TypedDict):
    """Typed dict for an exp2 wrapper expression."""

    exp2: "Expression"


class Expm1WrapperDict(TypedDict):
    """Typed dict for an expm1 wrapper expression."""

    expm1: "Expression"


class Log10WrapperDict(TypedDict):
    """Typed dict for a log10 wrapper expression."""

    log10: "Expression"


class Log1pWrapperDict(TypedDict):
    """Typed dict for a log1p wrapper expression."""

    log1p: "Expression"


class Log2WrapperDict(TypedDict):
    """Typed dict for a log2 wrapper expression."""

    log2: "Expression"


# ----------------------------------------------
# trigonometry
# ----------------------------------------------


class SinWrapperDict(TypedDict):
    """Typed dict for a sine wrapper expression."""

    sin: "Expression"


class SinhWrapperDict(TypedDict):
    """Typed dict for a hyperbolic sine wrapper expression."""

    sinh: "Expression"


class AsinWrapperDict(TypedDict):
    """Typed dict for an arc-sine wrapper expression."""

    asin: "Expression"


class AsinhWrapperDict(TypedDict):
    """Typed dict for an inverse hyperbolic sine wrapper expression."""

    asinh: "Expression"


class CosWrapperDict(TypedDict):
    """Typed dict for a cosine wrapper expression."""

    cos: "Expression"


class CoshWrapperDict(TypedDict):
    """Typed dict for a hyperbolic cosine wrapper expression."""

    cosh: "Expression"


class AcosWrapperDict(TypedDict):
    """Typed dict for an arc-cosine wrapper expression."""

    acos: "Expression"


class AcoshWrapperDict(TypedDict):
    """Typed dict for an inverse hyperbolic cosine wrapper expression."""

    acosh: "Expression"


class TanWrapperDict(TypedDict):
    """Typed dict for a tangent wrapper expression."""

    tan: "Expression"


class TanhWrapperDict(TypedDict):
    """Typed dict for a hyperbolic tangent wrapper expression."""

    tanh: "Expression"


class AtanWrapperDict(TypedDict):
    """Typed dict for an arc-tangent wrapper expression."""

    atan: "Expression"


class AtanhWrapperDict(TypedDict):
    """Typed dict for an inverse hyperbolic tangent wrapper expression."""

    atanh: "Expression"


# ----------------------------------------------
# angular conversion
# ----------------------------------------------


class DegreesWrapperDict(TypedDict):
    """Typed dict for a degrees-conversion wrapper expression."""

    degrees: "Expression"


class RadiansWrapperDict(TypedDict):
    """Typed dict for a radians-conversion wrapper expression."""

    radians: "Expression"


# ----------------------------------------------
# special functions
# ----------------------------------------------


class ErfWrapperDict(TypedDict):
    """Typed dict for an error-function wrapper expression."""

    erf: "Expression"


class ErfcWrapperDict(TypedDict):
    """Typed dict for a complementary error-function wrapper expression."""

    erfc: "Expression"


class GammaWrapperDict(TypedDict):
    """Typed dict for a gamma-function wrapper expression."""

    gamma: "Expression"


class LgammaWrapperDict(TypedDict):
    """Typed dict for a logarithmic gamma wrapper expression."""

    lgamma: "Expression"


class FabsWrapperDict(TypedDict):
    """Typed dict for a floating-point absolute-value wrapper expression."""

    fabs: "Expression"


class UlpWrapperDict(TypedDict):
    """Typed dict for an ulp wrapper expression."""

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
    """Typed dict describing a binary operation expression tree."""

    operator: Operator
    expressions: list["Expression"]


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    """Return whether the object matches the binary-formula schema."""
    return _is_typed_dict(obj, "operator", "expressions")


# -----------------------
# helper
# -----------------------


def _is_typed_dict(obj: object, *keys: str) -> bool:
    return (
        isinstance(obj, dict) and all(key in obj for key in keys) and len(obj.keys()) == len(keys)
    )
