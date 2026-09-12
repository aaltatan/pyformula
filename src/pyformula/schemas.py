from decimal import Decimal  # noqa: TC003
from typing import Any, Self

from pydantic import RootModel, model_serializer, model_validator

from .models import Operator


class SimpleFormulaSchema(RootModel[dict[Operator, list["SimpleFormulaSchema | Decimal | str"]]]):
    @property
    def operator(self) -> Operator:
        return next(iter(self.root.keys()))

    @property
    def expressions(self) -> list["SimpleFormulaSchema | Decimal | str"]:
        return self.root[self.operator]

    @model_serializer()
    def serialize(self) -> dict[str, Any]:
        return {"operator": self.operator, "expressions": self.expressions}

    @model_validator(mode="after")
    def validate_single_key(self) -> Self:
        if len(self.root.keys()) != 1:
            msg = "SimpleFormulaSchema must have exactly one root operator key."
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_expressions(self) -> Self:
        if len(self.expressions) == 0:
            msg = "SimpleFormulaSchema expressions must not be empty."
            raise ValueError(msg)
        return self


SimpleFormulaSchema.model_rebuild()
