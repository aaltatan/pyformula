from typing import Any

import pytest
from jsonschema import Draft202012Validator
from pyformula import FUNCTIONS, Formula, VariablesRegistry, get_formula_json_schema

AMOUNT = {"en": "Amount", "ar": "المبلغ"}


type Registry = VariablesRegistry[dict[str, float]]


@pytest.fixture
def registry() -> Registry:
    registry = VariablesRegistry[dict[str, float]]()

    @registry.variable(label=AMOUNT)
    def amount(row: dict[str, float]) -> float:
        """Return the line amount."""
        return row["amount"]

    @registry.variable()
    def days(row: dict[str, float]) -> float:
        return row["days"]

    @registry.variable(hidden=True, label="Secret")
    def secret(row: dict[str, float]) -> float:
        return row["secret"]

    return registry


@pytest.fixture
def validator(registry: Registry) -> Draft202012Validator:
    schema = get_formula_json_schema(registry.variables, labels=registry.labels)
    Draft202012Validator.check_schema(schema)

    return Draft202012Validator(schema)


class TestShape:
    def test_root_is_a_formula(self, registry: Registry):
        schema = get_formula_json_schema(registry.variables)

        assert schema["x-kind"] == "formula"
        assert schema["$ref"] == "#/$defs/formula"

    def test_variables_carry_labels_and_descriptions(self, registry: Registry):
        schema = get_formula_json_schema(registry.variables, labels=registry.labels)

        assert schema["$defs"]["variable"]["oneOf"] == [
            {"const": "amount", "x-label": AMOUNT, "description": "Return the line amount."},
            {"const": "days"},
        ]

    def test_registry_labels_leave_out_hidden_variables(self, registry: Registry):
        assert registry.labels == {"amount": AMOUNT}


class TestValidation:
    @pytest.mark.parametrize(
        "formula",
        [
            0.05,
            12,
            "amount",
            {"operator": "multiply", "expressions": ["amount", 0.05]},
            {"operator": "add", "expressions": [{"floor": "amount"}, {"sqrt": "days"}]},
            {"round": "amount", "ndigits": 2},
            {"negative": {"round": {"absolute": "days"}, "ndigits": 0}},
        ],
    )
    def test_accepts_what_the_compiler_accepts(self, validator: Draft202012Validator, formula: Any):
        assert list(validator.iter_errors(formula)) == []

    @pytest.mark.parametrize(
        "formula",
        [
            "secret",
            "unknown",
            True,
            None,
            {"operator": "concat", "expressions": ["amount"]},
            {"operator": "add", "expressions": []},
            {"round": "amount"},
            {"round": "amount", "ndigits": 1.5},
            {"floor": "amount", "ceil": "amount"},
            {"cube": "amount"},
        ],
    )
    def test_rejects_what_the_compiler_rejects(self, validator: Draft202012Validator, formula: Any):
        assert list(validator.iter_errors(formula)) != []


class TestChoosing:
    def test_only_the_chosen_operators_and_functions(self, registry: Registry):
        schema = get_formula_json_schema(registry.variables, operators=["add"], functions=["floor"])
        validator = Draft202012Validator(schema)

        assert validator.is_valid({"operator": "add", "expressions": [{"floor": 1.5}]})
        assert not validator.is_valid({"operator": "multiply", "expressions": [1]})
        assert not validator.is_valid({"round": 1.5, "ndigits": 0})
        assert not validator.is_valid({"ceil": 1.5})

    def test_no_operators_and_no_functions(self):
        schema = get_formula_json_schema({}, operators=[], functions=[])
        validator = Draft202012Validator(schema)

        assert validator.is_valid(3)
        assert not validator.is_valid("amount")
        assert not validator.is_valid({"operator": "add", "expressions": [1]})

    def test_every_function_by_default(self, registry: Registry):
        schema = get_formula_json_schema(registry.variables)
        names = {
            next(iter(node["required"]))
            for node in schema["$defs"]["formula"]["oneOf"]
            if "required" in node and "operator" not in node["required"]
        }

        assert names == set(FUNCTIONS)

    def test_unknown_operator_is_rejected(self):
        with pytest.raises(ValueError, match=r"Unknown operators: concat\. Available operators"):
            get_formula_json_schema({}, operators=["add", "concat"])

    def test_unknown_function_is_rejected(self):
        with pytest.raises(ValueError, match=r"Unknown functions: cube\. Available functions"):
            get_formula_json_schema({}, functions=["cube"])

    def test_label_for_an_unknown_variable_is_rejected(self):
        width = Formula[dict[str, float]](lambda row: row["width"], name="width")

        with pytest.raises(ValueError, match="Labels for unknown variables: height"):
            get_formula_json_schema({"width": width}, labels={"height": "Height"})


class TestExtraNodes:
    def test_extra_node_is_a_formula_too(self, registry: Registry):
        twice = {
            "type": "object",
            "properties": {"twice": {"$ref": "#"}},
            "required": ["twice"],
            "additionalProperties": False,
        }
        schema = get_formula_json_schema(registry.variables, nodes=[twice])
        validator = Draft202012Validator(schema)

        assert validator.is_valid({"operator": "add", "expressions": [{"twice": "amount"}, 1]})
        assert not validator.is_valid({"twice": "unknown"})
