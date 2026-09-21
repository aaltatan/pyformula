import math
from decimal import Decimal
from typing import Any

import pytest
from pyformula import Formula
from pyformula import math as m


@pytest.mark.parametrize(
    "formula, expected_result, expected_result_type",
    (
        # floor
        (m.floor(Formula(lambda _: 1)), 1, int),
        (m.floor(Formula(lambda _: 1.2)), 1, int),
        (m.floor(Formula(lambda _: -1.2)), -2, int),
        (m.floor(Formula(lambda _: 1.9)), 1, int),
        (m.floor(Formula(lambda _: -1.9)), -2, int),
        (m.floor(Formula(lambda _: Decimal("1.3"))), Decimal(1), int),
        (m.floor(Formula(lambda _: Decimal("1.9"))), Decimal(1), int),
        (m.floor(Formula(lambda _: Decimal("-1.9"))), Decimal(-2), int),
        # ceil
        (m.ceil(Formula(lambda _: 1)), 1, int),
        (m.ceil(Formula(lambda _: 1.2)), 2, int),
        (m.ceil(Formula(lambda _: -1.2)), -1, int),
        (m.ceil(Formula(lambda _: 1.9)), 2, int),
        (m.ceil(Formula(lambda _: -1.9)), -1, int),
        (m.ceil(Formula(lambda _: Decimal("1.3"))), Decimal(2), int),
        (m.ceil(Formula(lambda _: Decimal("1.9"))), Decimal(2), int),
        (m.ceil(Formula(lambda _: Decimal("-1.9"))), Decimal(-1), int),
        # trunc
        (m.trunc(Formula(lambda _: 1)), 1, int),
        (m.trunc(Formula(lambda _: 1.2)), 1, int),
        (m.trunc(Formula(lambda _: -1.2)), -1, int),
        (m.trunc(Formula(lambda _: 1.9)), 1, int),
        (m.trunc(Formula(lambda _: -1.9)), -1, int),
        (m.trunc(Formula(lambda _: Decimal("1.3"))), Decimal(1), int),
        (m.trunc(Formula(lambda _: Decimal("1.9"))), Decimal(1), int),
        (m.trunc(Formula(lambda _: Decimal("-1.9"))), Decimal(-1), int),
        (m.trunc(Formula(lambda _: Decimal("-2.9"))), Decimal(-2), int),
        (m.trunc(Formula(lambda _: Decimal("-102.9"))), Decimal(-102), int),
        # sqrt
        (m.sqrt(Formula(lambda _: 1)), 1, float),
        (m.sqrt(Formula(lambda _: 9)), 3, float),
        (m.sqrt(Formula(lambda _: 9.0)), 3, float),
        (m.sqrt(Formula(lambda _: Decimal(1))), 1, float),
        (m.sqrt(Formula(lambda _: Decimal(9))), 3, float),
        (m.sqrt(Formula(lambda _: Decimal(81))), 9, float),
        (m.sqrt(Formula(lambda _: Decimal(144))), 12, float),
    ),
)
def test_math_wrapping_formula(
    formula: Formula[Any],
    expected_result: Any,
    expected_result_type: type[Any],
) -> None:
    assert formula(None) == expected_result
    assert isinstance(formula(None), expected_result_type)


@pytest.mark.parametrize(
    "math_fn, value, expected_result, expected_result_type",
    (
        (m.cbrt, 8, 2.0, float),
        (m.cbrt, -27, -3.0, float),
        (m.exp, 0, 1.0, float),
        (m.exp, 1, math.e, float),
        (m.exp2, 0, 1.0, float),
        (m.exp2, 3, 8.0, float),
        (m.expm1, 0, 0.0, float),
        (m.expm1, 1, math.expm1(1), float),
        (m.log10, 1, 0.0, float),
        (m.log10, 100, 2.0, float),
        (m.log10, 0.1, -1.0, float),
        (m.log1p, 0, 0.0, float),
        (m.log1p, 1, math.log1p(1), float),
        (m.log1p, -0.5, math.log1p(-0.5), float),
        (m.log2, 1, 0.0, float),
        (m.log2, 2, 1.0, float),
        (m.log2, 0.5, -1.0, float),
        (m.sin, 0, 0.0, float),
        (m.sin, math.pi / 2, 1.0, float),
        (m.sin, -math.pi / 2, -1.0, float),
        (m.sinh, 0, 0.0, float),
        (m.sinh, 1, math.sinh(1), float),
        (m.asin, 0, 0.0, float),
        (m.asin, 1, math.pi / 2, float),
        (m.asin, -1, -math.pi / 2, float),
        (m.asinh, 0, 0.0, float),
        (m.asinh, 1, math.asinh(1), float),
        (m.cos, 0, 1.0, float),
        (m.cos, math.pi, -1.0, float),
        (m.cosh, 0, 1.0, float),
        (m.cosh, 1, math.cosh(1), float),
        (m.acos, 0, math.pi / 2, float),
        (m.acos, 1, 0.0, float),
        (m.acos, -1, math.pi, float),
        (m.acosh, 1, 0.0, float),
        (m.acosh, 2, math.acosh(2), float),
        (m.tan, 0, 0.0, float),
        (m.tan, math.pi / 4, 1.0, float),
        (m.tanh, 0, 0.0, float),
        (m.tanh, 1, math.tanh(1), float),
        (m.atan, 0, 0.0, float),
        (m.atan, 1, math.pi / 4, float),
        (m.atanh, 0, 0.0, float),
        (m.atanh, 0.5, math.atanh(0.5), float),
        (m.degrees, 0, 0.0, float),
        (m.degrees, math.pi, 180.0, float),
        (m.radians, 0, 0.0, float),
        (m.radians, 180, math.pi, float),
        (m.erf, 0, 0.0, float),
        (m.erf, 1, math.erf(1), float),
        (m.erf, -1, math.erf(-1), float),
        (m.erfc, 0, 1.0, float),
        (m.erfc, 1, math.erfc(1), float),
        (m.gamma, 1, 1.0, float),
        (m.gamma, 0.5, math.gamma(0.5), float),
        (m.gamma, 5, 24.0, float),
        (m.lgamma, 1, 0.0, float),
        (m.lgamma, 5, math.lgamma(5), float),
        (m.fabs, 0, 0.0, float),
        (m.fabs, -1.25, 1.25, float),
        (m.ulp, 0.0, math.ulp(0.0), float),
        (m.ulp, 1.0, math.ulp(1.0), float),
        (m.ulp, -1.0, math.ulp(-1.0), float),
    ),
)
def test_math_wrapping_formula_all_functions(
    math_fn: Any,
    value: Any,
    expected_result: Any,
    expected_result_type: type[Any],
) -> None:
    result = math_fn(Formula(lambda _: value))(None)
    assert result == pytest.approx(expected_result)
    assert isinstance(result, expected_result_type)


@pytest.mark.parametrize(
    "math_fn, value, expected_result, wrong_result",
    (
        (m.sqrt, 9, 3.0, 4.0),
        (m.cbrt, 27, 3.0, 2.0),
        (m.exp, 1, math.e, 2.0),
        (m.log10, 100, 2.0, 1.0),
        (m.log2, 8, 3.0, 2.0),
        (m.sin, math.pi / 2, 1.0, 0.0),
        (m.cos, math.pi, -1.0, 1.0),
        (m.tan, 0.0, 0.0, 1.0),
        (m.degrees, math.pi, 180.0, 90.0),
        (m.radians, 180.0, math.pi, 1.0),
        (m.gamma, 5, 24.0, 23.0),
        (m.fabs, -1.25, 1.25, 0.0),
    ),
)
def test_math_wrapping_formula_rejects_wrong_results(
    math_fn: Any,
    value: Any,
    expected_result: Any,
    wrong_result: Any,
) -> None:
    result = math_fn(Formula(lambda _: value))(None)

    assert result == pytest.approx(expected_result)
    assert result != wrong_result


@pytest.mark.parametrize(
    "math_fn, value, error_type",
    (
        (m.sqrt, -1, ValueError),
        (m.sqrt, -0.5, ValueError),
        (m.log10, 0, ValueError),
        (m.log10, -1, ValueError),
        (m.log1p, -1.1, ValueError),
        (m.log2, 0, ValueError),
        (m.log2, -1, ValueError),
        (m.asin, 2, ValueError),
        (m.asin, -2, ValueError),
        (m.acos, 2, ValueError),
        (m.acos, -2, ValueError),
        (m.acosh, 0, ValueError),
        (m.acosh, -1, ValueError),
        (m.atanh, 2, ValueError),
        (m.atanh, -2, ValueError),
        (m.gamma, 0, ValueError),
        (m.gamma, -1, ValueError),
        (m.lgamma, 0, ValueError),
        (m.lgamma, -1, ValueError),
        (m.exp, 1000, OverflowError),
        (m.exp2, 1024, OverflowError),
    ),
)
def test_math_wrapping_formula_invalid_domain_raises(
    math_fn: Any,
    value: Any,
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        math_fn(Formula(lambda _: value))(None)


@pytest.mark.parametrize(
    "math_fn, value, expected_result",
    (
        (m.ceil, Decimal("1.0000000000000001"), 1),
        (m.ceil, Decimal("-1.0000000000000001"), -1),
        (m.floor, Decimal("1.0000000000000001"), 1),
        (m.floor, Decimal("-1.0000000000000001"), -1),
        (m.trunc, Decimal("-0.0000000000000001"), 0),
        (m.exp, -1, math.e ** -1),
        (m.exp, -10, math.e ** -10),
        (m.log10, 0.0001, -4.0),
        (m.log1p, -0.999999, math.log1p(-0.999999)),
        (m.sin, -math.pi, 0.0),
        (m.cos, 2 * math.pi, 1.0),
        (m.tan, math.pi / 4, 1.0),
        (m.degrees, -math.pi / 2, -90.0),
        (m.radians, -90.0, -math.pi / 2),
        (m.fabs, -0.0, 0.0),
        (m.ulp, 0.0, math.ulp(0.0)),
    ),
)
def test_math_wrapping_formula_edge_values(
    math_fn: Any,
    value: Any,
    expected_result: Any,
) -> None:
    result = math_fn(Formula(lambda _: value))(None)
    assert result == pytest.approx(expected_result)
