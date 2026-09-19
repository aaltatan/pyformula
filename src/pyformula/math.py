from collections.abc import Callable

from .formula import Formula


def wrap[T](
    formula: Formula[T],
    /,
    *,
    math_fn: Callable[[float], float],
    name: str | None = None,
) -> Formula[T]:
    return Formula(
        lambda obj: math_fn(float(formula(obj))),
        name=f"{name or math_fn.__name__}({formula})",
    )
