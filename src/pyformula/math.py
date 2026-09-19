import math as builtin_math
from collections.abc import Callable

from .formula import Formula

# ----------------------------------------------
# rounding
# ----------------------------------------------


def ceil[T](fm: Formula[T], /) -> Formula[T]:
    return _wrap(fm, math_fn=builtin_math.ceil)


def floor[T](fm: Formula[T], /) -> Formula[T]:
    return _wrap(fm, math_fn=builtin_math.floor)


def trunc[T](fm: Formula[T], /) -> Formula[T]:
    return _wrap(fm, math_fn=builtin_math.trunc)


# ----------------------------------------------
# roots and powers
# ----------------------------------------------


def sqrt[T](fm: Formula[T], /) -> Formula[T]:
    """Return the square root of formula."""
    return _wrap(fm, math_fn=builtin_math.sqrt)


def cbrt[T](fm: Formula[T], /) -> Formula[T]:
    """Return the cube root of formula."""
    return _wrap(fm, math_fn=builtin_math.cbrt)


# ----------------------------------------------
# exponential and logarithmic
# ----------------------------------------------


def exp[T](fm: Formula[T], /) -> Formula[T]:
    """Return e raised to the power of formula."""
    return _wrap(fm, math_fn=builtin_math.exp)


def exp2[T](fm: Formula[T], /) -> Formula[T]:
    """Return 2 raised to the power of formula."""
    return _wrap(fm, math_fn=builtin_math.exp2)


def expm1[T](fm: Formula[T], /) -> Formula[T]:
    """Return exp(formula)-1.

    This function avoids the loss of precision involved in the direct evaluation of exp(formula)-1.
    """
    return _wrap(fm, math_fn=builtin_math.expm1)


def log10[T](fm: Formula[T], /) -> Formula[T]:
    """Return the base 10 logarithm of formula."""
    return _wrap(fm, math_fn=builtin_math.log10)


def log1p[T](fm: Formula[T], /) -> Formula[T]:
    """Return the natural logarithm of 1+formula (base e).

    The result is computed in a way which is accurate for formula near zero.
    """
    return _wrap(fm, math_fn=builtin_math.log1p)


def log2[T](fm: Formula[T], /) -> Formula[T]:
    """Return the base 2 logarithm of formula."""
    return _wrap(fm, math_fn=builtin_math.log2)


# ----------------------------------------------
# trigonometry
# ----------------------------------------------


def sin[T](fm: Formula[T], /) -> Formula[T]:
    """Return the sine of formula (measured in radians)."""
    return _wrap(fm, math_fn=builtin_math.sin)


def sinh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic sine of formula."""
    return _wrap(fm, math_fn=builtin_math.sinh)


def asin[T](fm: Formula[T], /) -> Formula[T]:
    """Return the arc sine (measured in radians) of formula."""
    return _wrap(fm, math_fn=builtin_math.asin)


def asinh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the inverse hyperbolic sine of formula."""
    return _wrap(fm, math_fn=builtin_math.asinh)


def cos[T](fm: Formula[T], /) -> Formula[T]:
    """Return the cosine of formula (measured in radians)."""
    return _wrap(fm, math_fn=builtin_math.cos)


def cosh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic cosine of formula."""
    return _wrap(fm, math_fn=builtin_math.cosh)


def acos[T](fm: Formula[T], /) -> Formula[T]:
    """Return the arc cosine (measured in radians) of formula."""
    return _wrap(fm, math_fn=builtin_math.acos)


def acosh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic arc cosine of formula."""
    return _wrap(fm, math_fn=builtin_math.acosh)


def tan[T](fm: Formula[T], /) -> Formula[T]:
    """Return the tangent of formula (measured in radians)."""
    return _wrap(fm, math_fn=builtin_math.tan)


def tanh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic tangent of formula."""
    return _wrap(fm, math_fn=builtin_math.tanh)


def atan[T](fm: Formula[T], /) -> Formula[T]:
    """Return the arc tangent (measured in radians) of formula."""
    return _wrap(fm, math_fn=builtin_math.atan)


def atanh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic arc tangent of formula."""
    return _wrap(fm, math_fn=builtin_math.atanh)


# ----------------------------------------------
# angular conversion
# ----------------------------------------------


def degrees[T](fm: Formula[T], /) -> Formula[T]:
    """Convert angle formula from radians to degrees."""
    return _wrap(fm, math_fn=builtin_math.degrees)


def radians[T](fm: Formula[T], /) -> Formula[T]:
    """Convert angle formula from degrees to radians."""
    return _wrap(fm, math_fn=builtin_math.radians)


# ----------------------------------------------
# special functions
# ----------------------------------------------


def erf[T](fm: Formula[T], /) -> Formula[T]:
    """Return the error function of formula."""
    return _wrap(fm, math_fn=builtin_math.erf)


def erfc[T](fm: Formula[T], /) -> Formula[T]:
    """Complementary error function."""
    return _wrap(fm, math_fn=builtin_math.erfc)


def gamma[T](fm: Formula[T], /) -> Formula[T]:
    """Return the gamma function of formula."""
    return _wrap(fm, math_fn=builtin_math.gamma)


def lgamma[T](fm: Formula[T], /) -> Formula[T]:
    """Return the natural logarithm of the gamma function of formula."""
    return _wrap(fm, math_fn=builtin_math.lgamma)


# ----------------------------------------------
# distance and floating point manipulation
# ----------------------------------------------


def fabs[T](fm: Formula[T], /) -> Formula[T]:
    """Return the absolute value of formula."""
    return _wrap(fm, math_fn=builtin_math.fabs)


def ulp[T](fm: Formula[T], /) -> Formula[T]:
    """Return the distance between formula and the next larger representable number."""
    return _wrap(fm, math_fn=builtin_math.ulp)


# -----------------------
# helper
# -----------------------


def _wrap[T](formula: Formula[T], /, *, math_fn: Callable[[float], float]) -> Formula[T]:
    return Formula(lambda obj: math_fn(float(formula(obj))), name=f"{math_fn.__name__}({formula})")
