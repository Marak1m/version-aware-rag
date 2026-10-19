from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str = Field(..., example="pen")
    price: float = Field(..., example=1.5)


def product_schema():
    schema = getattr(Product, "model_json_schema", None) or Product.schema
    return schema()
