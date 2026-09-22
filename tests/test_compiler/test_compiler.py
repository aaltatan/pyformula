import math
from decimal import Decimal
from typing import Any

import pytest
from pyformula import Formula, FormulaCompiler
from pyformula.compiler.models import is_formula_dict
from pyformula.exceptions import FormulaNotFoundError


def compile_formula(expressions: list[Any], operator: str = "add") -> Formula[Any]:
    compiler = FormulaCompiler[Any]({"value": Formula(lambda _: 10)})
    return compiler.compile({"operator": operator, "expressions": expressions})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("operator", "expressions", "expected"),
    (
        ("add", [2, 3, 4], 9),
        ("subtract", [20, 3, 2], 15),
        ("multiply", [2, 3, 4], 24),
        ("divide", [24, 3, 2], 4.0),
        ("modulo", [23, 6, 4], 1),
        ("floor_divide", [23, 6, 2], 1),
        ("power", [2, 3, 2], 64),
    ),
)
def test_compiles_all_operators(operator: str, expressions: list[int], expected: float) -> None:
    assert compile_formula(expressions, operator)(None) == expected


@pytest.mark.parametrize(
    ("value", "expected", "expected_type"),
    ((0, 0, int), (1.25, 1.25, float), (Decimal("2.5"), Decimal("2.5"), Decimal)),
)
def test_compiles_numeric_literals(value: Any, expected: Any, expected_type: type[Any]) -> None:
    result = compile_formula([value])(None)

    assert result == expected
    assert isinstance(result, expected_type)


def test_compiles_registered_formula() -> None:
    formula = Formula(lambda value: value * 2)  # type: ignore[operator]
    compiler = FormulaCompiler[int]({"double": formula})

    assert compiler.compile({"operator": "add", "expressions": ["double", 3]})(4) == 11


def test_compiles_nested_formula() -> None:
    formula = {
        "operator": "multiply",
        "expressions": [
            {
                "operator": "add",
                "expressions": [
                    2,
                    3,
                ],
            },
            {"negative": 4},
        ],
    }

    assert compile_formula([formula])(None) == -20


@pytest.mark.parametrize(
    ("wrapper", "expected"),
    (
        ({"positive": {"negative": 4}}, -4),
        ({"negative": {"positive": -4}}, 4),
        ({"absolute": {"negative": 4}}, 4),
        ({"round": 12.345, "ndigits": 2}, 12.35),
    ),
)
def test_compiles_basic_wrappers(wrapper: dict[str, Any], expected: Any) -> None:
    assert compile_formula([wrapper])(None) == expected


@pytest.mark.parametrize(
    ("function_name", "value", "expected"),
    (
        ("ceil", 1.2, math.ceil(1.2)),
        ("floor", -1.2, math.floor(-1.2)),
        ("trunc", -1.8, math.trunc(-1.8)),
        ("sqrt", 9, math.sqrt(9)),
        ("cbrt", -27, math.cbrt(-27)),
        ("exp", 1, math.exp(1)),
        ("exp2", 3, math.exp2(3)),
        ("expm1", 1, math.expm1(1)),
        ("log10", 100, math.log10(100)),
        ("log1p", 1, math.log1p(1)),
        ("log2", 8, math.log2(8)),
        ("sin", math.pi / 2, math.sin(math.pi / 2)),
        ("sinh", 1, math.sinh(1)),
        ("asin", 1, math.asin(1)),
        ("asinh", 1, math.asinh(1)),
        ("cos", math.pi, math.cos(math.pi)),
        ("cosh", 1, math.cosh(1)),
        ("acos", 1, math.acos(1)),
        ("acosh", 2, math.acosh(2)),
        ("tan", math.pi / 4, math.tan(math.pi / 4)),
        ("tanh", 1, math.tanh(1)),
        ("atan", 1, math.atan(1)),
        ("atanh", 0.5, math.atanh(0.5)),
        ("degrees", math.pi, math.degrees(math.pi)),
        ("radians", 180, math.radians(180)),
        ("erf", 1, math.erf(1)),
        ("erfc", 1, math.erfc(1)),
        ("gamma", 5, math.gamma(5)),
        ("lgamma", 5, math.lgamma(5)),
        ("fabs", -1.25, math.fabs(-1.25)),
        ("ulp", 1.0, math.ulp(1.0)),
    ),
)
def test_compiles_every_math_wrapper(function_name: str, value: Any, expected: float) -> None:
    result = compile_formula([{function_name: value}])(None)

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    ("function_name", "value", "error_type"),
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
def test_compiled_math_wrapper_preserves_domain_errors(
    function_name: str, value: Any, error_type: type[Exception]
) -> None:
    with pytest.raises(error_type):
        compile_formula([{function_name: value}])(None)


def test_compiles_deeply_nested_wrappers_and_operations() -> None:
    expression: Any = 2
    for _ in range(25):
        expression = {"negative": {"absolute": {"positive": expression}}}

    assert compile_formula([expression])(None) == -2


def test_missing_formula_name_raises() -> None:
    with pytest.raises(FormulaNotFoundError, match="missing"):
        compile_formula(["missing"])


@pytest.mark.parametrize(
    "expression",
    (
        {},
        {"unknown": 1},
        {"absolute": 1, "extra": 2},
        {"round": 1},
        {"round": 1, "ndigits": 2, "extra": 3},
        {"operator": "add", "expression": [1, 2]},
    ),
)
def test_invalid_expression_shape_raises_type_error(expression: dict[str, Any]) -> None:
    with pytest.raises(TypeError, match="Invalid expression"):
        compile_formula([expression])


def test_formula_dict_guard_accepts_the_compiler_shape() -> None:
    assert is_formula_dict({"operator": "add", "expressions": [1, 2]})
    assert not is_formula_dict({"operator": "add", "expression": [1, 2]})


def test_empty_expressions_raise() -> None:
    compiler = FormulaCompiler[Any]({})

    with pytest.raises(TypeError, match="Invalid expression"):
        compiler.compile({"operator": "add", "expressions": []})


def test_unknown_operator_raises_when_multiple_expressions_are_present() -> None:
    with pytest.raises(TypeError, match="Invalid expression"):
        compile_formula([1, 2], "unknown")(None)


@pytest.mark.parametrize(
    ("left", "right", "operator", "expected"),
    (
        (Decimal("1.5"), 2.0, "add", Decimal("3.5")),
        (2.0, Decimal("1.5"), "subtract", Decimal("0.5")),
        (Decimal(3), 2.0, "multiply", Decimal(6)),
        (Decimal(3), 2.0, "divide", Decimal("1.5")),
        (Decimal(5), 2.0, "modulo", Decimal(1)),
        (Decimal(5), 2.0, "floor_divide", Decimal(2)),
        (Decimal(2), 3.0, "power", Decimal(8)),
    ),
)
def test_compiler_handles_decimal_float_operator_pairs(
    left: Any, right: Any, operator: str, expected: Decimal
) -> None:
    assert compile_formula([left, right], operator)(None) == expected
