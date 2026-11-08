# PHASES

## Round 1 — Agreed in the package-family review
- [x] `PyformulaError` base class for all four exceptions
- [x] `FormulaNotFoundError` lists available formulas
- [x] Compiled literals show their value in `repr` instead of `anonymous`
- [x] Keyword-only `literal=` hook on `FormulaCompiler`, plus `decimal_literal` (branch `fix/errors-and-literals`, 1038 tests)
- [ ] Open a PR for the branch

## Next
- [ ] Decide whether pyformula adopts pyvocabulary (it would add the pyargprocessors dependency)
- [ ] JSON-path notes on compiler errors, like pyspecification and pyflowstep
- [ ] Clean up the 4 pre-existing `mypy --strict` findings in `compiler.py` and `registry.py`
- [ ] Clean up the 20 pre-existing ruff findings
