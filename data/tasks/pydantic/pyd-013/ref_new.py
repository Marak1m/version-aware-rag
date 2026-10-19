from pydantic import BaseModel, ConfigDict


class Product(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"name": "pen", "price": 1.5}]})

    name: str
    price: float


def product_schema():
    return Product.model_json_schema()
