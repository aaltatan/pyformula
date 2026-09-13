from collections.abc import Callable
from functools import wraps

from .formula import Formula
from .models import NumberType


def variable[T](fn: Callable[[T], NumberType]) -> Formula[T]:
    @wraps(fn)
    def wrapper(fn: Callable[[T], NumberType]) -> Callable[[T], NumberType]:
        return fn

    return Formula(wrapper(fn))
