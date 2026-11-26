# API

`T` is the type of the object a formula is evaluated against.

## Formulas

### `Formula[T]`

```py
Formula(fn: Callable[[T], Number], *, name: str | None = None)
```

A lazily evaluated numeric function of `T`.

| Member | Description |
| --- | --- |
| `formula(obj) -> Number` | evaluate `fn(obj)` |
| `a + b`, `a - b`, `a * b`, `a / b`, `a // b`, `a % b`, `a ** b` | new formula; either side may be a number |
| `-a`, `+a`, `abs(a)` | new formula |
| `round(a, ndigits=None)` | new formula that rounds, keeping the number type |
| `str(formula)` | its name, e.g. `((price * quantity) + shipping)`; `anonymous` for an unnamed lambda |
| `repr(formula)` | `Formula(<name>)` |

Raises, when called: Python's arithmetic errors (`ZeroDivisionError`,
`decimal.InvalidOperation`...), and `TypeError` when a result would be `complex`.

Guide: [Formulas](../guide/formulas.md), [Numbers](../guide/numbers.md).

### `Number`

```py
Number = Decimal | int | float
```

### `Operator`

```py
Operator = Literal["add", "subtract", "multiply", "divide", "modulo", "power", "floor_divide"]
```

The operator names used in JSON expressions.

### `OperatorFn`

```py
OperatorFn = Callable[[SupportsMathOperator, SupportsMathOperator], SupportsMathOperator]
```

The type of a binary operator implementation; mostly useful in type hints.

## Variables

### `variable`

```py
variable(*, name: str | None = None) -> Callable[[Callable[[T], Number]], Formula[T]]
```

Decorator turning an accessor into a `Formula` named `name` or the function's name. The
function's `__name__`, `__doc__` and `__wrapped__` are kept.

### `VariablesRegistry[T]`

```py
VariablesRegistry[T]()
```

| Member | Description |
| --- | --- |
| `variable(*, name=None, description=None, hidden=False, label=None)` | decorator; registers and returns the formula |
| `register_variable(fn, /, *, name=None, description=None, hidden=False, label=None) -> Formula[T]` | registers a callable or a formula and returns the registered formula |
| `registry[name] -> Formula[T]` | `FormulaNotRegisteredError` if unknown or hidden |
| `variables -> Mapping[str, Formula[T]]` | read-only live view of the visible variables |
| `labels -> dict[str, Text]` | labels of the visible variables that have one |

Registration raises `InvalidFormulaNameError` for a name that is not an ASCII identifier
(including an unnamed lambda) and `FormulaAlreadyRegisteredError` for a taken name,
hidden ones included.

`Text` is pyvocabulary's label type: a `str`, or a `dict[str, str]` of language code to
text.

Guide: [Variables and registries](../guide/variables.md).

## Compiler

### `FormulaCompiler[T]`

```py
FormulaCompiler(fns: Mapping[str, Formula[T]], /, *, literal: LiteralFn | None = None)
```

| Member | Description |
| --- | --- |
| `compile(expression: Expression) -> Formula[T]` | build the formula; errors carry a JSON-path note such as `at $.expressions[1].sqrt` |

Raises `FormulaNotFoundError` for an unknown variable and `InvalidExpressionError` for a
malformed expression.

### `Expression`

```py
Expression = FormulaDict | WrapperDict | str | Number
```

The type of a JSON expression; see [Expression format](expressions.md).

### `LiteralFn`

```py
type LiteralFn = Callable[[Number], Any]
```

### `decimal_literal`

```py
decimal_literal(number: Number, /) -> Decimal
```

Converts a number to `Decimal` through `str`, so `0.8` stays `0.8`. A `Decimal` is
returned unchanged.

Guide: [Compiling formulas from JSON](../guide/compiling.md).

## JSON Schema

### `get_formula_json_schema`

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

The draft 2020-12 schema of the expressions over `variables`. Raises `ValueError` for an
unknown operator or function, or a label of an unknown variable.

### `FUNCTIONS`

```py
FUNCTIONS: tuple[str, ...]
```

Every function name an expression may use: `round` and the
[function wrappers](expressions.md#functions).

Guide: [JSON Schema](../guide/json-schema.md).

## `pyformula.math`

Each function takes a `Formula[T]` (positional-only) and returns a `Formula[T]` named
`fn(inner)`, which converts the value to `float` and applies the `math` function of the
same name:

`ceil`, `floor`, `trunc`, `sqrt`, `cbrt`, `exp`, `exp2`, `expm1`, `log10`, `log1p`,
`log2`, `sin`, `sinh`, `asin`, `asinh`, `cos`, `cosh`, `acos`, `acosh`, `tan`, `tanh`,
`atan`, `atanh`, `degrees`, `radians`, `erf`, `erfc`, `gamma`, `lgamma`, `fabs`, `ulp`.

Guide: [Math functions](../guide/math.md).

## Exceptions

See [Exceptions](exceptions.md).
