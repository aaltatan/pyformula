# Expression format

This is the JSON a [`FormulaCompiler`](../guide/compiling.md) accepts. An expression is
one of five shapes; every place that takes an expression accepts any of them, so they
nest freely.

## Number

```json
0.15
```

Any JSON number, except booleans (`true`/`false` are rejected). It becomes a constant
formula named after its value, after the compiler's [`literal`](../guide/compiling.md#literals)
conversion.

## Variable

```json
"salary"
```

A name from the compiler's variables. Unknown names raise `FormulaNotFoundError`, which
lists the available ones.

## Operation

```json
{"operator": "add", "expressions": ["salary", "bonus", 100]}
```

Exactly the keys `operator` and `expressions`. `expressions` is a non-empty list, folded
from the left: `[a, b, c]` is `(a op b) op c`. A single expression is returned as it is.

| `operator` | Python |
| --- | --- |
| `add` | `+` |
| `subtract` | `-` |
| `multiply` | `*` |
| `divide` | `/` |
| `floor_divide` | `//` |
| `modulo` | `%` |
| `power` | `**` |

## Round

```json
{"round": {"operator": "divide", "expressions": ["total", 3]}, "ndigits": 2}
```

Exactly the keys `round` and `ndigits`; `ndigits` must be an integer (negative rounds to
tens, hundreds...). Same behaviour as Python's `round()`: half-to-even, keeps the number
type. See [Rounding](../guide/numbers.md#rounding).

## Functions

```json
{"sqrt": {"operator": "add", "expressions": [{"operator": "power", "expressions": ["width", 2]}, {"operator": "power", "expressions": ["height", 2]}]}}
```

A single key naming the function, whose value is the argument expression.

| Key | Meaning | Returns |
| --- | --- | --- |
| `positive` | `+x` | same type |
| `negative` | `-x` | same type |
| `absolute` | `abs(x)` | same type |
| `ceil`, `floor`, `trunc` | rounding up, down, toward zero | `int` |
| `sqrt`, `cbrt` | square and cube root | `float` |
| `exp`, `exp2`, `expm1` | `e**x`, `2**x`, `e**x - 1` | `float` |
| `log10`, `log2`, `log1p` | base-10 and base-2 logarithm, `ln(1 + x)` | `float` |
| `sin`, `cos`, `tan` | trigonometry, in radians | `float` |
| `asin`, `acos`, `atan` | inverse trigonometry, in radians | `float` |
| `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` | hyperbolic functions | `float` |
| `degrees`, `radians` | angle conversion | `float` |
| `erf`, `erfc` | error function and its complement | `float` |
| `gamma`, `lgamma` | gamma function and its natural logarithm | `float` |
| `fabs` | absolute value as `float` | `float` |
| `ulp` | the value of the least significant bit | `float` |

Every function except `positive`, `negative` and `absolute` converts its argument to
`float` first, see [Math functions](../guide/math.md#what-the-functions-return).

## A complete example

The net pay of an employee, `round((salary + bonus) * (1 - tax_rate), 2)`:

```python
from pyformula import Formula, FormulaCompiler

variables = {
    name: Formula(lambda e, name=name: e[name], name=name)
    for name in ("salary", "bonus", "tax_rate")
}

net_pay = FormulaCompiler(variables).compile(
    {
        "round": {
            "operator": "multiply",
            "expressions": [
                {"operator": "add", "expressions": ["salary", "bonus"]},
                {"operator": "subtract", "expressions": [1, "tax_rate"]},
            ],
        },
        "ndigits": 2,
    }
)

assert str(net_pay) == "round(((salary + bonus) * (1 - tax_rate)), 2)"
assert net_pay({"salary": 3000, "bonus": 200, "tax_rate": 0.2}) == 2560.0
```

## Rules of the format

- Dictionaries must have **exactly** the keys of their shape. `{"sqrt": "a", "note": "x"}`
  is invalid.
- Anything else (a list, `null`, a boolean, a string that is not a variable) is invalid.
- Errors carry a note with the path of the offending part, such as
  `at $.round.expressions[1]`.
- The [JSON Schema](../guide/json-schema.md) describes the same rules for validators and
  editors.
