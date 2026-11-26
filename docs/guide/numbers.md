# Numbers, Decimal and rounding

A formula computes with whatever numbers your accessors return. `Number` is
`int | float | Decimal`, and the result follows Python's rules, with one improvement for
money (see below).

## Use `Decimal` for money

`float` is binary, so most decimal fractions are approximations:

```python
from decimal import Decimal

from pyformula import Formula

price = Formula(lambda item: item["price"], name="price")

assert (price * 3)({"price": 0.1}) == 0.30000000000000004  # float
assert (price * 3)({"price": Decimal("0.1")}) == Decimal("0.3")  # Decimal
```

Return `Decimal` from the accessors of money variables, and every `+ - * / // %` stays
exact. Integers mix freely with `Decimal`.

## Floats meeting Decimals

Python refuses `Decimal + float`. pyformula converts the `float` instead, **through its
shortest text form**: `0.1` becomes `Decimal("0.1")`, not the binary approximation
`Decimal(0.1) = 0.1000000000000000055…`:

```python
assert (price + 0.1)({"price": Decimal("1.10")}) == Decimal("1.20")
assert (price * 1.15)({"price": Decimal("200")}) == Decimal("230.00")
```

So a `Decimal` variable times a `float` constant written in code, or coming from JSON,
gives the exact result you expect.

## JSON literals and `decimal_literal`

Numbers in JSON arrive as `float`. When a whole formula is made of literals, or the data
is `int`, there is no `Decimal` to convert to, and float noise appears. Pass
`literal=decimal_literal` to the compiler to turn every literal into an exact `Decimal`:

```python
import json

from pyformula import FormulaCompiler, decimal_literal

fee = json.loads('{"operator": "add", "expressions": [0.1, 0.2]}')

assert FormulaCompiler({}).compile(fee)(None) == 0.30000000000000004
assert FormulaCompiler({}, literal=decimal_literal).compile(fee)(None) == Decimal("0.3")
```

`decimal_literal(number)` works on its own as well: `decimal_literal(0.8) == Decimal("0.8")`.
More in [Compiling](compiling.md#literals).

## Rounding

`round(formula, ndigits)` returns a rounding formula and keeps the number type:

| Input | `round(x)` | `round(x, 2)` |
| --- | --- | --- |
| `Decimal("2.675")` | `Decimal("3")` | `Decimal("2.68")` |
| `2.675` (float) | `3.0` | `2.67` (the float is really 2.67499…) |
| `7` (int) | `7` | `7` |

```python
total = Formula(lambda invoice: invoice["total"], name="total")

assert round(total, 2)({"total": Decimal("2.675")}) == Decimal("2.68")
assert round(total, 2)({"total": 2.675}) == 2.67
assert str(round(total, 2)) == "round(total, 2)"
```

### Rounding is half-to-even

Python's `round()` rounds halves to the **even** neighbour ("banker's rounding"), and so
does pyformula:

```python
assert round(total)({"total": Decimal("2.5")}) == 2
assert round(total)({"total": Decimal("3.5")}) == 4
```

That is the right default for statistics and many accounting systems, but invoices and
payslips often require **half-up**. Write a small helper that returns a formula:

```python
from decimal import ROUND_HALF_UP


def round_half_up(formula: Formula, places: int) -> Formula:
    step = Decimal(1).scaleb(-places)  # places=2 -> Decimal("0.01")

    return Formula(
        lambda obj: Decimal(formula(obj)).quantize(step, rounding=ROUND_HALF_UP),
        name=f"round_half_up({formula}, {places})",
    )


assert round_half_up(total, 0)({"total": Decimal("2.5")}) == Decimal("3")
assert round_half_up(total, 2)({"total": Decimal("10.125")}) == Decimal("10.13")
```

The same pattern adds any function pyformula does not have.

### Rounding to tens, hundreds, thousands

A negative `ndigits` rounds left of the decimal point, for example salaries rounded to the
nearest 100:

```python
salary = Formula(lambda e: e["salary"], name="salary")

assert round(salary, -2)({"salary": 123_456}) == 123_500
assert round(salary, -2)({"salary": Decimal("123456")}) == Decimal("1.235E+5")
```

`Decimal("1.235E+5")` **equals** `123500`; it is just written in scientific notation.
Format it with `f"{value:f}"` or `int(value)` for display.

## Mixing types: summary

| Left | Right | Result |
| --- | --- | --- |
| `int` | `int` | `int` (`/` gives `float`) |
| `int` | `float` | `float` |
| `int` | `Decimal` | `Decimal` |
| `float` | `float` | `float` |
| `float` | `Decimal` | `Decimal`, the float converted through `str` |
| `Decimal` | `Decimal` | `Decimal` |

[Math functions](math.md) other than rounding always return `float`.
