import pytest
from pyformula import Formula, FormulaCompiler
from pyformula.exceptions import FormulaNotFoundError, InvalidExpressionError

type Compiler = FormulaCompiler[dict[str, float]]


@pytest.fixture
def compiler() -> Compiler:
    price = Formula[dict[str, float]](lambda order: order["price"], name="price")
    return FormulaCompiler({"price": price})


class TestPathNotes:
    def test_error_in_an_operand_points_at_it(self, compiler: Compiler) -> None:
        with pytest.raises(FormulaNotFoundError) as info:
            compiler.compile({"operator": "add", "expressions": ["price", "pricee"]})

        assert info.value.__notes__ == ["at $.expressions[1]"]

    def test_nested_operands_report_the_full_path(self, compiler: Compiler) -> None:
        expression = {
            "operator": "multiply",
            "expressions": [
                "price",
                {"operator": "add", "expressions": [1, {"sqrt": "taxx"}]},
            ],
        }

        with pytest.raises(FormulaNotFoundError) as info:
            compiler.compile(expression)

        assert info.value.__notes__ == ["at $.expressions[1].expressions[1].sqrt"]

    def test_round_operand_is_located(self, compiler: Compiler) -> None:
        with pytest.raises(InvalidExpressionError) as info:
            compiler.compile({"round": {"operator": "nope", "expressions": [1]}, "ndigits": 2})

        assert info.value.__notes__ == ["at $.round"]

    def test_error_at_the_root_has_no_note(self, compiler: Compiler) -> None:
        with pytest.raises(FormulaNotFoundError) as info:
            compiler.compile("pricee")

        assert not getattr(info.value, "__notes__", [])

    def test_message_and_type_are_unchanged(self, compiler: Compiler) -> None:
        with pytest.raises(FormulaNotFoundError) as info:
            compiler.compile({"operator": "add", "expressions": ["price", "pricee"]})

        # `pytest.raises(match=)` also searches notes, so compare the message itself
        assert str(info.value) == "Formula not found: pricee. Available formulas: price"
