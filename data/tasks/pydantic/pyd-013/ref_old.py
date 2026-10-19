from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float

    class Config:
        schema_extra = {"examples": [{"name": "pen", "price": 1.5}]}


def product_schema():
    return Product.schema()
