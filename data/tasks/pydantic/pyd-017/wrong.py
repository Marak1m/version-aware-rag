from pydantic import BaseModel, constr


class Plate(BaseModel):
    number: constr(min_length=6, max_length=6, to_upper=True)


def make_plate(number):
    return Plate(number=number)
