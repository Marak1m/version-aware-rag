from pydantic import BaseModel, Field


class Point(BaseModel):
    x: int = Field(..., frozen=True)


def make_point(x):
    return Point(x=x)
