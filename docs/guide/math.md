# Math functions

`pyformula.math` holds formula versions of Python's [`math`](https://docs.python.org/3/library/math.html)
functions. Each takes a formula and returns a new formula:

```py
from pyformula import math as fm

fm.sqrt(width ** 2 + height ** 2)
```

| Group | Functions |
| --- | --- |
| Rounding | `ceil`, `floor`, `trunc` (and the built-in `round()`, see [Numbers](numbers.md#rounding)) |
| Roots | `sqrt`, `cbrt` |
| Exponential and logarithmic | `exp`, `exp2`, `expm1`, `log10`, `log1p`, `log2` |
| Trigonometry | `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` |
| Angular conversion | `degrees`, `radians` |
| Special | `erf`, `erfc`, `gamma`, `lgamma` |
| Floating point | `fabs`, `ulp` |

The built-in `abs()` and unary `-`/`+` work on formulas directly.

Importing the module as `fm` (or importing single functions) keeps it apart from the
standard `math` module.

## Example: how many boxes to ship

A warehouse packs 12 bottles per box and charges per started box:

```python
from pyformula import Formula
from pyformula import math as fm

bottles = Formula(lambda order: order["bottles"], name="bottles")

boxes = fm.ceil(bottles / 12)
packing_fee = boxes * 1.75

assert boxes({"bottles": 30}) == 3
assert packing_fee({"bottles": 30}) == 5.25
assert str(boxes) == "ceil((bottles / 12))"
```

## Example: delivery distance between two points

A delivery app prices trips by great-circle distance (the haversine formula), using the
latitude and longitude of pick-up and drop-off:

```python
from dataclasses import dataclass

from pyformula import variable


@dataclass
class Trip:
    from_lat: float
    from_lon: float
    to_lat: float
    to_lon: float


@variable()
def from_lat(trip: Trip) -> float:
    return trip.from_lat


@variable()
def from_lon(trip: Trip) -> float:
    return trip.from_lon


@variable()
def to_lat(trip: Trip) -> float:
    return trip.to_lat


@variable()
def to_lon(trip: Trip) -> float:
    return trip.to_lon


EARTH_RADIUS_KM = 6371

d_lat = fm.radians(to_lat - from_lat)
d_lon = fm.radians(to_lon - from_lon)

a = fm.sin(d_lat / 2) ** 2 + fm.cos(fm.radians(from_lat)) * fm.cos(fm.radians(to_lat)) * fm.sin(d_lon / 2) ** 2
distance_km = 2 * EARTH_RADIUS_KM * fm.asin(fm.sqrt(a))

fare = round(2.0 + distance_km * 0.9, 2)

damascus_to_homs = Trip(33.5138, 36.2765, 34.7324, 36.7137)

assert round(distance_km(damascus_to_homs)) == 141
assert fare(damascus_to_homs) == 129.22
```

## Example: a credit score with diminishing returns

Logarithms flatten large values, so the 50th on-time payment counts less than the 5th:

```python
on_time = Formula(lambda c: c["on_time_payments"], name="on_time_payments")
late = Formula(lambda c: c["late_payments"], name="late_payments")

score = round(300 + 120 * fm.log10(on_time + 1) - 45 * late, 0)

assert score({"on_time_payments": 9, "late_payments": 0}) == 420.0
assert score({"on_time_payments": 99, "late_payments": 1}) == 495.0
```

There is no natural-log function; `log1p(x - 1)` is `ln(x)`.

## What the functions return

The functions convert their input to `float` before calling `math`, like `math` itself
does:

- `ceil`, `floor` and `trunc` return an `int`.
- Every other function returns a `float`, even for `Decimal` input.

```python
from decimal import Decimal

amount = Formula(lambda o: o["amount"], name="amount")

assert fm.floor(amount)({"amount": Decimal("7.9")}) == 7
assert fm.sqrt(amount)({"amount": Decimal("16")}) == 4.0
assert isinstance(fm.sqrt(amount)({"amount": Decimal("16")}), float)
```

!!! warning "Money and math functions"
    Because they go through `float`, math functions are not exact for money. Keep money
    arithmetic in `+ - * /` and `round()`, which stay in `Decimal`; see
    [Numbers, Decimal and rounding](numbers.md).

## Domain errors

Out-of-domain input raises `math`'s own `ValueError` when the formula runs:

```python
try:
    fm.sqrt(amount)({"amount": -1})
except ValueError as error:
    assert str(error) == "math domain error"
```
