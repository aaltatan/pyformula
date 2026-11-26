# Formulas

A `Formula[T]` wraps a function `T -> number` and lets you do arithmetic with it before
there is anything to calculate:

```py
Formula(fn: Callable[[T], Number], *, name: str | None = None)
```

- `fn`: reads a number from the object under test. `Number` is `int | float | Decimal`.
- `name`: how the formula prints. Defaults to the function's name, or `anonymous` for a
  lambda.

Most of the time you get formulas from [variables](variables.md) rather than by calling
`Formula` yourself.

## Example: the total of an online order

```python
from dataclasses import dataclass
from decimal import Decimal

from pyformula import Formula


@dataclass(frozen=True)
class Order:
    unit_price: Decimal
    quantity: int
    discount_percent: Decimal
    shipping: Decimal
    vat_rate: Decimal


unit_price = Formula(lambda o: o.unit_price, name="unit_price")
quantity = Formula(lambda o: o.quantity, name="quantity")
discount_percent = Formula(lambda o: o.discount_percent, name="discount_percent")
shipping = Formula(lambda o: o.shipping, name="shipping")
vat_rate = Formula(lambda o: o.vat_rate, name="vat_rate")

subtotal = unit_price * quantity
discounted = subtotal * (1 - discount_percent / 100)
total = round((discounted + shipping) * (1 + vat_rate), 2)

order = Order(
    unit_price=Decimal("24.90"),
    quantity=3,
    discount_percent=Decimal("10"),
    shipping=Decimal("5.00"),
    vat_rate=Decimal("0.15"),
)

assert subtotal(order) == Decimal("74.70")
assert discounted(order) == Decimal("67.230")
assert total(order) == Decimal("83.06")
```

`subtotal`, `discounted` and `total` are formulas too: evaluate any of them, or build
further on them.

## Operators

Every arithmetic operator works between two formulas, or between a formula and a number
on either side:

| Python | Meaning | Prints as |
| --- | --- | --- |
| `a + b` | addition | `(a + b)` |
| `a - b` | subtraction | `(a - b)` |
| `a * b` | multiplication | `(a * b)` |
| `a / b` | true division | `(a / b)` |
| `a // b` | floor division | `(a // b)` |
| `a % b` | modulo | `(a % b)` |
| `a ** b` | power | `(a ** b)` |
| `-a`, `+a` | negation, identity | `-a`, `+a` |
| `abs(a)` | absolute value | `\|a\|` |
| `round(a, n)` | rounding, see [Numbers](numbers.md#rounding) | `round(a, n)` |

The usual Python precedence applies, and the printed form adds parentheses so the order
is never ambiguous:

```python
assert str(total) == (
    "round(((((unit_price * quantity) * (1 - (discount_percent / 100))) + shipping)"
    " * (1 + vat_rate)), 2)"
)
assert repr(-shipping + 3) == "Formula((-shipping + 3))"
assert str(100 - discount_percent) == "(100 - discount_percent)"
```

## Composition never changes the parts

Operators return new formulas. `subtotal` above is still `unit_price * quantity` after
`discounted` was built from it, so a shared building block can safely be reused:

```python
gift_wrap = Formula(lambda o: Decimal("2.50"), name="gift_wrap")

total_with_gift = round((discounted + shipping + gift_wrap) * (1 + vat_rate), 2)

assert total(order) == Decimal("83.06")
assert total_with_gift(order) == Decimal("85.94")
```

## Lazy evaluation

A formula does nothing until it is called. Accessors run on every call, so one formula
evaluates many objects:

```python
orders = [order, Order(Decimal("10"), 1, Decimal("0"), Decimal("0"), Decimal("0"))]

assert [total(o) for o in orders] == [Decimal("83.06"), Decimal("10.00")]
```

## Errors while evaluating

Arithmetic errors are Python's own and are raised when the formula is called:

```python
margin = Formula(lambda o: o["profit"], name="profit") / Formula(lambda o: o["revenue"], name="revenue")

try:
    margin({"profit": 10, "revenue": 0})
except ZeroDivisionError:
    pass
```

A result that would be a complex number (such as the square root of a negative number
through `** 0.5`) raises `TypeError` instead of silently returning a `complex`:

```python
side = Formula(lambda o: o["area"], name="area") ** 0.5

try:
    side({"area": -4})
except TypeError as error:
    assert "unsupported complex result" in str(error)
```

!!! tip "Guarding a division"
    Formulas have no `if`. To treat "revenue is zero" as a business case, choose the
    formula with a rule first; see [With pyspecification](pyspecification.md).
