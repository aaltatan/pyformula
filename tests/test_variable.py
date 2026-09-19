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
