from pydantic import BaseModel, conint


class Order(BaseModel):
    qty: conint(ge=0)


def make_order(qty):
    return Order(qty=qty)
