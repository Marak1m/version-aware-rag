import pydantic
from pydantic import BaseModel

EXAMPLES = {"examples": [{"name": "pen", "price": 1.5}]}

if pydantic.VERSION.startswith("1."):
    class Product(BaseModel):
        name: str
        price: float

        class Config:
            schema_extra = EXAMPLES

    def product_schema():
        return Product.schema()
else:
    class Product(BaseModel):
        model_config = {"json_schema_extra": EXAMPLES}

        name: str
        price: float

    def product_schema():
        return Product.model_json_schema()
