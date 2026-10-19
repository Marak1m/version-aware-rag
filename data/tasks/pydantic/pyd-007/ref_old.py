from pydantic import BaseModel, Field


class Point(BaseModel):
    x: int = Field(..., allow_mutation=False)

    class Config:
        validate_assignment = True


def make_point(x):
    return Point(x=x)
