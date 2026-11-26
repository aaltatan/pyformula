# JSON Schema

`get_formula_json_schema` describes, as [JSON Schema](https://json-schema.org/) draft
2020-12, the expressions a [compiler](compiling.md) accepts over your variables. Hand it
to:

- a **formula editor** in the browser, which builds its pickers from the schema,
- a **validator**, to reject bad payloads before compiling,
- an **LLM**, to turn "revenue minus costs, rounded to cents" into JSON,
- your **API docs**.

```py
get_formula_json_schema(
    variables: Mapping[str, Formula[Any]],
    /,
    *,
    labels: Mapping[str, Text] | None = None,
    operators: Collection[str] | None = None,
    functions: Collection[str] | None = None,
    nodes: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]
```

## Example: a KPI editor for a sales dashboard

Analysts define KPIs over monthly sales figures. Their editor is built from the schema.

```python
from pyformula import VariablesRegistry, get_formula_json_schema

kpis = VariablesRegistry[dict[str, float]]()


@kpis.variable(label={"en": "Revenue", "ar": "الإيرادات"})
def revenue(month: dict[str, float]) -> float:
    """Total invoiced in the month, before tax."""
    return month["revenue"]


@kpis.variable(label={"en": "Orders", "ar": "الطلبات"})
def orders(month: dict[str, float]) -> float:
    return month["orders"]


@kpis.variable(label={"en": "Visitors", "ar": "الزوار"})
def visitors(month: dict[str, float]) -> float:
    return month["visitors"]


schema = get_formula_json_schema(kpis.variables, labels=kpis.labels)
```

The root is a `$ref` to a `formula`, which is `oneOf` a number, a variable, an operation
and one shape per function. Nested expressions point back at the root with
`{"$ref": "#"}`:

```python
assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
assert schema["x-kind"] == "formula"
assert schema["$ref"] == "#/$defs/formula"

shapes = schema["$defs"]["formula"]["oneOf"]

assert shapes[0] == {"type": "number"}
assert shapes[1] == {"$ref": "#/$defs/variable"}
assert shapes[2]["properties"]["expressions"] == {"type": "array", "items": {"$ref": "#"}, "minItems": 1}
```

Each variable is a `const` with its label and its docstring (or `description=`):

```python
assert schema["$defs"]["variable"]["oneOf"][0] == {
    "const": "revenue",
    "x-label": {"en": "Revenue", "ar": "الإيرادات"},
    "description": "Total invoiced in the month, before tax.",
}
```

| Keyword | Where | From |
| --- | --- | --- |
| `x-kind: "formula"` | schema root | always; tells an editor what kind of expression this is |
| `x-label` | a variable | `label=` on `variable()` / `register_variable()`, via `labels=registry.labels` |
| `description` | a variable | `description=`, or the accessor's docstring |

JSON Schema ignores unknown `x-` keywords, so validators are unaffected by labels.

## Validating payloads

Any draft 2020-12 validator works. With
[`jsonschema`](https://pypi.org/project/jsonschema/):

```python
from jsonschema import Draft202012Validator

validator = Draft202012Validator(schema)

conversion_rate = {
    "round": {"operator": "multiply", "expressions": [{"operator": "divide", "expressions": ["orders", "visitors"]}, 100]},
    "ndigits": 2,
}
average_order = {"operator": "divide", "expressions": ["revenue", "orders"]}
typo = {"operator": "divide", "expressions": ["revenu", "orders"]}

assert validator.is_valid(conversion_rate)
assert validator.is_valid(average_order)
assert not validator.is_valid(typo)
```

Then compile what passed:

```python
from pyformula import FormulaCompiler

compiler = FormulaCompiler(kpis.variables)
november = {"revenue": 48_200.0, "orders": 964.0, "visitors": 31_100.0}

assert compiler.compile(conversion_rate)(november) == 3.1
assert compiler.compile(average_order)(november) == 50.0
```

## Choosing operators and functions

An editor for non-technical users should not offer `gamma` or `atanh`. `operators=` and
`functions=` narrow the schema:

```python
from pyformula import FUNCTIONS

simple = get_formula_json_schema(
    kpis.variables,
    labels=kpis.labels,
    operators=["add", "subtract", "multiply", "divide"],
    functions=["round", "absolute"],
)

simple_validator = Draft202012Validator(simple)

assert simple_validator.is_valid(conversion_rate)
assert not simple_validator.is_valid({"sqrt": "revenue"})
assert FUNCTIONS[:4] == ("round", "positive", "negative", "absolute")
```

`FUNCTIONS` lists every function name a formula may use. The order of the arguments you
pass does not matter; the schema keeps the library's order.

!!! warning "The schema narrows, the compiler does not"
    `operators=` and `functions=` only change the **schema**. `FormulaCompiler` still
    accepts every operator and function, so validate against the narrowed schema before
    compiling if you rely on it.

A name that does not exist is a `ValueError` that lists the valid ones:

```python
try:
    get_formula_json_schema(kpis.variables, operators=["plus"])
except ValueError as error:
    assert str(error).startswith("Unknown operators: plus. Available operators: add, subtract")

try:
    get_formula_json_schema(kpis.variables, labels={"profit": "Profit"})
except ValueError as error:
    assert str(error) == "Labels for unknown variables: profit"
```

## Extra node shapes

`nodes=` adds shapes a formula may take, for packages that extend the expression
language, such as pyruleset's `{"when": <ruleset>}`. Inside a node, `{"$ref": "#"}` means
"a formula":

```python
piecewise = {
    "type": "object",
    "properties": {"when": {"type": "array", "items": {"$ref": "#"}}},
    "required": ["when"],
    "additionalProperties": False,
}

extended = get_formula_json_schema(kpis.variables, nodes=[piecewise])

assert extended["$defs"]["formula"]["oneOf"][-1] == piecewise
```

The schema then accepts the node; compiling it is up to the package that defined it.

## Letting an LLM write formulas

The schema is a ready-made tool input schema. With the Anthropic SDK:

```py
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=[
        {
            "name": "define_kpi",
            "description": "Define a KPI as a formula over the monthly sales figures.",
            "input_schema": {"type": "object", "properties": {"formula": simple}, "required": ["formula"]},
        }
    ],
    tool_choice={"type": "tool", "name": "define_kpi"},
    messages=[{"role": "user", "content": "Revenue per visitor, rounded to cents"}],
)

kpi = compiler.compile(response.content[0].input["formula"])
```

Variable docstrings become schema descriptions, so a precise docstring is also a precise
prompt. Compile what the model returns inside a `try`.
