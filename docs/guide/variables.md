# Variables and registries

A **variable** is a named formula that reads one quantity from your object: `salary`,
`children`, `distance_km`. Variables are the words your formulas are written with.

## `@variable()`

```py
variable(*, name: str | None = None) -> Callable[[Callable[[T], Number]], Formula[T]]
```

It turns an accessor function into a `Formula` named after the function (or `name`):

```python
from dataclasses import dataclass
from decimal import Decimal

from pyformula import variable


@dataclass
class Shipment:
    weight_kg: Decimal
    distance_km: Decimal
    fragile: bool


@variable()
def weight_kg(shipment: Shipment) -> Decimal:
    """Gross weight including packaging."""
    return shipment.weight_kg


@variable()
def distance_km(shipment: Shipment) -> Decimal:
    return shipment.distance_km


@variable(name="fragile_fee")
def _fragile_fee(shipment: Shipment) -> Decimal:
    return Decimal("4.00") if shipment.fragile else Decimal("0")


cost = Decimal("3.50") + weight_kg * Decimal("0.80") + distance_km * Decimal("0.05") + _fragile_fee

parcel = Shipment(weight_kg=Decimal("2.5"), distance_km=Decimal("120"), fragile=True)

assert cost(parcel) == Decimal("15.50")
assert str(cost) == "(((3.50 + (weight_kg * 0.80)) + (distance_km * 0.05)) + fragile_fee)"
```

The accessor is where data-dependent logic lives: `_fragile_fee` turns a flag into an
amount, so the formula itself stays pure arithmetic.

The function's metadata is kept, so IDEs, `help()` and the
[JSON Schema](json-schema.md) see its docstring:

```python
assert weight_kg.__doc__ == "Gross weight including packaging."
assert weight_kg.__name__ == "weight_kg"
```

## `VariablesRegistry`

When formulas are written **as data** (by HR, analysts, customers) they reference
variables by name. A registry is that vocabulary:

```py
VariablesRegistry[T]()
```

| Member | What it does |
| --- | --- |
| `registry.variable(*, name=None, description=None, hidden=False, label=None)` | decorator: register an accessor, return its formula |
| `registry.register_variable(fn, /, *, name=None, description=None, hidden=False, label=None)` | register an existing callable or formula, return its formula |
| `registry[name]` | the formula; `FormulaNotRegisteredError` if unknown or hidden |
| `registry.variables` | a read-only, live mapping of the visible variables, for the [compiler](compiling.md) |
| `registry.labels` | the labels of visible variables that have one, for the [schema](json-schema.md) |

### Example: payroll allowances

A payroll department pays several allowances on top of the base salary. Each variable is
registered once; formulas then combine them.

```python
from pyformula import VariablesRegistry


@dataclass
class Employee:
    name: str
    base_salary: Decimal
    children: int
    years_of_service: int
    lives_far: bool


payroll = VariablesRegistry[Employee]()


@payroll.variable(label={"en": "Base salary", "ar": "الراتب الأساسي"})
def base_salary(employee: Employee) -> Decimal:
    """The monthly base salary."""
    return employee.base_salary


@payroll.variable(label={"en": "Children", "ar": "عدد الأولاد"})
def children(employee: Employee) -> int:
    return employee.children


@payroll.variable(label={"en": "Years of service", "ar": "سنوات الخدمة"})
def years_of_service(employee: Employee) -> int:
    return employee.years_of_service


@payroll.variable(description="1 when the employee lives more than 30 km away, otherwise 0.")
def lives_far(employee: Employee) -> int:
    return int(employee.lives_far)


family_allowance = children * 25
seniority_bonus = base_salary * years_of_service * Decimal("0.01")
transport_allowance = lives_far * 40

gross = base_salary + family_allowance + seniority_bonus + transport_allowance

rana = Employee("Rana", Decimal("1800"), children=2, years_of_service=6, lives_far=True)

assert gross(rana) == Decimal("1998.00")
```

A boolean becomes a 0/1 multiplier (`lives_far * 40`): the usual way to switch a term on
or off inside arithmetic.

### Registering existing callables and derived formulas

`register_variable` registers something that already exists, including a **formula built
from other variables**. That is how you expose a derived quantity, such as gross salary,
to people who write formulas as JSON:

```python
payroll.register_variable(
    gross,
    name="gross_salary",
    description="Base salary plus every allowance.",
    label="Gross salary",
)

assert str(payroll["gross_salary"]) == "gross_salary"
assert payroll["gross_salary"](rana) == Decimal("1998.00")
```

A lambda has no usable name, so it must be given one:

```python
payroll.register_variable(lambda e: len(e.name), name="name_length", hidden=True)
```

### Names

Names end up in JSON, so they must be ASCII Python identifiers: a letter or underscore
first, then letters, digits and underscores. Anything else, including an unnamed lambda,
raises `InvalidFormulaNameError` (also a `ValueError`):

```python
from pyformula import FormulaAlreadyRegisteredError, FormulaNotRegisteredError, InvalidFormulaNameError

try:
    payroll.register_variable(lambda e: 1, name="net-salary")
except InvalidFormulaNameError as error:
    assert str(error).startswith("Invalid formula name: 'net-salary'")

try:
    payroll.register_variable(lambda e: 1)
except InvalidFormulaNameError:
    pass
```

A name can only be registered once, hidden or not:

```python
try:
    payroll.register_variable(lambda e: e.children, name="children")
except FormulaAlreadyRegisteredError as error:
    assert str(error) == "Formula already registered: children"
```

And looking up an unknown name fails clearly:

```python
try:
    payroll["salary"]
except FormulaNotRegisteredError as error:
    assert str(error) == "Formula not registered: salary"
```

### Hidden variables

A hidden variable is registered (its name is taken), but it is not in `variables`,
`labels` or the schema, and `registry[name]` does not find it. The formula returned by
the decorator still works in code.

Use it for quantities that are fine internally but must not be offered to the people
writing formulas, such as an employee's personal loan balance:

```python
@payroll.variable(hidden=True)
def loan_balance(employee: Employee) -> Decimal:
    return Decimal("900")


assert "loan_balance" not in payroll.variables

net_of_loan = gross - loan_balance / 12  # still usable from code

assert net_of_loan(rana) == Decimal("1923.00")
```

Because the compiler only sees `registry.variables`, a JSON formula can never reach a
hidden variable.

### `variables` is a live view

`registry.variables` reflects later registrations, so a compiler built early still sees
variables registered afterwards:

```python
view = payroll.variables


@payroll.variable()
def overtime_hours(employee: Employee) -> int:
    return 0


assert "overtime_hours" in view
assert list(view) == ["base_salary", "children", "years_of_service", "lives_far", "gross_salary", "overtime_hours"]
```
