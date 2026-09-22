# pyformula

A lightweight, typed Python library for composing business rules as reusable, executable numeric formulas.

`pyformula` focuses on a functional style where:

- formulas are first-class callable objects
- calculations compose naturally with arithmetic operators
- formulas are built from typed model accessors and reusable variables
- registry-based declaration keeps formulas organized and discoverable
- structured formula definitions can be compiled from dictionaries or JSON-like payloads
- structured formula definitions make calculations portable, inspectable, and machine-readable

It is especially useful for:

- pricing and discount engines
- payroll and compensation logic
- scoring and risk calculations
- declarative business rules
- dynamic feature or KPI computation
- policy systems where rules are selected by context and evaluated against domain objects

The package is designed for clarity and portability: formula definitions are not locked inside one-off Python functions, but can be described as data and evaluated consistently.

---

## Features

- `Formula[T]` objects behave like lazily evaluated numeric functions
- arithmetic composition with `+`, `-`, `*`, `/`, `%`, `**`, `//`
- math wrappers such as `sqrt`, `sin`, `log10`, `round`, `exp`, `gamma`, and more
- `variable()` decorator for turning accessors into reusable named formulas
- `VariablesRegistry` for naming and organizing formulas
- `FormulaCompiler` for compiling nested dictionary expressions into executable formulas
- recursive expression trees for declarative rule and calculation definition
- strict validation for malformed or missing expressions

---

## Why this package exists

Most formula libraries are either:

- low-level numeric math libraries, or
- expression evaluators that work with strings

pyformula tries a middle ground:

- formulas are Python objects
- formulas are evaluated against real domain objects
- formulas are composable and inspectable
- expressions can be defined as dictionaries and compiled at runtime

That means you can keep your calculation logic structured, reusable, and easy to debug.

This is valuable when formulas are part of a business process rather than just a single one-off calculation.

---

## Install

From a PyPI:

```bash
pip install pyformula
```

or using uv:

```bash
uv add pyformula
```

The project declares Python 3.12+ in `pyproject.toml`.

---

## Quick start

### 1) Define a model and formulas

```python
from dataclasses import dataclass

from pyformula import Formula


@dataclass
class Rectangle:
    width: float
    height: float


width = Formula[Rectangle](lambda rect: rect.width)
height = Formula[Rectangle](lambda rect: rect.height)

perimeter = (width + height) * 2
area = width * height

rect = Rectangle(10, 20)
print(perimeter(rect))  # 60.0
print(area(rect))      # 200.0
```

### 2) Use the `variable` decorator

```python
from dataclasses import dataclass

from pyformula import variable


@dataclass
class Employee:
    salary: float
    hourly_rate: float


@variable()
def salary(employee: Employee) -> float:
    return employee.salary


@variable()
def hourly_rate(employee: Employee) -> float:
    return employee.hourly_rate


bonus = salary * 0.25
weekly_cost = (salary / 40) * hourly_rate

employee = Employee(5000, 25)
print(bonus(employee))     # 1250.0
print(weekly_cost(employee))
```

### 3) Compile a formula tree from a dictionary

```python
from pyformula import FormulaCompiler

compiler = FormulaCompiler({
    "base_salary": Formula(lambda employee: employee["salary"]),
    "bonus": Formula(lambda employee: employee["bonus"]),
})

expression = {
    "operator": "add",
    "expressions": [
        "base_salary",
        {"operator": "multiply", "expressions": ["bonus", 0.15]},
    ],
}

formula = compiler.compile(expression)
print(formula({"salary": 1000, "bonus": 200}))
```

---

## Core concepts

### Formula

`Formula[T]` wraps a callable that takes an instance of `T` and returns a numeric result.

Allowed numeric results are `int`, `float`, and `Decimal`.

```python
from pyformula import Formula

f = Formula[dict](lambda item: item["value"])
print(f({"value": 3}))  # 3
```

You can build formulas with arithmetic operations:

```python
base = Formula[dict](lambda item: item["base"])
multiplier = Formula[dict](lambda item: item["multiplier"])

final_formula = (base * multiplier) + 5
```

The library overloads the normal arithmetic operators, so formula composition is natural and expressive.

### variable

`variable()` is a decorator that converts a function into a named `Formula` while preserving the original function metadata.

```python
from pyformula import variable

@variable(name="days_in_month")
def days_in_month(_: object) -> float:
    return 30
```

This is useful for turning ordinary model accessors into named formula building blocks.

### VariablesRegistry

A `VariablesRegistry` stores named formulas keyed by string names.

```python
from pyformula.registry import VariablesRegistry

registry = VariablesRegistry()


def salary(_: object) -> float:
    return 1200

registry.register_variable(salary)
print(registry["salary"](None))
```

It is useful when the formula engine needs to resolve variable names dynamically from a data model or configuration.

### FormulaCompiler

A `FormulaCompiler` compiles structured expression trees into executable formulas.

This is the on-ramp for the dictionary schema described below.

```python
from pyformula import FormulaCompiler

compiler = FormulaCompiler({
    "price": Formula(lambda item: item["price"]),
    "qty": Formula(lambda item: item["qty"]),
})

expression = {
    "operator": "multiply",
    "expressions": ["price", "qty"],
}

formula = compiler.compile(expression)
print(formula({"price": 10, "qty": 4}))  # 40
```

---

## Formula dict schema

The most important part of the package is the structured expression schema used by `FormulaCompiler.compile()`.

The schema supports:

1. numeric literals
2. named variables
3. binary arithmetic expressions
4. unary wrapper expressions
5. nested expressions

### 1) Numeric literal

```python
42
3.14
```

A plain number is treated as a constant expression.

### 2) Named variable

```python
"salary"
```

This looks up the variable name in the compiler registry.

### 3) Binary operation expression

```python
{
    "operator": "add",
    "expressions": ["salary", 1000],
}
```

Supported operators are:

- `add`
- `subtract`
- `multiply`
- `divide`
- `modulo`
- `power`
- `floor_divide`

Example:

```python
{
    "operator": "divide",
    "expressions": [
        {
            "operator": "add",
            "expressions": ["salary", "bonus"],
        },
        2,
    ],
}
```

This produces:

```python
(salary + bonus) / 2
```

### 4) Unary wrapper expressions

The compiler supports wrappers such as:

```python
{"positive": expression}
{"negative": expression}
{"absolute": expression}
{"round": expression, "ndigits": 2}
```

The math wrappers use the same pattern as the other unary wrappers: the wrapper name is the key, and the inner value is the expression to evaluate.

```python
{"ceil": expression}
{"floor": expression}
{"trunc": expression}
{"sqrt": expression}
{"cbrt": expression}
{"exp": expression}
{"exp2": expression}
{"expm1": expression}
{"log10": expression}
{"log1p": expression}
{"log2": expression}
{"sin": expression}
{"sinh": expression}
{"asin": expression}
{"asinh": expression}
{"cos": expression}
{"cosh": expression}
{"acos": expression}
{"acosh": expression}
{"tan": expression}
{"tanh": expression}
{"atan": expression}
{"atanh": expression}
{"degrees": expression}
{"radians": expression}
{"erf": expression}
{"erfc": expression}
{"gamma": expression}
{"lgamma": expression}
{"fabs": expression}
{"ulp": expression}
```

### Full wrapper reference

#### Rounding

- `ceil`: applies `math.ceil(...)`
- `floor`: applies `math.floor(...)`
- `trunc`: applies `math.trunc(...)`

```python
{"ceil": {"operator": "divide", "expressions": ["salary", 4]}}
{"floor": "hours_worked"}
{"trunc": {"negative": "rate"}}
```

#### Roots and powers

- `sqrt`: applies `math.sqrt(...)`
- `cbrt`: applies `math.cbrt(...)`

```python
{"sqrt": {"operator": "add", "expressions": ["width", "height"]}}
{"cbrt": {"operator": "power", "expressions": ["volume", 3]}}
```

#### Exponential and logarithmic functions

- `exp`: applies `math.exp(...)`
- `exp2`: applies `math.exp2(...)`
- `expm1`: applies `math.expm1(...)`
- `log10`: applies `math.log10(...)`
- `log1p`: applies `math.log1p(...)`
- `log2`: applies `math.log2(...)`

```python
{"exp": "rate"}
{"log10": {"operator": "multiply", "expressions": ["base", 10]}}
{"log1p": {"operator": "divide", "expressions": ["bonus", "salary"]}}
```

#### Trigonometry

- `sin`, `sinh`, `asin`, `asinh`
- `cos`, `cosh`, `acos`, `acosh`
- `tan`, `tanh`, `atan`, `atanh`

```python
{"sin": "angle_radians"}
{"cos": {"degrees": "angle_degrees"}}
{"atan": {"operator": "divide", "expressions": ["y", "x"]}}
```

#### Angular conversion

- `degrees`: converts radians to degrees with `math.degrees(...)`
- `radians`: converts degrees to radians with `math.radians(...)`

```python
{"degrees": "angle_in_radians"}
{"radians": "angle_in_degrees"}
```

#### Special functions

- `erf`: `math.erf(...)`
- `erfc`: `math.erfc(...)`
- `gamma`: `math.gamma(...)`
- `lgamma`: `math.lgamma(...)`

```python
{"gamma": {"operator": "add", "expressions": ["n", 1]}}
{"lgamma": "score"}
```

#### Absolute value and floating-point helpers

- `fabs`: `math.fabs(...)`
- `ulp`: `math.ulp(...)`

```python
{"fabs": {"negative": "margin"}}
{"ulp": "threshold"}
```

### Round wrapper form

`round` is a special unary wrapper because it also needs `ndigits`.

```python
{
    "round": {
        "operator": "divide",
        "expressions": [
            {
                "operator": "add",
                "expressions": ["salary", "bonus"],
            },
            3,
        ],
    },
    "ndigits": 2,
}
```

This is equivalent to:

```python
round((salary + bonus) / 3, 2)
```

### Example: nested wrapper use

```python
expression = {
    "sqrt": {
        "operator": "add",
        "expressions": [
            {"operator": "power", "expressions": ["width", 2]},
            {"operator": "power", "expressions": ["height", 2]},
        ],
    }
}
```

This is equivalent to:

```python
math.sqrt(width**2 + height**2)
```

### Example: full rule payload using wrappers

```python
expression = {
    "operator": "multiply",
    "expressions": [
        {"sqrt": {"operator": "add", "expressions": ["x", "y"]}},
        {"log10": {"operator": "add", "expressions": ["value", 1]}},
    ],
}
```

This is equivalent to:

```python
sqrt(x + y) * log10(value + 1)
```

### 5) Full nested expression trees

The schema is recursive, so you can build deeply nested formulas.

```python
expression = {
    "operator": "multiply",
    "expressions": [
        2,
        {
            "operator": "add",
            "expressions": [
                "width",
                "height",
            ],
        },
    ],
}
```

This evaluates to:

```python
2 * (width + height)
```

### 6) Validation rules

The compiler is intentionally strict:

- missing formula names raise `FormulaNotFoundError`
- invalid expression shapes raise `InvalidExpressionError`
- empty expression lists are rejected
- `round` requires an integer `ndigits`

This is helpful when formulas come from untrusted configuration or user input.

---

## Example: payroll and compensation policies

This is a natural domain for pyformula because compensation rules are often a combination of:

- base pay
- overtime
- bonuses
- taxes
- deductions
- thresholds
- role-based adjustments

```python
from dataclasses import dataclass

from pyformula import FormulaCompiler, VariablesRegistry


@dataclass
class Employee:
    salary: float
    hours_worked: float
    bonus: float
    tax_rate: float


registry = VariablesRegistry[Employee]()
registry.register_variable(lambda e: e.salary, name="salary")
registry.register_variable(lambda e: e.hours_worked, name="hours_worked")
registry.register_variable(lambda e: e.bonus, name="bonus")
registry.register_variable(lambda e: e.tax_rate, name="tax_rate")

compiler = FormulaCompiler(registry.variables)

expression = {
    "operator": "subtract",
    "expressions": [
        {
            "operator": "add",
            "expressions": ["salary", "bonus"],
        },
        {
            "operator": "multiply",
            "expressions": [
                {
                    "operator": "add",
                    "expressions": ["salary", "bonus"],
                },
                "tax_rate",
            ],
        },
    ],
}

net_pay = compiler.compile(expression)
emp = Employee(3000, 40, 200, 0.2)
print(net_pay(emp))  # 2560.0
```

This pattern scales well when you have a catalog of formulas in a registry and select which ones to apply based on role, contract type, or employee segment.

---

## Example: using with `pyspecification`

The project includes a script in `scripts/with_pyspecification.py` that demonstrates an even more powerful pattern: use `Formula` objects together with `pyspecification` predicates to build a rule-based evaluator.

That script defines a dataclass like `Employee`, then builds predicates such as:

- `is_administrator()`
- `is_fulltime()`
- `salary > 0`
- `name__icontains(...)`

Then it combines those predicates and formulas in a guard-based condition engine:

```python
from dataclasses import dataclass
from pyformula import variable
from pyformula.formula import Formula
from pyspecification import Predicate, object_rule


@dataclass
class Guard:
    rule: Predicate[Employee, bool]
    formula: Formula[Employee]


@dataclass
class Condition:
    guards: list[Guard]
    fallback: Formula[Employee]

    def evaluate(self, employee: Employee) -> float:
        for guard in self.guards:
            if guard.rule(employee):
                return float(guard.formula(employee))
        return float(self.fallback(employee))
```

Then the actual logic becomes:

```python
reward = Condition(
    [
        Guard(is_administrator() & is_fulltime(), salary * 0.25),
        Guard(is_teacher() & is_fulltime(), salary * 0.5),
        Guard(is_teacher() & is_parttime(), salary * 0.15),
    ],
    salary / 0.1,
)
```

This is the key idea:

- `pyspecification` tells you whether a rule applies
- `pyformula` computes the numeric result when the rule matches

The combination is excellent for:

- compensation policy engines
- credit eligibility scoring
- insurance pricing by segment
- pricing adjustments by contract or customer class
- decision logic that needs both a boolean gate and a numeric output

This is one of the strongest real-world patterns in the package.

---

## Use cases beyond the examples

The examples in the repository show arithmetic and reward calculations, but the package can be used in many more problem domains.

### 1) Pricing and discount policy engines

Instead of writing inline if/else logic, you can make formulas explicit:

- base price
- loyalty discount
- shipping surcharge
- taxes
- volume-based discounts
- seasonal multipliers

```python
price = Formula[Order](lambda o: o.subtotal)
loyalty = Formula[Order](lambda o: o.loyalty_discount)
shipping = Formula[Order](lambda o: o.shipping)

final_total = (price - loyalty) + shipping
```

### 2) Risk and scoring systems

For a fraud-risk or business-risk model, formulas can represent weighted features or policy thresholds.

- exposure amount
- transaction velocity
- customer age
- outstanding amount
- default probability

These can be composed into a score or a final risk-adjusted amount.

### 3) Operational planning

An object representing a warehouse, machine, or service can expose formulas such as:

- utilization
- capacity utilization
- run-time cost
- maintenance interval
- labor hours
- defect rate adjusted cost

This is especially useful when you want to calculate KPIs from domain objects without embedding the math in the object itself.

### 4) Scientific and engineering calculations

The library supports a wide math wrapper set, so it is useful for parameterized engineering formulas such as:

- energy calculations
- signal processing formulas
- vehicle dynamics
- thermal loads
- financial approximation formulas
- root and logarithmic calculations

### 5) UI and form-based calculators

If your application has dynamic forms or configurable calculations, pyformula can express them as data-driven formulas rather than a batch of custom event handlers.

Examples:

- loan calculator
- margin calculator
- tax estimate estimator
- insurance premium estimator
- medical dosage estimator

### 6) Data pipeline feature computation

If you receive records and need to compute feature values for each row, you can register variables, build formulas, and compile them from dictionaries. That creates a tidy separation between:

- data extraction
- transformation schema
- evaluation logic

### 7) Policy-as-data systems

This is the strongest long-term use case.

Instead of hard-coding a formula implementation in Python, you can define a formula dictionary in config or a database table, then compile it at runtime with a registry of available variables.

This gives you:

- rule versioning
- formula portability
- safer auditing
- easier business-user review

---

## Recommended pattern for production code

When using pyformula in real systems, the cleanest pattern is usually:

1. define a domain model
2. register all relevant variables in a `VariablesRegistry`
3. define formula expressions as either Python `Formula` objects or dictionary trees
4. compile the expression tree with `FormulaCompiler`
5. evaluate against the domain object

For example:

```python
from dataclasses import dataclass

from pyformula import FormulaCompiler, VariablesRegistry


@dataclass
class Invoice:
    subtotal: float
    discount_pct: float
    tax_pct: float
    shipping: float


registry = VariablesRegistry[Invoice]()
registry.register_variable(lambda i: i.subtotal, name="subtotal")
registry.register_variable(lambda i: i.discount_pct, name="discount_pct")
registry.register_variable(lambda i: i.tax_pct, name="tax_pct")
registry.register_variable(lambda i: i.shipping, name="shipping")

compiler = FormulaCompiler(registry.variables)

net_total = compiler.compile({
    "operator": "add",
    "expressions": [
        {
            "operator": "subtract",
            "expressions": [
                "subtotal",
                {
                    "operator": "multiply",
                    "expressions": ["subtotal", "discount_pct"],
                },
            ],
        },
        {
            "operator": "multiply",
            "expressions": [
                {
                    "operator": "subtract",
                    "expressions": [
                        "subtotal",
                        {
                            "operator": "multiply",
                            "expressions": ["subtotal", "discount_pct"],
                        },
                    ],
                },
                "tax_pct",
            ],
        },
        "shipping",
    ],
})

invoice = Invoice(100, 0.1, 0.2, 10)
print(net_total(invoice))
```

This avoids hard-coded logic and turns business rules into a transparent, inspectable expression tree.

---

## Error handling overview

The library raises explicit exceptions for common configuration mistakes:

- `FormulaNotFoundError`: a referenced variable name does not exist in the registry
- `InvalidExpressionError`: the expression shape is malformed or unsupported
- `FormulaAlreadyRegisteredError`: duplicate variable registration name
- `FormulaNotRegisteredError`: name is registered but hidden or unavailable

Examples:

```python
from pyformula import FormulaCompiler
from pyformula.exceptions import FormulaNotFoundError

compiler = FormulaCompiler({})

try:
    compiler.compile("missing_variable")
except FormulaNotFoundError:
    print("That variable is not registered")
```

---

## Library surface

The top-level package exposes:

```python
from pyformula import Formula, FormulaCompiler, VariablesRegistry, variable
```

And the main submodules are:

- `pyformula.formula` — core `Formula` implementation
- `pyformula.variable` — decorator for named formulas
- `pyformula.registry` — registry for named variables
- `pyformula.compiler` — expression-tree compilation logic
- `pyformula.math` — wrapper math functions for formulas
- `pyformula.models` — numeric and operator type aliases
- `pyformula.exceptions` — library-specific errors

---

## Summary

pyformula is best thought of as a small expression system for domain objects.

It gives you three core capabilities:

- build formulas from object accessors
- compose formulas with arithmetic and math wrappers
- compile nested expression dictionaries into runtime formulas

That makes it particularly powerful when formulas are part of business logic, policy decisions, or configurable calculations rather than just ad hoc arithmetic.

If you want a calculation model that is:

- readable
- declarative
- composable
- inspectable
- and easy to version or parameterize

then pyformula is a good fit.

---

## Full example from the repository

The repository’s `scripts/with_pyspecification.py` is an excellent demonstration of the library’s real-world pattern: boolean rule predicates choose which numeric formula to run.

That file is the best example of building a policy engine where rule selection and numeric calculation are separated cleanly.

In other words:

- `pyspecification` decides whether the rule applies
- `pyformula` computes the value

This pairing is especially useful when the final output is numeric but the decision logic itself is rule-driven.
