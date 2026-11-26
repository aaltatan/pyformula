# Recipes

Complete, runnable programs for common jobs. Each one is self-contained.

## Loan instalments

A bank shows the fixed monthly instalment of a loan (the annuity formula):

`instalment = P · r · (1 + r)ⁿ / ((1 + r)ⁿ − 1)`, with `r` the monthly rate and `n` the
number of months.

```python
from dataclasses import dataclass
from decimal import Decimal

from pyformula import VariablesRegistry


@dataclass
class Loan:
    principal: Decimal
    annual_rate: Decimal
    months: int


loans = VariablesRegistry[Loan]()


@loans.variable(label="Amount borrowed")
def principal(loan: Loan) -> Decimal:
    return loan.principal


@loans.variable(label="Yearly interest rate")
def annual_rate(loan: Loan) -> Decimal:
    return loan.annual_rate


@loans.variable(label="Duration in months")
def months(loan: Loan) -> int:
    return loan.months


monthly_rate = annual_rate / 12
growth = (1 + monthly_rate) ** months

instalment = round(principal * monthly_rate * growth / (growth - 1), 2)
total_paid = instalment * months
total_interest = total_paid - principal

car_loan = Loan(principal=Decimal("15000"), annual_rate=Decimal("0.09"), months=48)

assert instalment(car_loan) == Decimal("373.28")
assert total_interest(car_loan) == Decimal("2917.44")
```

`instalment` is defined once and reused by `total_paid` and `total_interest`.

## A tiered electricity bill

A utility charges by consumption tiers: the first 100 kWh at 0.05, the next 200 at 0.08,
everything above at 0.15, plus a fixed fee. Formulas have no `min`/`max`, so the
**accessors** split consumption into tiers and the formula stays a readable sum:

```python
@dataclass
class Meter:
    kwh: Decimal


bill = VariablesRegistry[Meter]()


def _in_tier(kwh: Decimal, start: int, end: int | None) -> Decimal:
    upper = kwh if end is None else min(kwh, Decimal(end))

    return max(Decimal(0), upper - start)


@bill.variable(label="kWh in tier 1 (0-100)")
def tier_1(meter: Meter) -> Decimal:
    return _in_tier(meter.kwh, 0, 100)


@bill.variable(label="kWh in tier 2 (100-300)")
def tier_2(meter: Meter) -> Decimal:
    return _in_tier(meter.kwh, 100, 300)


@bill.variable(label="kWh in tier 3 (300+)")
def tier_3(meter: Meter) -> Decimal:
    return _in_tier(meter.kwh, 300, None)


FIXED_FEE = Decimal("3.00")

amount_due = round(FIXED_FEE + tier_1 * Decimal("0.05") + tier_2 * Decimal("0.08") + tier_3 * Decimal("0.15"), 2)

assert amount_due(Meter(Decimal("80"))) == Decimal("7.00")
assert amount_due(Meter(Decimal("250"))) == Decimal("20.00")
assert amount_due(Meter(Decimal("420"))) == Decimal("42.00")
```

When the tiers change, only the accessor boundaries or the prices change, and the
regulator-facing formula stays easy to audit.

## Invoice lines with half-up rounding

Tax authorities often require each invoice line rounded **half-up** to cents. Python's
`round()` rounds half-to-even, so add a half-up formula (see
[Numbers](guide/numbers.md#rounding-is-half-to-even)):

```python
from decimal import ROUND_HALF_UP

from pyformula import Formula


def round_half_up(formula: Formula, places: int = 2) -> Formula:
    step = Decimal(1).scaleb(-places)

    return Formula(
        lambda obj: Decimal(formula(obj)).quantize(step, rounding=ROUND_HALF_UP),
        name=f"round_half_up({formula}, {places})",
    )


line_price = Formula(lambda line: line["price"], name="price")
line_quantity = Formula(lambda line: line["quantity"], name="quantity")

net = round_half_up(line_price * line_quantity)
vat = round_half_up(net * Decimal("0.15"))
gross = net + vat

invoice = [
    {"item": "Notebook", "price": Decimal("2.35"), "quantity": 3},
    {"item": "Pen", "price": Decimal("0.45"), "quantity": 10},
    {"item": "Stapler", "price": Decimal("6.90"), "quantity": 1},
]

lines = [(line["item"], net(line), vat(line), gross(line)) for line in invoice]

assert lines == [
    ("Notebook", Decimal("7.05"), Decimal("1.06"), Decimal("8.11")),
    ("Pen", Decimal("4.50"), Decimal("0.68"), Decimal("5.18")),
    ("Stapler", Decimal("6.90"), Decimal("1.04"), Decimal("7.94")),
]
assert sum(row[3] for row in lines) == Decimal("21.23")
```

The difference shows on exact halves: a VAT of `0.125` becomes `0.12` with `round()` but
`0.13` with `round_half_up`:

```python
half = Formula(lambda _: Decimal("0.125"), name="half")

assert round(half, 2)(None) == Decimal("0.12")
assert round_half_up(half)(None) == Decimal("0.13")
```

## Computed columns for a report

An analytics team defines computed columns over raw rows (like spreadsheet formulas).
Derived columns are registered as variables so later formulas, and JSON, can use them:

```python
import csv
import io

from pyformula import FormulaCompiler

ROWS = """\
store,revenue,cost,visitors,orders
Damascus,52000,31000,18000,1100
Aleppo,38000,26500,15500,700
Latakia,21000,12000,6200,420
"""

report = VariablesRegistry[dict[str, str]]()

for column in ("revenue", "cost", "visitors", "orders"):
    report.register_variable(lambda row, column=column: Decimal(row[column]), name=column)

profit = report.register_variable(report["revenue"] - report["cost"], name="profit")
report.register_variable(round(profit / report["revenue"] * 100, 1), name="margin_percent")
report.register_variable(round(report["orders"] / report["visitors"] * 100, 2), name="conversion_percent")

# an analyst adds a column without touching code
compiler = FormulaCompiler(report.variables)
report.register_variable(
    compiler.compile({"round": {"operator": "divide", "expressions": ["profit", "orders"]}, "ndigits": 2}),
    name="profit_per_order",
)

columns = ["profit", "margin_percent", "conversion_percent", "profit_per_order"]
table = [
    [row["store"], *(report[name](row) for name in columns)]
    for row in csv.DictReader(io.StringIO(ROWS))
]

assert table == [
    ["Damascus", Decimal("21000"), Decimal("40.4"), Decimal("6.11"), Decimal("19.09")],
    ["Aleppo", Decimal("11500"), Decimal("30.3"), Decimal("4.52"), Decimal("16.43")],
    ["Latakia", Decimal("9000"), Decimal("42.9"), Decimal("6.77"), Decimal("21.43")],
]
```

Note `column=column` in the lambda: it captures the current loop value, a classic Python
pitfall when registering accessors in a loop.

## A formula editor endpoint

A web form lets users write a formula, preview it on sample data and save it. Errors
must come back with the path of the bad part so the form can highlight it.

```python
from jsonschema import Draft202012Validator

from pyformula import PyformulaError, get_formula_json_schema

products = VariablesRegistry[dict[str, Decimal]]()

for field in ("cost", "list_price", "weight_kg"):
    products.register_variable(lambda p, field=field: p[field], name=field)

schema = get_formula_json_schema(
    products.variables,
    operators=["add", "subtract", "multiply", "divide"],
    functions=["round", "ceil"],
)
validator = Draft202012Validator(schema)
product_compiler = FormulaCompiler(products.variables)

SAMPLE = {"cost": Decimal("12.00"), "list_price": Decimal("19.90"), "weight_kg": Decimal("0.4")}


def preview(expression: object) -> dict[str, object]:
    if errors := [error.message for error in validator.iter_errors(expression)]:
        return {"ok": False, "errors": errors[:1]}

    try:
        formula = product_compiler.compile(expression)
    except PyformulaError as error:
        return {"ok": False, "errors": [str(error)], "at": getattr(error, "__notes__", [])}

    return {"ok": True, "formula": str(formula), "sample": str(formula(SAMPLE))}


margin = {"round": {"operator": "subtract", "expressions": ["list_price", "cost"]}, "ndigits": 2}

assert preview(margin) == {"ok": True, "formula": "round((list_price - cost), 2)", "sample": "7.90"}
assert preview({"sqrt": "cost"})["ok"] is False  # not offered by this editor
assert preview({"operator": "add", "expressions": ["cost", "shipping"]})["ok"] is False
```

The schema rejects anything outside the editor's vocabulary, including unknown variable
names; the compiler is the final check and gives the JSON path.
