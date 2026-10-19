from pydantic import BaseModel, ConfigDict


class Unit:
    def __init__(self, symbol):
        self.symbol = symbol


class Reading(BaseModel):
    model_config = ConfigDict(ignored_types=(Unit,))

    value: float
    unit = Unit("m")


def make_reading(value):
    return Reading(value=value)
