from pydantic import BaseModel


class Unit:
    def __init__(self, symbol):
        self.symbol = symbol


class Reading(BaseModel):
    value: float
    unit = Unit("m")

    class Config:
        keep_untouched = (Unit,)


def make_reading(value):
    return Reading(value=value)
