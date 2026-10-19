from pydantic import BaseModel, Field


class Cart(BaseModel):
    items: list[str] = Field(..., min_length=2)


def make_cart(items):
    return Cart(items=items)
