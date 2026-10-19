from pydantic import BaseModel, Field


class Point(BaseModel):
    x: int = Field(..., allow_mutation=False)


def make_point(x):
    return Point(x=x)
