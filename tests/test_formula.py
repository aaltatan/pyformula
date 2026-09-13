from dataclasses import dataclass
from typing import Literal

import pytest
from pyformula import Formula


@dataclass(frozen=True, kw_only=True)
class Employee:
    name: str
    type: Literal["administrator", "teacher"] = "administrator"
    salary: float
    hourly_rate: float = 0.0


@pytest.fixture
def normal_formulas() -> dict[str, Formula[Employee]]:
    def salary(employee: Employee) -> float:
        return employee.salary

    def hourly_rate(employee: Employee) -> float:
        return employee.hourly_rate

    def working_days(_: Employee) -> float:
        return 30

    salary_var = Formula(salary)
    hourly_rate_var = Formula(hourly_rate)
    working_days_var = Formula(working_days)

    return {
        "overtime_day": (salary_var / working_days_var) * 2,
        "half_salary_reward": salary_var / 2,
        "leaves_without_pay": salary_var / working_days_var,
        "administrator_watch_cut": salary_var / 30 * 2,
    }


@pytest.fixture
def lambda_formulas() -> dict[str, Formula[Employee]]:
    salary_var = Formula[Employee](lambda employee: employee.salary)
    working_days_var = Formula[Employee](lambda _: 30)

    return {
        "overtime_day": (salary_var / working_days_var) * 2,
        "half_salary_reward": salary_var / 2,
        "leaves_without_pay": salary_var / working_days_var,
    }


@pytest.mark.parametrize(
    "user, overtime_day_value, half_salary_reward_value, leaves_without_pay_value",
    [
        (Employee(name="John", salary=1_500), 100, 750, 50),
        (Employee(name="Jane", salary=4_500), 300, 2_250, 150),
    ],
)
def test_formulas(  # noqa: PLR0913
    normal_formulas: dict[str, Formula[Employee]],
    lambda_formulas: dict[str, Formula[Employee]],
    user: Employee,
    overtime_day_value: float,
    half_salary_reward_value: float,
    leaves_without_pay_value: float,
) -> None:
    assert (
        normal_formulas["overtime_day"](user)
        == lambda_formulas["overtime_day"](user)
        == overtime_day_value
    )
    assert (
        normal_formulas["half_salary_reward"](user)
        == lambda_formulas["half_salary_reward"](user)
        == half_salary_reward_value
    )
    assert (
        normal_formulas["leaves_without_pay"](user)
        == lambda_formulas["leaves_without_pay"](user)
        == leaves_without_pay_value
    )
