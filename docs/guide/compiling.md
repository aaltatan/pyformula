# Compiling formulas from JSON

Formulas written in code are for developers. When a formula is **data** (a commission
plan an admin edits, a KPI an analyst defines, a fee a customer configures) you describe
it as JSON and compile it. There is no `eval` and no string parsing: the JSON can only
name your variables, numbers, operators and functions.

```py
FormulaCompiler(variables: Mapping[str, Formula[T]], /, *, literal: LiteralFn | None = None)
compiler.compile(expression) -> Formula[T]
```

- `variables`: the names an expression may use, usually `registry.variables`.
- `literal`: converts every number in the expression, see [Literals](#literals).

## The JSON shapes

An expression is one of five shapes, nested as deep as you like.
The [expression format reference](../reference/expressions.md) lists them all with every
function.

| Shape | Example | Means |
| --- | --- | --- |
| number | `0.15` | the constant |
| variable name | `"salary"` | `registry["salary"]` |
| operation | `{"operator": "add", "expressions": ["salary", "bonus", 100]}` | `salary + bonus + 100` |
| function | `{"sqrt": "area"}` | `sqrt(area)` |
| round | `{"round": "total", "ndigits": 2}` | `round(total, 2)` |

Operators are `add`, `subtract`, `multiply`, `divide`, `floor_divide`, `modulo` and
`power`. An operation takes **one or more** expressions and folds them from the left:
`{"operator": "subtract", "expressions": [100, "a", "b"]}` is `(100 - a) - b`.

!!! note "Power folds from the left too"
    `{"operator": "power", "expressions": [2, 3, 2]}` is `(2 ** 3) ** 2 = 64`, unlike
    Python's `2 ** 3 ** 2 = 512`. Nest two operations to get the other grouping.

## Example: sales commission plans

A company pays each sales team by its own plan. The plans live in a database table as
JSON, and payroll compiles them every month.

```python
import json
import sqlite3
from dataclasses import dataclass
from decimal import Decimal

from pyformula import FormulaCompiler, VariablesRegistry, decimal_literal


@dataclass
class SalesMonth:
    revenue: Decimal
    target: Decimal
    new_clients: int
    base_salary: Decimal


sales = VariablesRegistry[SalesMonth]()


@sales.variable(label="Revenue")
def revenue(month: SalesMonth) -> Decimal:
    return month.revenue


@sales.variable(label="Target")
def target(month: SalesMonth) -> Decimal:
    return month.target


@sales.variable(label="New clients")
def new_clients(month: SalesMonth) -> int:
    return month.new_clients


@sales.variable(label="Base salary")
def base_salary(month: SalesMonth) -> Decimal:
    return month.base_salary


compiler = FormulaCompiler(sales.variables, literal=decimal_literal)

database = sqlite3.connect(":memory:")
database.execute("CREATE TABLE commission_plan (team TEXT PRIMARY KEY, formula TEXT)")
database.executemany(
    "INSERT INTO commission_plan VALUES (?, ?)",
    [
        # 5% of revenue plus 50 per new client
        (
            "field",
            json.dumps(
                {
                    "operator": "add",
                    "expressions": [
                        {"operator": "multiply", "expressions": ["revenue", 0.05]},
                        {"operator": "multiply", "expressions": ["new_clients", 50]},
                    ],
                }
            ),
        ),
        # 20% of base salary per started 10% of target reached, rounded to whole units
        (
            "key_accounts",
            json.dumps(
                {
                    "round": {
                        "operator": "multiply",
                        "expressions": [
                            "base_salary",
                            0.2,
                            {"ceil": {"operator": "multiply", "expressions": [{"operator": "divide", "expressions": ["revenue", "target"]}, 10]}},
                        ],
                    },
                    "ndigits": 0,
                }
            ),
        ),
    ],
)

plans = {
    team: compiler.compile(json.loads(formula))
    for team, formula in database.execute("SELECT team, formula FROM commission_plan")
}

month = SalesMonth(revenue=Decimal("42000"), target=Decimal("50000"), new_clients=3, base_salary=Decimal("1500"))

assert plans["field"](month) == Decimal("2250.00")
assert plans["key_accounts"](month) == Decimal("2700")
assert str(plans["field"]) == "((revenue * 0.05) + (new_clients * 50))"
```

The compiled plans are ordinary formulas: combine them with code-defined formulas,
print them in an audit log, evaluate them for every employee.

## Literals

Every number in an expression becomes a formula named after its value, so printed
formulas read naturally (`(revenue * 0.05)`).

JSON numbers arrive as `float`. With `literal=decimal_literal` they are converted to
exact `Decimal`s through their text form, which is what you want for money. `literal`
accepts any one-argument function, for example to reject numbers outside a range:

```python
from pyformula import InvalidExpressionError


def bounded(number: float) -> Decimal:
    if abs(number) > 1_000_000:
        raise InvalidExpressionError(number)

    return decimal_literal(number)


strict = FormulaCompiler(sales.variables, literal=bounded)

try:
    strict.compile({"operator": "multiply", "expressions": ["revenue", 1e9]})
except InvalidExpressionError as error:
    assert error.__notes__ == ["at $.expressions[1]"]
```

## Errors point at the bad part

The compiler checks the whole expression while compiling, before any object is
evaluated. Errors are subclasses of `PyformulaError`, and each one gets an exception
**note with the JSON path** of the offending part:

```python
from pyformula import FormulaNotFoundError

try:
    compiler.compile({"operator": "add", "expressions": ["revenue", {"sqrt": "profit"}]})
except FormulaNotFoundError as error:
    assert str(error) == "Formula not found: profit. Available formulas: revenue, target, new_clients, base_salary"
    assert error.__notes__ == ["at $.expressions[1].sqrt"]
```

`InvalidExpressionError` is raised for anything that is not one of the five shapes:

| Mistake | Example |
| --- | --- |
| unknown operator | `{"operator": "plus", "expressions": [1, 2]}` |
| empty operation | `{"operator": "add", "expressions": []}` |
| extra or missing keys | `{"sqrt": "a", "cbrt": "a"}`, `{"round": "a"}` |
| `ndigits` not an integer | `{"round": "a", "ndigits": 1.5}` |
| a boolean where a number is expected | `true` |
| a list, `null` or other JSON value | `[1, 2]` |

```python
for bad in [
    {"operator": "plus", "expressions": [1, 2]},
    {"operator": "add", "expressions": []},
    {"sqrt": "revenue", "cbrt": "revenue"},
    {"round": "revenue", "ndigits": 1.5},
    True,
    [1, 2],
]:
    try:
        compiler.compile(bad)
    except InvalidExpressionError as error:
        assert str(error) == f"Invalid expression: {bad}"
```

Python prints notes under the traceback, so paths show up in logs. To send them to a
form, read `error.__notes__`.

!!! tip "Validate, then compile once"
    Validate incoming JSON against the [JSON Schema](json-schema.md), then compile it
    **before saving**: the schema catches shapes, compiling also catches unknown
    variables. Compile stored formulas once at start-up, not per object.

## Security

A compiler can only reach the variables in the mapping you give it. Variables registered
with `hidden=True` are not in `registry.variables`, so user-written JSON cannot read them.
The JSON never contains code.

Evaluating still runs real arithmetic, so a hostile formula can ask for
`{"operator": "power", "expressions": [10, 1000000]}`. If users you do not trust write
formulas, bound the literals (as above) and limit the operators and functions offered by
the [schema](json-schema.md#choosing-operators-and-functions).
