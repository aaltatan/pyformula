# PHASES

## Round 1 — Agreed in the package-family review
- [x] `PyformulaError` base class for all four exceptions
- [x] `FormulaNotFoundError` lists available formulas
- [x] Compiled literals show their value in `repr` instead of `anonymous`
- [x] Keyword-only `literal=` hook on `FormulaCompiler`, plus `decimal_literal` (branch `fix/errors-and-literals`, 1038 tests)
- [x] Open a PR for the branch. Merged into `main` locally for review instead of PRs; pyvocabulary 0.1.0 now comes from PyPI (2026-11-08)

## Next
- [x] Adopt pyvocabulary (branch `refactor/pyvocabulary`, on top of `fix/errors-and-literals`, 1046 tests). Hidden variables leave `registry.variables`; names must be identifiers; 0.2.0
- [x] JSON-path notes on compiler errors via `pyvocabulary.located` (`at $.expressions[1].sqrt`)
- [ ] Clean up the 4 pre-existing `mypy --strict` findings in `compiler.py` and `registry.py`
- [ ] Clean up the 20 pre-existing ruff findings
