# pyformula

**Arithmetic over your objects as small, typed, composable formulas.**

Name each quantity once (`salary`, `overtime_hours`, `tax_rate`) and write the calculation
with ordinary operators. You get a formula you can evaluate for any object, print,
store as JSON, edit in a form and describe with JSON Schema.

```py
net_pay = round((salary + overtime_hours * hourly_rate * 1.5) * (1 - tax_rate), 2)
```

## A first taste

A company pays a base salary, overtime at time-and-a-half, and withholds tax.

```python
from dataclasses import dataclass
from decimal import Decimal

from pyformula import VariablesRegistry


@dataclass
class Payslip:
    salary: Decimal
    overtime_hours: Decimal
    tax_rate: Decimal


pay = VariablesRegistry[Payslip]()


@pay.variable(label="Monthly salary")
def salary(slip: Payslip) -> Decimal:
    return slip.salary


@pay.variable(label="Overtime hours")
def overtime_hours(slip: Payslip) -> Decimal:
    return slip.overtime_hours


@pay.variable(label="Tax rate")
def tax_rate(slip: Payslip) -> Decimal:
    return slip.tax_rate


hourly_rate = salary / 160
gross = salary + overtime_hours * hourly_rate * Decimal("1.5")
net = round(gross * (1 - tax_rate), 2)

slip = Payslip(salary=Decimal("3200"), overtime_hours=Decimal("10"), tax_rate=Decimal("0.1"))

assert gross(slip) == Decimal("3500")
assert net(slip) == Decimal("3150.00")
```

Each decorated function became a **variable**: a `Formula` you combine with numbers and
other formulas. Nothing is computed until you call the result with an object.

### Read what it does

```python
assert str(net) == "round(((salary + ((overtime_hours * (salary / 160)) * 1.5)) * (1 - tax_rate)), 2)"
```

### Let HR edit the formula as JSON

```python
from pyformula import FormulaCompiler, decimal_literal

compiler = FormulaCompiler(pay.variables, literal=decimal_literal)

saved_in_database = {
    "round": {
        "operator": "multiply",
        "expressions": [
            {
                "operator": "add",
                "expressions": [
                    "salary",
                    {"operator": "multiply", "expressions": ["overtime_hours", {"operator": "divide", "expressions": ["salary", 160]}, 1.5]},
                ],
            },
            {"operator": "subtract", "expressions": [1, "tax_rate"]},
        ],
    },
    "ndigits": 2,
}

assert compiler.compile(saved_in_database)(slip) == Decimal("3150.00")
```

### Describe it to a formula editor

```python
from pyformula import get_formula_json_schema

schema = get_formula_json_schema(pay.variables, labels=pay.labels)

assert schema["x-kind"] == "formula"
assert schema["$defs"]["variable"]["oneOf"][0] == {"const": "salary", "x-label": "Monthly salary"}
```

## Where it fits

- **Payroll and compensation**: allowances, overtime, deductions, bonuses per contract.
- **Pricing**: discounts, taxes, shipping, margins, tiered fees.
- **Finance**: instalments, interest, ratios, scores.
- **KPIs and reports**: conversion rates, averages, growth, defined by analysts.
- **Engineering and science**: anything built from `sqrt`, `log`, trigonometry.
- **Formula editors**: let non-developers build calculations safely, without `eval`.

## Where to next

<div class="grid cards" markdown>

- [**Installation**](install.md): one command.
- [**User guide**](guide/index.md): every feature, one page each.
- [**Recipes**](recipes.md): complete real-world programs.
- [**Expression format**](reference/expressions.md): the JSON shapes, all functions.

</div>
