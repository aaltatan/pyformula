import pytest
from pyformula.exceptions import FormulaAlreadyRegisteredError, FormulaNotRegisteredError
from pyformula.formula import Formula
from pyformula.registry import VariablesRegistry


def test_registry_initial_state() -> None:
    registry = VariablesRegistry()

    assert registry.variables == {}
    assert list(registry.variables) == []


def test_register_variable_uses_function_name_and_doc() -> None:
    registry = VariablesRegistry()

    def salary(_: object) -> float:
        """Return salary."""
        return 1000.0

    registry.register_variable(salary)
    formula = registry["salary"]

    assert "salary" in registry.variables
    assert registry.variables["salary"] is formula
    assert str(formula) == "salary"
    assert formula.__doc__ == "Return salary."
    assert formula(None) == 1000.0


def test_register_variable_sets_explicit_name_and_description() -> None:
    registry = VariablesRegistry()

    def hourly_rate(_: object) -> float:
        return 25.0

    registry.register_variable(hourly_rate, name="rate", description="Custom rate description")
    formula = registry["rate"]

    assert "rate" in registry.variables
    assert registry.variables["rate"] is formula
    assert str(formula) == "rate"
    assert formula.__doc__ == "Custom rate description"
    assert formula(None) == 25.0


def test_registry_variable_decorator_registers_formula() -> None:
    registry = VariablesRegistry()

    @registry.variable(name="days")
    def working_days(_: object) -> float:
        return 30.0

    assert "days" in registry.variables
    assert str(registry.variables["days"]) == "days"
    assert registry.variables["days"](None) == 30.0


def test_registry_variable_decorator_accepts_hidden_flag() -> None:
    registry = VariablesRegistry()

    @registry.variable(name="secret_salary", hidden=True)
    def secret_salary(_: object) -> float:
        return 999.0

    assert "secret_salary" in registry.variables
    assert registry.variables["secret_salary"](None) == 999.0

    with pytest.raises(FormulaNotRegisteredError):
        registry["secret_salary"]


def test_registry_getitem_returns_registered_formula() -> None:
    registry = VariablesRegistry()

    def salary(_: object) -> float:
        return 1500.0

    registry.register_variable(salary)
    formula = registry["salary"]

    assert registry["salary"] is formula
    assert formula(None) == 1500.0


def test_registry_getitem_raises_for_missing_name() -> None:
    registry = VariablesRegistry()

    with pytest.raises(FormulaNotRegisteredError, match="missing"):
        registry["missing"]


def test_registry_getitem_raises_for_hidden_name() -> None:
    registry = VariablesRegistry()

    def bonus(_: object) -> float:
        return 10.0

    registry.register_variable(bonus, name="bonus", hidden=True)

    with pytest.raises(FormulaNotRegisteredError, match="bonus"):
        registry["bonus"]

    assert "bonus" in registry.variables
    assert registry.variables["bonus"](None) == 10.0


def test_registry_rejects_duplicate_registration() -> None:
    registry = VariablesRegistry()

    def salary(_: object) -> float:
        return 100.0

    registry.register_variable(salary)

    assert registry["salary"](None) == 100.0

    with pytest.raises(FormulaAlreadyRegisteredError, match="salary"):
        registry.register_variable(salary)

    with pytest.raises(FormulaAlreadyRegisteredError, match="salary"):

        @registry.variable(name="salary")
        def another_salary(_: object) -> float: ...


def test_registry_variables_is_a_read_only_view() -> None:
    registry = VariablesRegistry()

    def salary(_: object) -> float:
        return 1000.0

    registry.register_variable(salary)

    with pytest.raises(TypeError):
        registry.variables["salary"] = Formula(lambda _: 0.0)  # type: ignore[index]

    with pytest.raises(TypeError):
        del registry.variables["salary"]  # type: ignore[attr-defined]


def test_registry_variables_view_reflects_later_registrations() -> None:
    registry = VariablesRegistry()
    view = registry.variables

    assert "salary" not in view

    def salary(_: object) -> float:
        return 1000.0

    registry.register_variable(salary)

    assert "salary" in view
    assert view["salary"](None) == 1000.0


def test_registry_allows_same_function_with_different_name() -> None:
    registry = VariablesRegistry()

    def salary(_: object) -> float:
        return 100.0

    registry.register_variable(salary, name="base_salary")
    registry.register_variable(salary, name="updated_salary")

    assert registry["base_salary"](None) == 100.0
    assert registry["updated_salary"](None) == 100.0
