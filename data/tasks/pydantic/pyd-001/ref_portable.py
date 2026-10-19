import pydantic
from pydantic import BaseModel, Field

PATTERN = r"^[A-Z]{3}-\d{4}$"

if pydantic.VERSION.startswith("1."):
    class Sku(BaseModel):
        code: str = Field(..., regex=PATTERN)
else:
    class Sku(BaseModel):
        code: str = Field(..., pattern=PATTERN)


def make_sku(code: str):
    return Sku(code=code)
