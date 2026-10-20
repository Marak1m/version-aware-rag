from pydantic import BaseModel, constr


class Plate(BaseModel):
    number: constr(regex=r"^[A-Z]{2}-\d{3}$")


def make_plate(number):
    return Plate(number=number)
