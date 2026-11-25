"""The JSON Schema of a formula, as accepted by `FormulaCompiler.compile`.

Editors (rulify) build formulas from it: the variables to pick from with their
labels, the operators and the functions. Validators use the same schema.
"""

from collections.abc import Collection, Mapping, Sequence
from typing import Any

from pyvocabulary import JSON_SCHEMA_DIALECT, Text, labelled

from .compiler.compiler import WRAPPER_FNS
from .formula import Formula
from .operator import OPERATORS

FUNCTIONS: tuple[str, ...] = ("round", *WRAPPER_FNS)
"""Every function a formula may apply, e.g. `{"floor": ...}` or `{"round": ..., "ndigits": 2}`."""


def get_formula_json_schema(
    variables: Mapping[str, Formula[Any]],
    /,
    *,
    labels: Mapping[str, Text] | None = None,
    operators: Collection[str] | None = None,
    functions: Collection[str] | None = None,
    nodes: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Return the JSON Schema of a formula over `variables`.

    A formula is a number, a variable name, an operation
    (`{"operator": "add", "expressions": [...]}`) or a function of one formula.
    The root has `x-kind: "formula"`; each variable has its `x-label` when labelled.

    Args:
        variables: The variables a formula may name, e.g. `registry.variables`.
        labels: Labels by variable name, e.g. `registry.labels`.
        operators: The operators to offer. Defaults to all of them.
        functions: The functions to offer, from `FUNCTIONS`. Defaults to all of them.
        nodes: More shapes a formula may take, e.g. pyruleset's `when` node.
            Inside them, `{"$ref": "#"}` means "a formula".

    Raises:
        ValueError: For an unknown operator or function, or a label of an unknown variable.

    Example:
    ```python
    >>> amount = Formula(lambda row: row["amount"], name="amount")
    >>> schema = get_formula_json_schema(
    ...     {"amount": amount}, labels={"amount": {"en": "Amount", "ar": "المبلغ"}}
    ... )
    >>> schema["x-kind"], schema["$defs"]["variable"]
    ('formula', {'oneOf': [{'const': 'amount', 'x-label': {'en': 'Amount', 'ar': 'المبلغ'}}]})

    ```

    """
    operators = _checked(operators, list(OPERATORS), "operators")
    functions = _checked(functions, list(FUNCTIONS), "functions")
    labels = labels or {}

    if unknown := sorted(set(labels) - set(variables)):
        msg = f"Labels for unknown variables: {', '.join(unknown)}"
        raise ValueError(msg)

    formula: list[dict[str, Any]] = [{"type": "number"}]

    if variables:
        formula.append({"$ref": "#/$defs/variable"})

    if operators:
        formula.append(_operation(operators))

    formula.extend(_function(name) for name in functions)
    formula.extend(dict(node) for node in nodes)

    defs: dict[str, Any] = {"formula": {"oneOf": formula}}

    if variables:
        defs["variable"] = {
            "oneOf": [_variable(name, fn, labels.get(name)) for name, fn in variables.items()]
        }

    return {
        "$schema": JSON_SCHEMA_DIALECT,
        "x-kind": "formula",
        "$defs": defs,
        "$ref": "#/$defs/formula",
    }


# -----------------------
# helpers
# -----------------------


def _checked(chosen: Collection[str] | None, available: list[str], what: str) -> list[str]:
    if chosen is None:
        return available

    if unknown := [name for name in chosen if name not in available]:
        msg = f"Unknown {what}: {', '.join(unknown)}. Available {what}: {', '.join(available)}"
        raise ValueError(msg)

    return [name for name in available if name in chosen]


def _variable(name: str, fn: Formula[Any], label: Text | None) -> dict[str, Any]:
    schema = labelled({"const": name}, label=label)

    if fn.__doc__ and fn.__doc__ != Formula.__doc__:
        schema["description"] = fn.__doc__.strip()

    return schema


def _operation(operators: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "operator": {"enum": operators, "type": "string"},
            "expressions": {"type": "array", "items": {"$ref": "#"}, "minItems": 1},
        },
        "required": ["operator", "expressions"],
        "additionalProperties": False,
    }


def _function(name: str) -> dict[str, Any]:
    if name == "round":
        return {
            "type": "object",
            "properties": {"round": {"$ref": "#"}, "ndigits": {"type": "integer"}},
            "required": ["round", "ndigits"],
            "additionalProperties": False,
        }

    return {
        "type": "object",
        "properties": {name: {"$ref": "#"}},
        "required": [name],
        "additionalProperties": False,
    }
