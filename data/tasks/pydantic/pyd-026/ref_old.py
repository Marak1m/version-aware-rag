from pydantic import BaseModel


class Order(BaseModel):
    id: int
    paid: bool


def order_schema_text():
    return Order.schema_json(indent=2)
