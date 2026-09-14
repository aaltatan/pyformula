from collections.abc import Callable
from functools import wraps

from .formula import Formula
from .models import NumberType


def variable[T](*, name: str | None = None) -> Callable[[Callable[[T], NumberType]], Formula[T]]:
    def decorator(fn: Callable[[T], NumberType]) -> Formula[T]:
        @wraps(fn)
        def wrapper(fn: Callable[[T], NumberType]) -> Callable[[T], NumberType]:
            return fn

        return Formula(wrapper(fn), name=name or fn.__name__)

    return decorator
