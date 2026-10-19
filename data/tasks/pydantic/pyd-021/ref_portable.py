from pydantic import BaseModel, Json


class Order(BaseModel):
    id: int
    items: list[str]


class _Raw(BaseModel):
    order: Json[Order]


def parse_order(raw):
    return _Raw(order=raw).order
