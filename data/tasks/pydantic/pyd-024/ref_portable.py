import pydantic
from pydantic import BaseModel


class Point(BaseModel):
    x: int
    y: int


def trusted_point(x, y):
    if pydantic.VERSION.startswith("1."):
        return Point.construct(x=x, y=y)
    return Point.model_construct(x=x, y=y)
