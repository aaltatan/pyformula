import math
from typing import Any

import pytest
from pyformula import Formula, FormulaCompiler
from pyformula.exceptions import FormulaNotFoundError


def compile_expression(expression: Any) -> Formula[None]:
    return FormulaCompiler[None]({}).compile(expression)


WRAPPER_CASES = (
    [("positive", value, +value) for value in (-10, -1.5, 0, 2, 10.25)]
    + [("negative", value, -value) for value in (-10, -1.5, 0, 2, 10.25)]
    + [("absolute", value, abs(value)) for value in (-10, -1.5, 0, 2, 10.25)]
    + [("ceil", value, math.ceil(value)) for value in (-2.5, -1.1, 0, 1.1, 2.5)]
    + [("floor", value, math.floor(value)) for value in (-2.5, -1.1, 0, 1.1, 2.5)]
    + [("trunc", value, math.trunc(value)) for value in (-2.5, -1.1, 0, 1.1, 2.5)]
    + [("sqrt", value, math.sqrt(value)) for value in (0, 0.25, 1, 2, 9)]
    + [("cbrt", value, math.cbrt(value)) for value in (-27, -1, 0, 1, 64)]
    + [("exp", value, math.exp(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("exp2", value, math.exp2(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("expm1", value, math.expm1(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("log10", value, math.log10(value)) for value in (0.1, 0.5, 1, 10, 100)]
    + [("log1p", value, math.log1p(value)) for value in (-0.5, -0.1, 0, 1, 10)]
    + [("log2", value, math.log2(value)) for value in (0.25, 0.5, 1, 2, 8)]
    + [
        ("sin", value, math.sin(value))
        for value in (-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi)
    ]
    + [
        ("cos", value, math.cos(value))
        for value in (-math.pi, -math.pi / 2, 0, math.pi / 2, math.pi)
    ]
    + [("tan", value, math.tan(value)) for value in (-math.pi / 4, -0.2, 0, 0.2, math.pi / 4)]
    + [("sinh", value, math.sinh(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("cosh", value, math.cosh(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("tanh", value, math.tanh(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("asin", value, math.asin(value)) for value in (-1, -0.5, 0, 0.5, 1)]
    + [("acos", value, math.acos(value)) for value in (-1, -0.5, 0, 0.5, 1)]
    + [("atan", value, math.atan(value)) for value in (-10, -1, 0, 1, 10)]
    + [("asinh", value, math.asinh(value)) for value in (-10, -1, 0, 1, 10)]
    + [("acosh", value, math.acosh(value)) for value in (1, 1.5, 2, 5, 10)]
    + [("atanh", value, math.atanh(value)) for value in (-0.9, -0.5, 0, 0.5, 0.9)]
    + [("degrees", value, math.degrees(value)) for value in (-math.pi, -1, 0, 1, math.pi)]
    + [("radians", value, math.radians(value)) for value in (-180, -90, 0, 90, 180)]
    + [("erf", value, math.erf(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("erfc", value, math.erfc(value)) for value in (-2, -0.5, 0, 0.5, 2)]
    + [("gamma", value, math.gamma(value)) for value in (0.5, 1, 2, 3, 5)]
    + [("lgamma", value, math.lgamma(value)) for value in (0.5, 1, 2, 3, 5)]
    + [("fabs", value, math.fabs(value)) for value in (-10, -1.5, 0, 1.5, 10)]
    + [("ulp", value, math.ulp(value)) for value in (-10.0, -1.0, 0.0, 1.0, 10.0)]
)


@pytest.mark.parametrize("wrapper, value, expected", WRAPPER_CASES)
def test_compiles_math_and_basic_wrapper_cases(wrapper: str, value: float, expected: float) -> None:
    result = compile_expression({wrapper: value})(None)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize("value", range(-30, 31))
def test_deep_wrapper_chains_preserve_expected_sign(value: int) -> None:
    expression: Any = value
    for wrapper in ("absolute", "negative", "negative", "positive"):
        expression = {wrapper: expression}

    assert compile_expression(expression)(None) == abs(value)


@pytest.mark.parametrize(
    "value, ndigits",
    [(value / 7, digits) for value in range(-20, 21) for digits in (0, 1, 2)],
)
def test_round_wrapper_cases(value: float, ndigits: int) -> None:
    expression = {"round": value, "ndigits": ndigits}

    assert compile_expression(expression)(None) == round(value, ndigits)


@pytest.mark.parametrize(
    "expression",
    (
        {},
        {"unknown": 1},
        {"positive": 1, "negative": 1},
        {"round": 1},
        {"round": 1, "ndigits": 2, "extra": 3},
        {"operator": "add", "expression": [1, 2]},
        {"absolute": {"unknown": 1}},
        {"sqrt": {"operator": "add", "expressions": [1, 2]}, "extra": 0},
    ),
)
def test_invalid_expression_shapes_raise_type_error(expression: dict[str, Any]) -> None:
    with pytest.raises(TypeError, match="Invalid expression"):
        compile_expression(expression)


@pytest.mark.parametrize(
    "expression",
    (
        None,
        {"operator": "add", "expressions": []},
        {"operator": "add", "expressions": "12"},
        {"operator": "unknown", "expressions": [1, 2]},
        {"operator": [], "expressions": [1, 2]},
        {"round": 1, "ndigits": "2"},
    ),
)
def test_malformed_formula_inputs_raise_invalid_expression_type_error(expression: Any) -> None:
    with pytest.raises(TypeError, match="Invalid expression"):
        compile_expression(expression)


@pytest.mark.parametrize("expressions", [1, None])
def test_non_iterable_expression_lists_raise_type_error(expressions: Any) -> None:
    with pytest.raises(TypeError):
        compile_expression({"operator": "add", "expressions": expressions})


def test_string_expression_list_items_are_resolved_as_names() -> None:
    with pytest.raises(TypeError, match="Invalid expression"):
        compile_expression({"operator": "add", "expressions": "12"})


@pytest.mark.parametrize("name", ["missing", "unknown", "not_registered", "field", "x"])
def test_missing_registered_formula_names_raise(name: str) -> None:
    with pytest.raises(FormulaNotFoundError, match=name):
        compile_expression(name)


@pytest.mark.parametrize(
    ("wrapper", "value", "error_type"),
    (
        ("sqrt", -1, ValueError),
        ("log10", 0, ValueError),
        ("log1p", -1.1, ValueError),
        ("log2", 0, ValueError),
        ("asin", 2, ValueError),
        ("acos", 2, ValueError),
        ("acosh", 0, ValueError),
        ("atanh", 1, ValueError),
        ("gamma", 0, ValueError),
        ("lgamma", 0, ValueError),
        ("exp", 1000, OverflowError),
        ("exp2", 1024, OverflowError),
    ),
)
def test_math_domain_and_overflow_errors_are_deferred(
    wrapper: str, value: float, error_type: type[Exception]
) -> None:
    formula = compile_expression({wrapper: value})

    with pytest.raises(error_type):
        formula(None)
