import operator
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal

import pytest
from pyformula import Formula, NumberType, OperatorFn


@dataclass(kw_only=True)
class Employee:
    name: str
    type: Literal["administrator", "teacher"] = "administrator"
    salary: float
    salary_decimal: Decimal = field(init=False)
    hourly_rate: float = 0.0

    def __post_init__(self) -> None:
        self.salary_decimal = Decimal(self.salary)


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
        "administrator_watch_cut": salary_var / working_days_var / 2,
        "teacher_watch_cut": hourly_rate_var / 2,
    }


@pytest.fixture
def lambda_formulas() -> dict[str, Formula[Employee]]:
    salary_var = Formula[Employee](lambda employee: employee.salary)
    hourly_rate_var = Formula[Employee](lambda employee: employee.hourly_rate, name="hourly_rate")
    working_days_var = Formula[Employee](lambda _: 30)

    return {
        "overtime_day": (salary_var / working_days_var) * 2,
        "half_salary_reward": salary_var / 2,
        "leaves_without_pay": salary_var / working_days_var,
        "administrator_watch_cut": salary_var / working_days_var / 2,
        "teacher_watch_cut": hourly_rate_var / 2,
    }


def test_formula_repr(normal_formulas: dict[str, Formula[Employee]]) -> None:
    assert repr(normal_formulas["overtime_day"]) == "Formula(((salary / working_days) * 2))"
    assert repr(normal_formulas["half_salary_reward"]) == "Formula((salary / 2))"
    assert repr(normal_formulas["leaves_without_pay"]) == "Formula((salary / working_days))"
    assert (
        repr(normal_formulas["administrator_watch_cut"]) == "Formula(((salary / working_days) / 2))"
    )
    assert repr(normal_formulas["teacher_watch_cut"]) == "Formula((hourly_rate / 2))"

    var = Formula[Employee](lambda obj: obj.hourly_rate, name="new_hourly_rate")

    complex_formula = abs(-var) / 2
    assert repr(complex_formula) == "Formula((|-new_hourly_rate| / 2))"


def test_lambda_formula_repr(lambda_formulas: dict[str, Formula[Employee]]) -> None:
    assert repr(lambda_formulas["overtime_day"]) == "Formula(((anonymous / anonymous) * 2))"
    assert repr(lambda_formulas["teacher_watch_cut"]) == "Formula((hourly_rate / 2))"


@pytest.mark.parametrize(
    (
        "user, "
        "overtime_day_value, "
        "half_salary_reward_value, "
        "leaves_without_pay_value, "
        "administrator_watch_cut_value, "
        "teacher_watch_cut_value"
    ),
    [
        (Employee(name="John", salary=1_500, hourly_rate=200), 100, 750, 50, 25, 100),
        (Employee(name="Jane", salary=4_500, hourly_rate=300), 300, 2_250, 150, 75, 150),
    ],
)
def test_formulas(  # noqa: PLR0913
    normal_formulas: dict[str, Formula[Employee]],
    lambda_formulas: dict[str, Formula[Employee]],
    user: Employee,
    overtime_day_value: float,
    half_salary_reward_value: float,
    leaves_without_pay_value: float,
    administrator_watch_cut_value: float,
    teacher_watch_cut_value: float,
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
    assert (
        normal_formulas["administrator_watch_cut"](user)
        == lambda_formulas["administrator_watch_cut"](user)
        == administrator_watch_cut_value
    )
    assert (
        normal_formulas["teacher_watch_cut"](user)
        == lambda_formulas["teacher_watch_cut"](user)
        == teacher_watch_cut_value
    )


def test_positive_formulas() -> None:
    negative_salary_var = Formula[Employee](lambda e: -e.salary)
    formula = +negative_salary_var / 2

    assert formula(Employee(name="John", salary=1_500, hourly_rate=200)) == -750


def test_negative_formulas() -> None:
    salary_var = Formula[Employee](lambda e: e.salary)
    formula = -salary_var / 2
    value = formula(Employee(name="John", salary=1_500, hourly_rate=200))

    assert isinstance(value, float)
    assert value == -750

    salary_var = Formula[Employee](lambda e: e.salary_decimal)
    formula = -salary_var / 2
    value = formula(Employee(name="John", salary=1_500, hourly_rate=200))

    assert isinstance(value, Decimal)
    assert value == Decimal(-750)


def test_abs_formulas() -> None:
    negative_salary_var = Formula[Employee](lambda e: -e.salary)
    formula = abs(negative_salary_var / 2)
    value = formula(Employee(name="John", salary=1_500, hourly_rate=200))

    assert isinstance(value, float)
    assert value == 750

    negative_salary_var = Formula[Employee](lambda e: -e.salary_decimal)
    formula = abs(negative_salary_var / 2)
    value = formula(Employee(name="John", salary=1_500, hourly_rate=200))

    assert isinstance(value, Decimal)
    assert value == Decimal(750)


@pytest.mark.parametrize(
    "n1, n2, expected_result, expected_result_type, operator_fn",
    (
        #####################################################################
        # add
        #####################################################################
        # int
        (1, 2, 3, int, operator.add),
        (1, 2.0, 3, float, operator.add),
        (1, Decimal("1.2"), Decimal("2.2"), Decimal, operator.add),
        # float
        (3.0, 2.0, 5, float, operator.add),
        (3.0, 2, 5, float, operator.add),
        (3.0, Decimal(2), Decimal(5), Decimal, operator.add),
        # Decimal
        (Decimal(3), Decimal(2), Decimal(5), Decimal, operator.add),
        (Decimal(3), 2, Decimal(5), Decimal, operator.add),
        (Decimal(3), 2.0, Decimal(5), Decimal, operator.add),
        #####################################################################
        # subtract
        #####################################################################
        # int
        (1, 2, -1, int, operator.sub),
        (1, 2.0, -1, float, operator.sub),
        (1, Decimal("1.2"), Decimal("-0.2"), Decimal, operator.sub),
        # float
        (3.0, 2.0, 1, float, operator.sub),
        (3.0, 2, 1, float, operator.sub),
        (3.0, Decimal(2), Decimal(1), Decimal, operator.sub),
        # Decimal
        (Decimal(3), Decimal(2), Decimal(1), Decimal, operator.sub),
        (Decimal(3), 2, Decimal(1), Decimal, operator.sub),
        (Decimal(3), 2.0, Decimal(1), Decimal, operator.sub),
        #####################################################################
        # multiply
        #####################################################################
        # int
        (1, 2, 2, int, operator.mul),
        (1, -2, -2, int, operator.mul),
        (1, 2.0, 2, float, operator.mul),
        (1, Decimal("1.2"), Decimal("1.2"), Decimal, operator.mul),
        # float
        (3.0, 2, 6, float, operator.mul),
        (3.0, -2, -6, float, operator.mul),
        (3.0, 2.0, 6, float, operator.mul),
        (3.0, Decimal(2), Decimal(6), Decimal, operator.mul),
        # Decimal
        (Decimal(3), 2, Decimal(6), Decimal, operator.mul),
        (Decimal(3), -2, Decimal(-6), Decimal, operator.mul),
        (Decimal(-3), 2, Decimal(-6), Decimal, operator.mul),
        (Decimal(3), 2.0, Decimal(6), Decimal, operator.mul),
        (Decimal(3), Decimal(2), Decimal(6), Decimal, operator.mul),
        #####################################################################
        # divide
        #####################################################################
        # int
        (1, 2, 0.5, float, operator.truediv),
        (1, 2.0, 0.5, float, operator.truediv),
        (1, Decimal(2), Decimal("0.5"), Decimal, operator.truediv),
        # float
        (3.0, 2, 1.5, float, operator.truediv),
        (3.0, 2.0, 1.5, float, operator.truediv),
        (3.0, Decimal(2), Decimal("1.5"), Decimal, operator.truediv),
        # Decimal
        (Decimal(3), 2, Decimal("1.5"), Decimal, operator.truediv),
        (Decimal(3), 2.0, Decimal("1.5"), Decimal, operator.truediv),
        (Decimal(3), Decimal(2), Decimal("1.5"), Decimal, operator.truediv),
        #####################################################################
        # modulo
        #####################################################################
        # int
        (1, 2, 1, int, operator.mod),
        (1, 2.0, 1, float, operator.mod),
        (1, Decimal("1.2"), Decimal(1), Decimal, operator.mod),
        # float
        (3.0, 2, 1.0, float, operator.mod),
        (3.0, 2.0, 1.0, float, operator.mod),
        (3.0, Decimal(2), Decimal(1), Decimal, operator.mod),
        # Decimal
        (Decimal(3), 2, Decimal(1), Decimal, operator.mod),
        (Decimal(3), 2.0, Decimal(1), Decimal, operator.mod),
        (Decimal(3), Decimal(2), Decimal(1), Decimal, operator.mod),
        #####################################################################
        # floor_divide
        #####################################################################
        # int
        (1, 2, 0, int, operator.floordiv),
        (1, 2.0, 0, float, operator.floordiv),
        (1, Decimal("1.2"), Decimal(0), Decimal, operator.floordiv),
        # float
        (3.0, 2, 1, float, operator.floordiv),
        (3.0, 2.0, 1, float, operator.floordiv),
        (3.0, Decimal(2), Decimal(1), Decimal, operator.floordiv),
        # Decimal
        (Decimal(3), 2, Decimal(1), Decimal, operator.floordiv),
        (Decimal(3), 2.0, Decimal(1), Decimal, operator.floordiv),
        (Decimal(3), Decimal(2), Decimal(1), Decimal, operator.floordiv),
        #####################################################################
        # power
        #####################################################################
        # int
        (2, 2, 4, int, operator.pow),
        (2, 2.0, 4, float, operator.pow),
        (2, Decimal(2), Decimal(4), Decimal, operator.pow),
        # float
        (2.0, 2, 4, float, operator.pow),
        (2.0, 2.0, 4, float, operator.pow),
        (2.0, Decimal(2), Decimal(4), Decimal, operator.pow),
        # Decimal
        (Decimal(2), 2, Decimal(4), Decimal, operator.pow),
        (Decimal(2), 2.0, Decimal(4), Decimal, operator.pow),
        (Decimal(2), Decimal(2), Decimal(4), Decimal, operator.pow),
        # TODO: add more tests for math functions like floor, ceil, etc. especially for Decimal
    ),
)
def test_formula_add_operator(
    n1: NumberType,
    n2: NumberType,
    expected_result: Any,
    expected_result_type: type[Any],
    operator_fn: OperatorFn,
) -> None:
    formula_1 = Formula(lambda _: n1)
    formula_2 = Formula(lambda _: n2)

    result_1 = (operator_fn(formula_1, formula_2))(None)  # type: ignore  # noqa: PGH003
    result_2 = (operator_fn(n1, formula_2))(None)  # type: ignore  # noqa: PGH003
    result_3 = (operator_fn(formula_1, n2))(None)  # type: ignore  # noqa: PGH003

    assert result_1 == result_2 == result_3 == expected_result
    assert isinstance(result_1, expected_result_type)
    assert isinstance(result_2, expected_result_type)
    assert isinstance(result_3, expected_result_type)
