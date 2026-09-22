import math
from dataclasses import dataclass
from typing import Any

import pytest
from pyformula import FormulaCompiler, VariablesRegistry


@dataclass
class Triangle:
    base: float
    height: float
    side_a: float
    side_b: float
    side_c: float


@dataclass
class Rectangle:
    width: float
    height: float


@dataclass
class Employee:
    salary: float
    hours: float
    bonus: float
    tax_rate: float


def triangle_compiler() -> FormulaCompiler[Triangle]:
    registry = VariablesRegistry[Triangle]()

    for field in ("base", "height", "side_a", "side_b", "side_c"):
        registry.register_variable(
            lambda triangle, field=field: getattr(triangle, field), name=field
        )

    return FormulaCompiler(registry.variables)


def rectangle_compiler() -> FormulaCompiler[Rectangle]:
    registry = VariablesRegistry[Rectangle]()

    for field in ("width", "height"):
        registry.register_variable(
            lambda rectangle, field=field: getattr(rectangle, field), name=field
        )

    return FormulaCompiler(registry.variables)


def employee_compiler() -> FormulaCompiler[Employee]:
    registry = VariablesRegistry[Employee]()

    for field in ("salary", "hours", "bonus", "tax_rate"):
        registry.register_variable(
            lambda employee, field=field: getattr(employee, field), name=field
        )

    return FormulaCompiler(registry.variables)


TRIANGLES = [
    Triangle(3, 4, 3, 4, 5),
    Triangle(5, 12, 5, 12, 13),
    Triangle(8, 15, 8, 15, 17),
    Triangle(6, 8, 6, 8, 10),
    Triangle(9, 12, 9, 12, 15),
    Triangle(10, 10, 10, 10, 10),
    Triangle(1.5, 2.5, 2, 2.5, 3),
    Triangle(7.25, 3.5, 4, 5, 6),
]

TRIANGLE_FORMULAS = [
    (
        "area",
        {
            "operator": "divide",
            "expressions": [{"operator": "multiply", "expressions": ["base", "height"]}, 2],
        },
        lambda triangle: triangle.base * triangle.height / 2,
    ),
    (
        "perimeter",
        {"operator": "add", "expressions": ["side_a", "side_b", "side_c"]},
        lambda triangle: triangle.side_a + triangle.side_b + triangle.side_c,
    ),
    (
        "semiperimeter",
        {
            "operator": "divide",
            "expressions": [{"operator": "add", "expressions": ["side_a", "side_b", "side_c"]}, 2],
        },
        lambda triangle: (triangle.side_a + triangle.side_b + triangle.side_c) / 2,
    ),
    (
        "heron_area",
        {
            "sqrt": {
                "operator": "multiply",
                "expressions": [
                    {
                        "operator": "divide",
                        "expressions": [
                            {"operator": "add", "expressions": ["side_a", "side_b", "side_c"]},
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
                                        "expressions": ["side_a", "side_b", "side_c"],
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
                                        "expressions": ["side_a", "side_b", "side_c"],
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
                                        "expressions": ["side_a", "side_b", "side_c"],
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
]


@pytest.mark.parametrize("formula_name, expression, expected_fn", TRIANGLE_FORMULAS)
@pytest.mark.parametrize("triangle", TRIANGLES)
def test_compiles_nested_triangle_formulas(
    formula_name: str, expression: Any, expected_fn: Any, triangle: Triangle
) -> None:
    result = triangle_compiler().compile(expression)(triangle)

    assert result == pytest.approx(expected_fn(triangle)), formula_name


RECTANGLES = [
    Rectangle(1, 1),
    Rectangle(2, 3),
    Rectangle(4, 5),
    Rectangle(10, 0.5),
    Rectangle(12.5, 8.25),
    Rectangle(100, 200),
    Rectangle(0, 9),
    Rectangle(-4, 3),
]

RECTANGLE_FORMULAS = [
    (
        "area",
        {"operator": "multiply", "expressions": ["width", "height"]},
        lambda rectangle: rectangle.width * rectangle.height,
    ),
    (
        "perimeter",
        {
            "operator": "multiply",
            "expressions": [2, {"operator": "add", "expressions": ["width", "height"]}],
        },
        lambda rectangle: 2 * (rectangle.width + rectangle.height),
    ),
    (
        "diagonal",
        {
            "sqrt": {
                "operator": "add",
                "expressions": [
                    {"operator": "power", "expressions": ["width", 2]},
                    {"operator": "power", "expressions": ["height", 2]},
                ],
            }
        },
        lambda rectangle: math.sqrt(rectangle.width**2 + rectangle.height**2),
    ),
    (
        "scaled_area",
        {
            "operator": "multiply",
            "expressions": [{"operator": "multiply", "expressions": ["width", "height"]}, 2.5],
        },
        lambda rectangle: rectangle.width * rectangle.height * 2.5,
    ),
]


@pytest.mark.parametrize("formula_name, expression, expected_fn", RECTANGLE_FORMULAS)
@pytest.mark.parametrize("rectangle", RECTANGLES)
def test_compiles_nested_rectangle_formulas(
    formula_name: str, expression: Any, expected_fn: Any, rectangle: Rectangle
) -> None:
    result = rectangle_compiler().compile(expression)(rectangle)

    assert result == pytest.approx(expected_fn(rectangle)), formula_name


EMPLOYEES = [
    Employee(1000, 40, 0, 0.1),
    Employee(1500, 37.5, 100, 0.2),
    Employee(2500, 20, 250, 0.25),
    Employee(5000, 160, 1000, 0.3),
    Employee(0, 40, 50, 0.0),
    Employee(-100, 10, -20, 0.1),
    Employee(1234.56, 38.5, 12.34, 0.175),
    Employee(99999, 1, 1, 0.5),
]

EMPLOYEE_FORMULAS = [
    (
        "gross",
        {"operator": "add", "expressions": ["salary", "bonus"]},
        lambda employee: employee.salary + employee.bonus,
    ),
    (
        "hourly_pay",
        {"operator": "divide", "expressions": ["salary", "hours"]},
        lambda employee: employee.salary / employee.hours,
    ),
    (
        "tax",
        {
            "operator": "multiply",
            "expressions": [{"operator": "add", "expressions": ["salary", "bonus"]}, "tax_rate"],
        },
        lambda employee: (employee.salary + employee.bonus) * employee.tax_rate,
    ),
    (
        "net",
        {
            "operator": "subtract",
            "expressions": [
                {"operator": "add", "expressions": ["salary", "bonus"]},
                {
                    "operator": "multiply",
                    "expressions": [
                        {"operator": "add", "expressions": ["salary", "bonus"]},
                        "tax_rate",
                    ],
                },
            ],
        },
        lambda employee: (employee.salary + employee.bonus) * (1 - employee.tax_rate),
    ),
    (
        "rounded_net",
        {
            "round": {
                "operator": "subtract",
                "expressions": [
                    {"operator": "add", "expressions": ["salary", "bonus"]},
                    {
                        "operator": "multiply",
                        "expressions": [
                            {"operator": "add", "expressions": ["salary", "bonus"]},
                            "tax_rate",
                        ],
                    },
                ],
            },
            "ndigits": 2,
        },
        lambda employee: round((employee.salary + employee.bonus) * (1 - employee.tax_rate), 2),
    ),
]


@pytest.mark.parametrize("formula_name, expression, expected_fn", EMPLOYEE_FORMULAS)
@pytest.mark.parametrize("employee", EMPLOYEES)
def test_compiles_employee_payroll_formulas(
    formula_name: str, expression: Any, expected_fn: Any, employee: Employee
) -> None:
    result = employee_compiler().compile(expression)(employee)

    assert result == pytest.approx(expected_fn(employee)), formula_name
