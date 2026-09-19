from dataclasses import dataclass
from typing import Literal

from pyformula import formula


@dataclass(kw_only=True)
class Employee:
    name: str
    type: Literal["administrator", "teacher"] = "administrator"
    salary: float
    hourly_rate: float = 0.0


@formula()
def salary(employee: Employee) -> float:
    return employee.salary


@formula()
def hourly_rate(employee: Employee) -> float:
    return employee.hourly_rate


@formula(name="days")
def working_days(_: Employee) -> float:
    return 30


def test_variable() -> None:
    employee = Employee(name="John Doe", salary=1000, hourly_rate=20)
    fm = salary + hourly_rate + working_days + 3

    assert repr(fm) == "Formula((((salary + hourly_rate) + days) + 3))"
    assert fm(employee) == 1_053
