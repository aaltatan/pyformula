from decimal import Decimal
from typing import Any

import pytest
from pyformula import FormulaCompiler, Operator


@pytest.fixture
def compiler() -> FormulaCompiler[Any]:
    return FormulaCompiler[Any]({})


OPERATOR_CASES = (
    [
        ("add", [left, right], left + right)
        for left, right in ((-10, -3), (-10, 0), (-10, 3), (0, 10), (1.5, 2.5), (100, -25))
    ]
    + [
        ("subtract", [left, right], left - right)
        for left, right in ((-10, -3), (-10, 0), (-10, 3), (0, 10), (1.5, 2.5), (100, -25))
    ]
    + [
        ("multiply", [left, right], left * right)
        for left, right in ((-10, -3), (-10, 0), (-10, 3), (0, 10), (1.5, 2.5), (100, -25))
    ]
    + [
        ("divide", [left, right], left / right)
        for left, right in ((-10, -3), (-10, 3), (10, 2), (1.5, 2.5), (100, -25), (7, 2))
    ]
    + [
        ("modulo", [left, right], left % right)
        for left, right in ((-10, -3), (-10, 3), (10, 2), (1.5, 2.5), (100, -25), (7, 2))
    ]
    + [
        ("floor_divide", [left, right], left // right)
        for left, right in ((-10, -3), (-10, 3), (10, 2), (1.5, 2.5), (100, -25), (7, 2))
    ]
    + [
        ("power", [left, right], left**right)
        for left, right in ((-2, 3), (-2, 2), (0, 3), (2, 0), (2, 3), (1.5, 2))
    ]
)


@pytest.mark.parametrize("operator, expressions, expected", OPERATOR_CASES)
def test_compiles_binary_operator_cases(
    operator: Operator,
    expressions: list[Any],
    expected: Any,
    compiler: FormulaCompiler[Any],
) -> None:
    fm = compiler.compile({"operator": operator, "expressions": expressions})
    assert fm(None) == expected


@pytest.mark.parametrize(
    "value, expected, expected_type",
    [
        (value, value, type(value))
        for value in (
            -10,
            -1,
            0,
            1,
            10,
            2**40,
            -(2**40),
            0.0,
            -0.5,
            1.25,
            10.5,
            float("inf"),
            float("-inf"),
            Decimal(0),
            Decimal("-12.50"),
            Decimal("999999.125"),
        )
    ],
)
def test_compiles_numeric_literal_cases(
    value: Any,
    expected: Any,
    expected_type: type[Any],
    compiler: FormulaCompiler[Any],
) -> None:
    fm = compiler.compile(value)
    result = fm(None)
    assert result == expected
    assert isinstance(result, expected_type)


NESTED_CASES = [
    (
        {
            "operator": "add",
            "expressions": [
                {
                    "operator": "multiply",
                    "expressions": [
                        2,
                        3,
                    ],
                },
                {
                    "negative": {
                        "operator": "subtract",
                        "expressions": [
                            10,
                            4,
                        ],
                    }
                },
            ],
        },
        0,
    ),
    (
        {
            "operator": "divide",
            "expressions": [
                {
                    "operator": "multiply",
                    "expressions": [
                        18,
                        5,
                    ],
                },
                {
                    "operator": "add",
                    "expressions": [
                        3,
                        2,
                    ],
                },
            ],
        },
        18,
    ),
    (
        {
            "operator": "power",
            "expressions": [
                {
                    "operator": "add",
                    "expressions": [
                        1,
                        2,
                    ],
                },
                {
                    "operator": "multiply",
                    "expressions": [
                        2,
                        3,
                    ],
                },
            ],
        },
        729,
    ),
    (
        {
            "absolute": {
                "operator": "subtract",
                "expressions": [
                    {
                        "operator": "multiply",
                        "expressions": [
                            4,
                            7,
                        ],
                    },
                    {
                        "operator": "power",
                        "expressions": [
                            3,
                            3,
                        ],
                    },
                ],
            }
        },
        1,
    ),
    (
        {
            "round": {
                "operator": "divide",
                "expressions": [
                    {
                        "operator": "add",
                        "expressions": [
                            100,
                            1,
                        ],
                    },
                    3,
                ],
            },
            "ndigits": 2,
        },
        33.67,
    ),
]


def _nested_variants() -> list[tuple[Any, Any]]:
    cases = list(NESTED_CASES)
    for value in range(-12, 13):
        expression: Any = value
        for wrapper in ("positive", "absolute", "negative", "negative"):
            expression = {wrapper: expression}
        cases.append((expression, abs(value)))
    return cases


@pytest.mark.parametrize("expression, expected", _nested_variants())
def test_compiles_nested_formula_variants(
    expression: Any,
    expected: Any,
    compiler: FormulaCompiler[Any],
) -> None:
    assert compiler.compile(expression)(None) == expected


@pytest.mark.parametrize(
    "operator, expressions, expected",
    (
        ("add", [1, 2, 3, 4, 5], 15),
        ("subtract", [100, 10, 5, 2], 83),
        ("multiply", [2, 3, 4, 5], 120),
        ("divide", [120, 5, 3, 2], 4.0),
        ("modulo", [100, 9, 4], 1),
        ("floor_divide", [100, 9, 4], 2),
        ("power", [2, 3, 2], 64),
    ),
)
def test_reduces_formula_expression_lists_left_to_right(
    operator: Operator,
    expressions: list[int],
    expected: Any,
    compiler: FormulaCompiler[Any],
) -> None:
    fm = compiler.compile({"operator": operator, "expressions": expressions})  # type: ignore  # noqa: PGH003
    assert fm(None) == expected


@pytest.mark.parametrize("value", range(-25, 26))
def test_single_expression_operator_returns_value(
    value: int,
    compiler: FormulaCompiler[Any],
) -> None:
    fm = compiler.compile({"operator": "multiply", "expressions": [value]})
    assert fm(None) == value
