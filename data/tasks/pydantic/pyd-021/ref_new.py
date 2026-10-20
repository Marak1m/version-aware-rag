from pydantic import BaseModel


class Order(BaseModel):
    id: int
    items: list[str]


def parse_order(raw):
    return Order.model_validate_json(raw)
