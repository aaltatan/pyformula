from collections.abc import Callable
from typing import Any, TypeAlias, TypeGuard

from .models import (
    AbsWrapperDict,
    CeilWrapperDict,
    FloorWrapperDict,
    FormulaDict,
    NegativeWrapperDict,
    PositiveWrapperDict,
    TruncWrapperDict,
)

CheckerFn: TypeAlias = Callable[[object], bool]
CheckerApplier: TypeAlias = Callable[[Any], Any]


def is_formula_dict(obj: object) -> TypeGuard[FormulaDict]:
    return (
        isinstance(obj, dict)
        and "operator" in obj
        and "expressions" in obj
        and len(obj.keys()) == 2
    )


def is_positive_wrapper_dict(obj: object) -> TypeGuard[PositiveWrapperDict]:
    return _is_wrapped_dict(obj, "positive")


def is_negative_wrapper_dict(obj: object) -> TypeGuard[NegativeWrapperDict]:
    return _is_wrapped_dict(obj, "negative")


def is_absolute_wrapper_dict(obj: object) -> TypeGuard[AbsWrapperDict]:
    return _is_wrapped_dict(obj, "absolute")


def is_floor_wrapper_dict(obj: object) -> TypeGuard[FloorWrapperDict]:
    return _is_wrapped_dict(obj, "floor")


def is_ceil_wrapper_dict(obj: object) -> TypeGuard[CeilWrapperDict]:
    return _is_wrapped_dict(obj, "ceil")


def is_trunc_wrapper_dict(obj: object) -> TypeGuard[TruncWrapperDict]:
    return _is_wrapped_dict(obj, "trunc")


def _is_wrapped_dict(obj: object, key: str) -> bool:
    return isinstance(obj, dict) and key in obj and len(obj.keys()) == 1
