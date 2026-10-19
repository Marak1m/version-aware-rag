import json

import pydantic
from pydantic import BaseModel


class Order(BaseModel):
    id: int
    paid: bool


def order_schema_text():
    if pydantic.VERSION.startswith("1."):
        return Order.schema_json(indent=2)
    return json.dumps(Order.model_json_schema(), indent=2)
