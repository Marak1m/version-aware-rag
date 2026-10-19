from pydantic import BaseModel


class Point(BaseModel):
    x: int
    y: int


def trusted_point(x, y):
    return Point.model_construct(x=x, y=y)
