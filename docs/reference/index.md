# Reference

- [API](api.md): every public name of `pyformula` and `pyformula.math`.
- [Expression format](expressions.md): every JSON shape, operator and function.
- [Exceptions](exceptions.md): the exception hierarchy and when each one is raised.

Everything in the API page is importable from the package root, except the math functions,
which live in `pyformula.math`:

```python
import pyformula

assert sorted(pyformula.__all__) == [
    "Expression",
    "FUNCTIONS",
    "Formula",
    "FormulaAlreadyRegisteredError",
    "FormulaCompiler",
    "FormulaNotFoundError",
    "FormulaNotRegisteredError",
    "InvalidExpressionError",
    "InvalidFormulaNameError",
    "LiteralFn",
    "Number",
    "Operator",
    "OperatorFn",
    "PyformulaError",
    "VariablesRegistry",
    "decimal_literal",
    "get_formula_json_schema",
    "variable",
]
```
