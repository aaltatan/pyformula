import math
from collections.abc import Callable

from .formula import Formula

# ----------------------------------------------
# rounding
# ----------------------------------------------


def ceil[T](fm: Formula[T], /) -> Formula[T]:
    """Return a formula that evaluates the ceiling of the wrapped value.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import ceil

    ceiled = ceil(Formula(lambda _: 1.2))
    print(ceiled(object))  # 2.0
    ```
    """
    return _wrap(fm, math_fn=math.ceil)


def floor[T](fm: Formula[T], /) -> Formula[T]:
    """Return a formula that evaluates the floor of the wrapped value.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import floor

    floored = floor(Formula(lambda _: 1.9))
    print(floored(object))  # 1.0
    ```
    """
    return _wrap(fm, math_fn=math.floor)


def trunc[T](fm: Formula[T], /) -> Formula[T]:
    """Return a formula that truncates the wrapped value toward zero.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import trunc

    truncated = trunc(Formula(lambda _: -1.8))
    print(truncated(object))  # -1.0
    ```
    """
    return _wrap(fm, math_fn=math.trunc)


# ----------------------------------------------
# roots and powers
# ----------------------------------------------


def sqrt[T](fm: Formula[T], /) -> Formula[T]:
    """Return the square root of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import sqrt

    square_root = sqrt(Formula(lambda _: 9))
    print(square_root(object))  # 3.0
    ```
    """
    return _wrap(fm, math_fn=math.sqrt)


def cbrt[T](fm: Formula[T], /) -> Formula[T]:
    """Return the cube root of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import cbrt

    cube_root = cbrt(Formula(lambda _: 27))
    print(cube_root(object))  # 3.0
    ```
    """
    return _wrap(fm, math_fn=math.cbrt)


# ----------------------------------------------
# exponential and logarithmic
# ----------------------------------------------


def exp[T](fm: Formula[T], /) -> Formula[T]:
    """Return e raised to the power of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import exp

    exponential = exp(Formula(lambda _: 1))
    print(exponential(object))  # 2.718281828459045
    ```

    """
    return _wrap(fm, math_fn=math.exp)


def exp2[T](fm: Formula[T], /) -> Formula[T]:
    """Return 2 raised to the power of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import exp2

    exponential = exp2(Formula(lambda _: 3))
    print(exponential(object))  # 9.0
    ```

    """
    return _wrap(fm, math_fn=math.exp2)


def expm1[T](fm: Formula[T], /) -> Formula[T]:
    """Return exp(formula) - 1 while preserving precision for small values.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import expm1

    exponential = expm1(Formula(lambda _: 1))
    print(exponential(object))  # 0.36787944117144233
    ```

    """
    return _wrap(fm, math_fn=math.expm1)


def log10[T](fm: Formula[T], /) -> Formula[T]:
    """Return the base-10 logarithm of the wrapped formula.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import log10

    logarithm = log10(Formula(lambda _: 100))
    print(logarithm(object))  # 2.0
    ```

    """
    return _wrap(fm, math_fn=math.log10)


def log1p[T](fm: Formula[T], /) -> Formula[T]:
    """Return the natural logarithm of 1 + the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import log1p

    logarithm = log1p(Formula(lambda _: 1))
    print(logarithm(object))  # 0.0
    ```

    """
    return _wrap(fm, math_fn=math.log1p)


def log2[T](fm: Formula[T], /) -> Formula[T]:
    """Return the base-2 logarithm of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import log2

    logarithm = log2(Formula(lambda _: 8))
    print(logarithm(object))  # 3.0
    ```

    """
    return _wrap(fm, math_fn=math.log2)


# ----------------------------------------------
# trigonometry
# ----------------------------------------------


def sin[T](fm: Formula[T], /) -> Formula[T]:
    """Return the sine of the wrapped formula in radians.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import sin

    sine = sin(Formula(lambda _: 0))
    print(sine(object))  # 0.0
    ```

    """
    return _wrap(fm, math_fn=math.sin)


def sinh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic sine of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import sinh

    hyperbolic_sine = sinh(Formula(lambda _: 1))
    print(hyperbolic_sine(object))  # 1.1752011936438014
    ```

    """
    return _wrap(fm, math_fn=math.sinh)


def asin[T](fm: Formula[T], /) -> Formula[T]:
    """Return the arc sine of the wrapped formula in radians.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import asin

    arc_sine = asin(Formula(lambda _: 1))
    print(arc_sine(object))  # 1.5707963267948966
    ```

    """
    return _wrap(fm, math_fn=math.asin)


def asinh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the inverse hyperbolic sine of the wrapped formula.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import asinh

    inverse_hyperbolic_sine = asinh(Formula(lambda _: 1))
    print(inverse_hyperbolic_sine(object))  # 0.8813735870195429
    ```

    """
    return _wrap(fm, math_fn=math.asinh)


def cos[T](fm: Formula[T], /) -> Formula[T]:
    """Return the cosine of the wrapped formula in radians.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import cos

    cosine = cos(Formula(lambda _: 0))
    print(cosine(object))  # 1.0
    ```

    """
    return _wrap(fm, math_fn=math.cos)


def cosh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic cosine of the wrapped formula.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import cosh

    hyperbolic_cosine = cosh(Formula(lambda _: 1))
    print(hyperbolic_cosine(object))  # 1.5430806348152437
    ```

    """
    return _wrap(fm, math_fn=math.cosh)


def acos[T](fm: Formula[T], /) -> Formula[T]:
    """Return the arc cosine of the wrapped formula in radians.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import acos

    arc_cosine = acos(Formula(lambda _: 1))
    print(arc_cosine(object))  # 0.0
    ```

    """
    return _wrap(fm, math_fn=math.acos)


def acosh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the inverse hyperbolic cosine of the wrapped formula.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import acosh

    inverse_hyperbolic_cosine = acosh(Formula(lambda _: 1))
    print(inverse_hyperbolic_cosine(object))  # 0.0
    ```

    """
    return _wrap(fm, math_fn=math.acosh)


def tan[T](fm: Formula[T], /) -> Formula[T]:
    """Return the tangent of the wrapped formula in radians.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import tan

    tangent = tan(Formula(lambda _: 2))
    print(tangent(object))  # 0.9092974268256817
    ```

    """
    return _wrap(fm, math_fn=math.tan)


def tanh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the hyperbolic tangent of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import tanh

    hyperbolic_tangent = tanh(Formula(lambda _: 1))
    print(hyperbolic_tangent(object))  # 0.7615941559557649
    ```

    """
    return _wrap(fm, math_fn=math.tanh)


def atan[T](fm: Formula[T], /) -> Formula[T]:
    """Return the arc tangent of the wrapped formula in radians.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import atan

    arc_tangent = atan(Formula(lambda _: 1))
    print(arc_tangent(object))  # 0.7853981633974483
    ```

    """
    return _wrap(fm, math_fn=math.atan)


def atanh[T](fm: Formula[T], /) -> Formula[T]:
    """Return the inverse hyperbolic tangent of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import atanh

    inverse_hyperbolic_tangent = atanh(Formula(lambda _: 0.5))
    print(inverse_hyperbolic_tangent(object))  # 0.5493061443340548
    ```

    """
    return _wrap(fm, math_fn=math.atanh)


# ----------------------------------------------
# angular conversion
# ----------------------------------------------


def degrees[T](fm: Formula[T], /) -> Formula[T]:
    """Convert an angle in radians from the wrapped formula into degrees.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import degrees

    angle = degrees(Formula(lambda _: 3.14159))
    print(angle(object))  # 180.0
    ```

    """
    return _wrap(fm, math_fn=math.degrees)


def radians[T](fm: Formula[T], /) -> Formula[T]:
    """Convert an angle in degrees from the wrapped formula into radians.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import radians

    angle = radians(Formula(lambda _: 180))
    print(angle(object))  # 3.141592653589793
    ```

    """
    return _wrap(fm, math_fn=math.radians)


# ----------------------------------------------
# special functions
# ----------------------------------------------


def erf[T](fm: Formula[T], /) -> Formula[T]:
    """Return the error function of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import erf

    error_function = erf(Formula(lambda _: 1))
    print(error_function(object))  # 0.8427007929497149
    ```

    """
    return _wrap(fm, math_fn=math.erf)


def erfc[T](fm: Formula[T], /) -> Formula[T]:
    """Return the complementary error function of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import erfc

    complementary_error_function = erfc(Formula(lambda _: 1))
    print(complementary_error_function(object))  # 0.1572992070502851
    ```

    """
    return _wrap(fm, math_fn=math.erfc)


def gamma[T](fm: Formula[T], /) -> Formula[T]:
    """Return the gamma function of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import gamma

    gamma_function = gamma(Formula(lambda _: 5))
    print(gamma_function(object))  # 24.0
    ```

    """
    return _wrap(fm, math_fn=math.gamma)


def lgamma[T](fm: Formula[T], /) -> Formula[T]:
    """Return the natural logarithm of the gamma function of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import lgamma

    natural_logarithm_of_gamma_function = lgamma(Formula(lambda _: 5))
    print(natural_logarithm_of_gamma_function(object))  # 1.791759469228055
    ```

    """
    return _wrap(fm, math_fn=math.lgamma)


# ----------------------------------------------
# distance and floating point manipulation
# ----------------------------------------------


def fabs[T](fm: Formula[T], /) -> Formula[T]:
    """Return the absolute value of the wrapped formula.

    ## Examples:

    ```python
    from pyformula import Formula
    from pyformula.math import fabs

    absolute_value = fabs(Formula(lambda _: -1.25))
    print(absolute_value(object))  # 1.25
    ```

    """
    return _wrap(fm, math_fn=math.fabs)


def ulp[T](fm: Formula[T], /) -> Formula[T]:
    """Return the distance to the next larger representable float from the wrapped formula.

    ## Examples:
    ```python
    from pyformula import Formula
    from pyformula.math import ulp

    distance_to_next_larger_representable_float = ulp(Formula(lambda _: 1.0))
    print(distance_to_next_larger_representable_float(object))  # 0.0
    ```

    """
    return _wrap(fm, math_fn=math.ulp)


# ----------------------------------------------
# helper
# ----------------------------------------------


def _wrap[T](formula: Formula[T], /, *, math_fn: Callable[[float], float]) -> Formula[T]:
    return Formula(lambda obj: math_fn(float(formula(obj))), name=f"{math_fn.__name__}({formula})")
