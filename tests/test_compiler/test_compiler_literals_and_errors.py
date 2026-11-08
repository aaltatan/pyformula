import json
from decimal import Decimal
from typing import Any

import pytest
from pyformula import (
    Formula,
    FormulaAlreadyRegisteredError,
    FormulaCompiler,
    FormulaNotFoundError,
    FormulaNotRegisteredError,
    InvalidExpressionError,
    Number,
    PyformulaError,
    decimal_literal,
)

price = Formula[dict[str, Any]](lambda order: order["price"], name="price")
quantity = Formula[dict[str, Any]](lambda order: order["quantity"], name="quantity")


class TestBaseError:
    @pytest.mark.parametrize(
        "error",
        [
            FormulaAlreadyRegisteredError("x"),
            FormulaNotRegisteredError("x"),
            FormulaNotFoundError("x"),
            InvalidExpressionError("x"),
        ],
    )
    def test_every_error_is_a_pyformula_error(self, error: Exception) -> None:
        assert isinstance(error, PyformulaError)

    def test_compiler_errors_can_be_caught_together(self):
        with pytest.raises(PyformulaError):
            FormulaCompiler({"price": price}).compile({"operator": "nope", "expressions": [1]})


class TestFormulaNotFound:
    def test_message_lists_available_formulas(self):
        compiler = FormulaCompiler({"price": price, "quantity": quantity})

        with pytest.raises(
            FormulaNotFoundError,
            match=r"^Formula not found: pricee\. Available formulas: price, quantity$",
        ):
            compiler.compile("pricee")

    def test_message_for_an_empty_compiler(self):
        with pytest.raises(FormulaNotFoundError, match=r"Available formulas: \(none\)$"):
            FormulaCompiler[Any]({}).compile("price")

    def test_message_without_available_names_is_unchanged(self):
        assert str(FormulaNotFoundError("price")) == "Formula not found: price"


class TestLiteralNames:
    def test_compiled_literal_shows_its_value_in_repr(self):
        formula = FormulaCompiler({"price": price}).compile(
            {"operator": "multiply", "expressions": ["price", 0.8]}
        )
        assert repr(formula) == "Formula((price * 0.8))"

    def test_compiled_literal_repr_matches_python_composition(self):
        compiled = FormulaCompiler({"price": price}).compile(
            {"operator": "add", "expressions": ["price", 2]}
        )
        assert repr(compiled) == repr(price + 2)

    def test_bare_literal(self):
        formula = FormulaCompiler[Any]({}).compile(Decimal("1.5"))
        assert repr(formula) == "Formula(1.5)"
        assert formula({}) == Decimal("1.5")


class TestLiteralHook:
    def test_default_keeps_literals_as_they_are(self):
        formula = FormulaCompiler[Any]({}).compile(0.8)
        assert type(formula({})) is float

    def test_float_literal_leaks_into_decimal_money_without_the_hook(self):
        leaky = FormulaCompiler({"price": price}).compile(
            {"operator": "multiply", "expressions": ["price", 0.8]}
        )
        assert leaky({"price": Decimal("120.00")}) != Decimal("96.000")

    def test_decimal_literal_keeps_money_exact(self):
        exact = FormulaCompiler({"price": price}, literal=decimal_literal).compile(
            json.loads('{"operator": "multiply", "expressions": ["price", 0.8]}')
        )
        assert exact({"price": Decimal("120.00")}) == Decimal("96.000")
        assert repr(exact) == "Formula((price * 0.8))"

    def test_hook_applies_to_nested_literals(self):
        seen: list[Any] = []

        def recording(number: Any) -> Any:
            seen.append(number)
            return number

        FormulaCompiler({"price": price}, literal=recording).compile(
            {
                "operator": "add",
                "expressions": [
                    {
                        "round": {
                            "operator": "multiply",
                            "expressions": ["price", 1.1],
                        },
                        "ndigits": 2,
                    },
                    3,
                ],
            }
        )
        assert seen == [1.1, 3]

    def test_hook_does_not_touch_ndigits(self):
        calls: list[Any] = []
        compiler = FormulaCompiler({"price": price}, literal=lambda n: calls.append(n) or n)
        compiler.compile({"round": "price", "ndigits": 2})
        assert calls == []

    def test_literal_is_keyword_only(self):
        with pytest.raises(TypeError):
            FormulaCompiler({"price": price}, decimal_literal)  # type: ignore[misc]


class TestDecimalLiteral:
    @pytest.mark.parametrize(
        ("number", "expected"),
        [
            (0.8, Decimal("0.8")),
            (2, Decimal(2)),
            (Decimal("1.10"), Decimal("1.10")),
            (1e-7, Decimal("1E-7")),
        ],
    )
    def test_converts_through_str(self, number: Number, expected: Decimal) -> None:
        assert decimal_literal(number) == expected
        assert str(decimal_literal(number)) == str(expected)
