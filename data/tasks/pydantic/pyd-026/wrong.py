import json

from pydantic import BaseModel


class Order(BaseModel):
    id: int
    paid: bool


def order_schema_text():
    return json.dumps(Order.model_json_schema())
