# Exceptions

```text
Exception
└── PyformulaError
    ├── FormulaAlreadyRegisteredError
    ├── FormulaNotRegisteredError
    ├── FormulaNotFoundError
    ├── InvalidFormulaNameError          (also a ValueError)
    └── InvalidExpressionError
```

Every exception raised by pyformula derives from `PyformulaError`, so one `except` clause
catches them all:

```python
from pyformula import (
    FormulaAlreadyRegisteredError,
    FormulaNotFoundError,
    FormulaNotRegisteredError,
    InvalidExpressionError,
    InvalidFormulaNameError,
    PyformulaError,
)

for error_type in (
    FormulaAlreadyRegisteredError,
    FormulaNotFoundError,
    FormulaNotRegisteredError,
    InvalidExpressionError,
    InvalidFormulaNameError,
):
    assert issubclass(error_type, PyformulaError)

assert issubclass(InvalidFormulaNameError, ValueError)
```

## When each one is raised

| Exception | Raised by | Example message |
| --- | --- | --- |
| `FormulaAlreadyRegisteredError` | registering a taken name (hidden ones included) | `Formula already registered: salary` |
| `FormulaNotRegisteredError` | `registry[name]` for an unknown or hidden name | `Formula not registered: salry` |
| `FormulaNotFoundError` | `compile` with an unknown variable | `Formula not found: salry. Available formulas: salary, bonus` |
| `InvalidFormulaNameError` | registering a name that is not an ASCII identifier, or an unnamed lambda | `Invalid formula name: 'net-pay', name must start with a letter or underscore and can only contain letters, numbers and underscores` |
| `InvalidExpressionError` | `compile` with a malformed expression | `Invalid expression: {'operator': 'add', 'expressions': []}` |

Other errors you may see:

| Error | When |
| --- | --- |
| `ValueError` | `get_formula_json_schema` with an unknown operator, function or labelled variable; a math function outside its domain (`math domain error`) |
| `ZeroDivisionError`, `decimal.DivisionByZero`, `decimal.InvalidOperation` | dividing by zero while evaluating |
| `TypeError` | a result would be a complex number, such as `(-4) ** 0.5` |

## JSON-path notes

Every `PyformulaError` raised while compiling a nested part gets an
[exception note](https://docs.python.org/3/library/exceptions.html#BaseException.add_note)
with the path of that part, such as `at $.expressions[1].sqrt`. Read it from
`error.__notes__`. Errors for the root expression itself have no note.

## Programming errors vs user errors

When formulas come from users, `FormulaNotFoundError` and `InvalidExpressionError` are
**their** mistakes: catch them while compiling and show the message with its path.
Registration errors (`FormulaAlreadyRegisteredError`, `InvalidFormulaNameError`) are
**yours**, raised when your module is imported, and should crash loudly in development.
