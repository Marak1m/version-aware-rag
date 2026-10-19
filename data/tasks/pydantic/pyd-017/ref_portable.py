import pydantic
from pydantic import BaseModel, constr

PATTERN = r"^[A-Z]{2}-\d{3}$"

if pydantic.VERSION.startswith("1."):
    PlateNumber = constr(regex=PATTERN)
else:
    PlateNumber = constr(pattern=PATTERN)


class Plate(BaseModel):
    number: PlateNumber


def make_plate(number):
    return Plate(number=number)
