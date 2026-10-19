from pydantic import BaseModel, Field


class Sku(BaseModel):
    code: str = Field(..., min_length=8, max_length=8)


def make_sku(code: str):
    return Sku(code=code)
