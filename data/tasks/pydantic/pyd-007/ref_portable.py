import pydantic
from pydantic import BaseModel, Field

if pydantic.VERSION.startswith("1."):
    class Point(BaseModel):
        x: int = Field(..., allow_mutation=False)

        class Config:
            validate_assignment = True
else:
    class Point(BaseModel):
        x: int = Field(..., frozen=True)


def make_point(x):
    return Point(x=x)
