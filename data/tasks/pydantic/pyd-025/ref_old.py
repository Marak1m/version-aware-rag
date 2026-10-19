from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float


def product_schema():
    return Product.schema()
