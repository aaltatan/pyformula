from dataclasses import dataclass
from typing import Any

import pytest
from pyformula import Expression, Formula, FormulaCompiler, VariablesRegistry


@dataclass
class Employee:
    name: str
    salary: float
    hourly_rate: float


@pytest.fixture
def variables() -> dict[str, Formula[Employee]]:
    reg = VariablesRegistry[Employee]()

    @reg.variable()
    def salary(employee: Employee) -> float:
        return employee.salary

    return reg.variables


@pytest.fixture
def compiler(variables: dict[str, Formula[Employee]]) -> FormulaCompiler[Employee]:
    return FormulaCompiler[Employee](variables)


@pytest.fixture
def employee() -> Employee:
    return Employee(name="John Doe", salary=1500, hourly_rate=20)


@pytest.mark.parametrize(
    "schema, expected",
    [
        (
            "salary",
            1_500,
        ),
        (
            500,
            500,
        ),
        (
            {
                "absolute": -500,
            },
            500,
        ),
        (
            {
                "absolute": {
                    "negative": 500,
                }
            },
            500,
        ),
        (
            {
                "operator": "divide",
                "expressions": [
                    "salary",
                    2,
                ],
            },
            750,
        ),
        (
            {
                "negative": {
                    "operator": "divide",
                    "expressions": [
                        "salary",
                        {
                            "negative": {
                                "negative": 2,
                            }
                        },
                    ],
                }
            },
            -750,
        ),
    ],
)
def test_formula_schema(
    compiler: FormulaCompiler[Employee],
    employee: Employee,
    schema: Expression,
    expected: Any,
) -> None:
    formula = compiler.compile(schema)
    assert formula(employee) == expected
