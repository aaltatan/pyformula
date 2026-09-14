from decimal import Decimal
from typing import Any

import pytest
from pyformula.models import is_number


@pytest.mark.parametrize(
    "obj, expected_result",
    [
        (1, True),
        (1.0, True),
        (Decimal(1), True),
        ("1", False),
        (True, False),
        (None, False),
        (False, False),
        ([], False),
        ({}, False),
        ((), False),
        (lambda: None, False),
        (object(), False),
    ],
)
def test_is_number(obj: Any, expected_result: bool) -> None:  # noqa: FBT001
    assert is_number(obj) == expected_result
