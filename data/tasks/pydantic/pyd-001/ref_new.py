from pydantic import BaseModel, Field


class Sku(BaseModel):
    code: str = Field(..., pattern=r"^[A-Z]{3}-\d{4}$")


def make_sku(code: str):
    return Sku(code=code)
