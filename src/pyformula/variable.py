from collections.abc import Callable
from functools import wraps

from .formula import Formula
from .models import Number


def variable[T](*, name: str | None = None) -> Callable[[Callable[[T], Number]], Formula[T]]:
    def decorator(fn: Callable[[T], Number]) -> Formula[T]:
        @wraps(fn)
        def wrapper(fn: Callable[[T], Number]) -> Callable[[T], Number]:
            return fn

        return Formula(wrapper(fn), name=name or fn.__name__)

    return decorator
