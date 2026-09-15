from collections.abc import Callable
from typing import Any, TypeAlias, TypeGuard

from .models import (
    AbsWrapperDict,
    CeilWrapperDict,
    FloorWrapperDict,
    FormulaDict,
    NegativeWrapperDict,
    PositiveWrapperDict,
    RoundWrapperDict,
    TruncWrapperDict,
)

CheckerFn: TypeAlias = Callable[[object], bool]
CheckerApplier: TypeAlias = Callable[[Any], Any]


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return _is_typed_dict(obj, "operator", "expression")


def is_positive_wrapper_dict(obj: object) -> TypeGuard[PositiveWrapperDict]:
    return _is_typed_dict(obj, "positive")


def is_negative_wrapper_dict(obj: object) -> TypeGuard[NegativeWrapperDict]:
    return _is_typed_dict(obj, "negative")


def is_absolute_wrapper_dict(obj: object) -> TypeGuard[AbsWrapperDict]:
    return _is_typed_dict(obj, "absolute")


def is_floor_wrapper_dict(obj: object) -> TypeGuard[FloorWrapperDict]:
    return _is_typed_dict(obj, "floor")


def is_ceil_wrapper_dict(obj: object) -> TypeGuard[CeilWrapperDict]:
    return _is_typed_dict(obj, "ceil")


def is_trunc_wrapper_dict(obj: object) -> TypeGuard[TruncWrapperDict]:
    return _is_typed_dict(obj, "trunc")


def is_round_wrapper_dict(obj: object) -> TypeGuard[RoundWrapperDict]:
    return _is_typed_dict(obj, "round", "ndigits")


def _is_typed_dict(obj: object, *keys: str) -> bool:
    return (
        isinstance(obj, dict) and all(key in obj for key in keys) and len(obj.keys()) == len(keys)
    )
