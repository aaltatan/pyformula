import math
from dataclasses import dataclass
from typing import Any

import pytest
from pyformula import FormulaCompiler, VariablesRegistry


@dataclass(kw_only=True)
class Triangle:
    base: float
    height: float
    side_a: float
    side_b: float
    side_c: float


@dataclass(kw_only=True)
class Rectangle:
    width: float
    height: float


@dataclass(kw_only=True)
class Employee:
    salary: float
    hours: float
    bonus: float
    tax_rate: float


@pytest.fixture
def triangle_compiler() -> FormulaCompiler[Triangle]:
    registry = VariablesRegistry[Triangle]()

    for field in ("base", "height", "side_a", "side_b", "side_c"):
        registry.register_variable(
            lambda triangle, field=field: getattr(triangle, field), name=field
        )

    return FormulaCompiler(registry.variables)


@pytest.fixture
def rectangle_compiler() -> FormulaCompiler[Rectangle]:
    registry = VariablesRegistry[Rectangle]()

    for field in ("width", "height"):
        registry.register_variable(
            lambda rectangle, field=field: getattr(rectangle, field), name=field
        )

    return FormulaCompiler(registry.variables)


@pytest.fixture
def employee_compiler() -> FormulaCompiler[Employee]:
    registry = VariablesRegistry[Employee]()

    for field in ("salary", "hours", "bonus", "tax_rate"):
        registry.register_variable(
            lambda employee, field=field: getattr(employee, field), name=field
        )

    return FormulaCompiler(registry.variables)


@pytest.mark.parametrize(
    "expression, expected_fn",
    [
        (
            {
                "operator": "divide",
                "expressions": [
                    {
                        "operator": "multiply",
                        "expressions": [
                            "base",
                            "height",
                        ],
                    },
                    2,
                ],
            },
            lambda triangle: (triangle.base * triangle.height) / 2,
        ),
        (
            {
                "operator": "add",
                "expressions": [
                    "side_a",
                    "side_b",
                    "side_c",
                ],
            },
            lambda triangle: triangle.side_a + triangle.side_b + triangle.side_c,
        ),
        (
            {
                "operator": "divide",
                "expressions": [
                    {
                        "operator": "add",
                        "expressions": [
                            "side_a",
                            "side_b",
                            "side_c",
                        ],
                    },
                    2,
                ],
            },
            lambda triangle: (triangle.side_a + triangle.side_b + triangle.side_c) / 2,
        ),
        (
            {
                "sqrt": {
                    "operator": "multiply",
                    "expressions": [
                        {
                            "operator": "divide",
                            "expressions": [
                                {
                                    "operator": "add",
                                    "expressions": [
                                        "side_a",
                                        "side_b",
                                        "side_c",
                                    ],
                                },
                                2,
                            ],
                        },
                        {
                            "operator": "subtract",
                            "expressions": [
                                {
                                    "operator": "divide",
                                    "expressions": [
                                        {
                                            "operator": "add",
                                            "expressions": [
                                                "side_a",
                                                "side_b",
                                                "side_c",
                                            ],
                                        },
                                        2,
                                    ],
                                },
                                "side_a",
                            ],
                        },
                        {
                            "operator": "subtract",
                            "expressions": [
                                {
                                    "operator": "divide",
                                    "expressions": [
                                        {
                                            "operator": "add",
                                            "expressions": [
                                                "side_a",
                                                "side_b",
                                                "side_c",
                                            ],
                                        },
                                        2,
                                    ],
                                },
                                "side_b",
                            ],
                        },
                        {
                            "operator": "subtract",
                            "expressions": [
                                {
                                    "operator": "divide",
                                    "expressions": [
                                        {
                                            "operator": "add",
                                            "expressions": [
                                                "side_a",
                                                "side_b",
                                                "side_c",
                                            ],
                                        },
                                        2,
                                    ],
                                },
                                "side_c",
                            ],
                        },
                    ],
                }
            },
            lambda triangle: math.sqrt(
                ((triangle.side_a + triangle.side_b + triangle.side_c) / 2)
                * (((triangle.side_a + triangle.side_b + triangle.side_c) / 2) - triangle.side_a)
                * (((triangle.side_a + triangle.side_b + triangle.side_c) / 2) - triangle.side_b)
                * (((triangle.side_a + triangle.side_b + triangle.side_c) / 2) - triangle.side_c)
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    "triangle",
    [
        Triangle(base=3, height=4, side_a=3, side_b=4, side_c=5),
        Triangle(base=5, height=12, side_a=5, side_b=12, side_c=13),
        Triangle(base=8, height=15, side_a=8, side_b=15, side_c=17),
        Triangle(base=6, height=8, side_a=6, side_b=8, side_c=10),
        Triangle(base=9, height=12, side_a=9, side_b=12, side_c=15),
        Triangle(base=10, height=10, side_a=10, side_b=10, side_c=10),
        Triangle(base=1.5, height=2.5, side_a=2, side_b=2.5, side_c=3),
        Triangle(base=7.25, height=3.5, side_a=4, side_b=5, side_c=6),
    ],
)
def test_compiles_nested_triangle_formulas(
    expression: Any,
    expected_fn: Any,
    triangle: Triangle,
    triangle_compiler: FormulaCompiler[Triangle],
) -> None:
    fm = triangle_compiler.compile(expression)
    assert fm(triangle) == pytest.approx(expected_fn(triangle))


@pytest.mark.parametrize(
    "expression, expected_fn",
    [
        (
            {
                "operator": "multiply",
                "expressions": [
                    "width",
                    "height",
                ],
            },
            lambda rectangle: rectangle.width * rectangle.height,
        ),
        (
            {
                "operator": "multiply",
                "expressions": [
                    2,
                    {
                        "operator": "add",
                        "expressions": [
                            "width",
                            "height",
                        ],
                    },
                ],
            },
            lambda rectangle: 2 * (rectangle.width + rectangle.height),
        ),
        (
            {
                "sqrt": {
                    "operator": "add",
                    "expressions": [
                        {
                            "operator": "power",
                            "expressions": [
                                "width",
                                2,
                            ],
                        },
                        {
                            "operator": "power",
                            "expressions": [
                                "height",
                                2,
                            ],
                        },
                    ],
                }
            },
            lambda rectangle: math.sqrt(rectangle.width**2 + rectangle.height**2),
        ),
        (
            {
                "operator": "multiply",
                "expressions": [
                    {
                        "operator": "multiply",
                        "expressions": [
                            "width",
                            "height",
                        ],
                    },
                    2.5,
                ],
            },
            lambda rectangle: rectangle.width * rectangle.height * 2.5,
        ),
    ],
)
@pytest.mark.parametrize(
    "rectangle",
    [
        Rectangle(width=1, height=1),
        Rectangle(width=2, height=3),
        Rectangle(width=4, height=5),
        Rectangle(width=10, height=0.5),
        Rectangle(width=12.5, height=8.25),
        Rectangle(width=100, height=200),
        Rectangle(width=0, height=9),
        Rectangle(width=-4, height=3),
    ],
)
def test_compiles_nested_rectangle_formulas(
    expression: Any,
    expected_fn: Any,
    rectangle: Rectangle,
    rectangle_compiler: FormulaCompiler[Rectangle],
) -> None:
    result = rectangle_compiler.compile(expression)(rectangle)
    assert result == pytest.approx(expected_fn(rectangle))


@pytest.mark.parametrize(
    "expression, expected_fn",
    [
        (
            {
                "operator": "add",
                "expressions": [
                    "salary",
                    "bonus",
                ],
            },
            lambda employee: employee.salary + employee.bonus,
        ),
        (
            {
                "operator": "divide",
                "expressions": [
                    "salary",
                    "hours",
                ],
            },
            lambda employee: employee.salary / employee.hours,
        ),
        (
            {
                "operator": "multiply",
                "expressions": [
                    {
                        "operator": "add",
                        "expressions": [
                            "salary",
                            "bonus",
                        ],
                    },
                    "tax_rate",
                ],
            },
            lambda employee: (employee.salary + employee.bonus) * employee.tax_rate,
        ),
        (
            {
                "operator": "subtract",
                "expressions": [
                    {
                        "operator": "add",
                        "expressions": [
                            "salary",
                            "bonus",
                        ],
                    },
                    {
                        "operator": "multiply",
                        "expressions": [
                            {
                                "operator": "add",
                                "expressions": [
                                    "salary",
                                    "bonus",
                                ],
                            },
                            "tax_rate",
                        ],
                    },
                ],
            },
            lambda employee: (employee.salary + employee.bonus) * (1 - employee.tax_rate),
        ),
        (
            {
                "round": {
                    "operator": "subtract",
                    "expressions": [
                        {
                            "operator": "add",
                            "expressions": [
                                "salary",
                                "bonus",
                            ],
                        },
                        {
                            "operator": "multiply",
                            "expressions": [
                                {
                                    "operator": "add",
                                    "expressions": [
                                        "salary",
                                        "bonus",
                                    ],
                                },
                                "tax_rate",
                            ],
                        },
                    ],
                },
                "ndigits": 2,
            },
            lambda employee: round((employee.salary + employee.bonus) * (1 - employee.tax_rate), 2),
        ),
    ],
)
@pytest.mark.parametrize(
    "employee",
    [
        Employee(salary=1000, hours=40, bonus=0, tax_rate=0.1),
        Employee(salary=1500, hours=37.5, bonus=100, tax_rate=0.2),
        Employee(salary=2500, hours=20, bonus=250, tax_rate=0.25),
        Employee(salary=5000, hours=160, bonus=1000, tax_rate=0.3),
        Employee(salary=0, hours=40, bonus=50, tax_rate=0.0),
        Employee(salary=-100, hours=10, bonus=-20, tax_rate=0.1),
        Employee(salary=1234.56, hours=38.5, bonus=12.34, tax_rate=0.175),
        Employee(salary=99999, hours=1, bonus=1, tax_rate=0.5),
    ],
)
def test_compiles_employee_payroll_formulas(
    expression: Any,
    expected_fn: Any,
    employee: Employee,
    employee_compiler: FormulaCompiler[Employee],
) -> None:
    result = employee_compiler.compile(expression)(employee)
    assert result == pytest.approx(expected_fn(employee))
