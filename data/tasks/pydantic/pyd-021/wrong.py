import json

from pydantic import BaseModel


class Order(BaseModel):
    id: int
    items: list[str]


def parse_order(raw):
    return Order(**json.loads(raw))
