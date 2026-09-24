from dataclasses import dataclass
from typing import Literal

from pyformula import variable


@dataclass(kw_only=True)
class Employee:
    name: str
    type: Literal["administrator", "teacher"] = "administrator"
    salary: float
    hourly_rate: float = 0.0


@variable()
def salary(employee: Employee) -> float:
    return employee.salary


@variable()
def hourly_rate(employee: Employee) -> float:
    return employee.hourly_rate


@variable(name="days")
def working_days(_: Employee) -> float:
    return 30


def test_variable() -> None:
    employee = Employee(name="John Doe", salary=1000, hourly_rate=20)
    formula = salary + hourly_rate + working_days + 3

    assert repr(formula) == "Formula((((salary + hourly_rate) + days) + 3))"
    assert formula(employee) == 1_053


def test_variable_preserves_original_function_metadata() -> None:
    @variable()
    def bonus(employee: Employee) -> float:
        """Return the employee's bonus."""
        return employee.salary * 0.1

    assert bonus.__doc__ == "Return the employee's bonus."
    assert bonus.__wrapped__.__name__ == "bonus"  # type: ignore[attr-defined]


def test_variable_explicit_name_overrides_str_but_keeps_function_metadata() -> None:
    @variable(name="days")
    def working_days_variable(_: Employee) -> float:
        """Return the number of working days."""
        return 30

    assert str(working_days_variable) == "days"
    assert working_days_variable.__doc__ == "Return the number of working days."
