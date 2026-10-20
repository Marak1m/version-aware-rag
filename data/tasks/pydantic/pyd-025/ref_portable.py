import pydantic
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float


def product_schema():
    if pydantic.VERSION.startswith("1."):
        return Product.schema()
    return Product.model_json_schema()
