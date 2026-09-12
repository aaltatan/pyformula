from collections.abc import Callable
from decimal import Decimal
from functools import wraps

from .formula import Formula


def variable[T](fn: Callable[[T], Decimal]) -> Formula[T]:
    @wraps(fn)
    def wrapper(fn: Callable[[T], Decimal]) -> Callable[[T], Decimal]:
        return fn

    return Formula(wrapper(fn))
